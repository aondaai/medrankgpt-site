from __future__ import annotations
import re
import unicodedata
import extruct
from bs4 import BeautifulSoup
from visibility.clients import HttpClient
from visibility.collectors.base import CollectorContext, CollectorOutput, SignalResult
from visibility.models import Status

CRM_RE = re.compile(r"\bCRM[\s./-]*[A-Z]{0,2}[\s-]*\d{4,6}\b", re.IGNORECASE)
RQE_RE = re.compile(r"\bRQE[\s.:-]*\d{3,6}\b", re.IGNORECASE)
_MED_TYPES = {"physician", "medicalclinic", "medicalorganization", "dentist", "hospital"}

def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    return s.lower()

class SiteAnalysisCollector:
    category = "site_conteudo"

    def __init__(self, http: HttpClient):
        self.http = http

    def collect(self, ctx: CollectorContext) -> CollectorOutput:
        site = ctx.doctor.site
        if not site:
            return CollectorOutput(signals=[self._unknown(i, l) for i, l in self._labels()])
        try:
            html = self.http.get_text(site)
        except Exception as exc:
            reason = f"Site inacessível: {type(exc).__name__}."
            return CollectorOutput(signals=[
                self._unknown(i, l, reason, reason) for i, l in self._labels()])
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(" ", strip=True)
        data = extruct.extract(html, base_url=site, syntaxes=["json-ld", "microdata"])
        return CollectorOutput(signals=[
            self._crm_rqe(text, site),
            self._schema(data, site),
            self._specialty_page(soup, ctx, site),
            self._procedure_pages(soup, ctx, site),
            self._qa_content(soup, data, site),
        ])

    # --- signals ---
    def _crm_rqe(self, text: str, url: str) -> SignalResult:
        has_crm = bool(CRM_RE.search(text)); has_rqe = bool(RQE_RE.search(text))
        status = Status.pass_ if (has_crm and has_rqe) else Status.partial if has_crm else Status.fail
        return SignalResult("crm_rqe_visivel", "CRM/RQE visível no site", status,
            has_crm, 5, 0.95, "site_scrape",
            [{"fonte": "site", "url": url, "resumo": f"CRM={has_crm} RQE={has_rqe}"}],
            None if has_crm else "Nenhum CRM encontrado no texto do site.")

    def _schema(self, data: dict, url: str) -> SignalResult:
        found = self._schema_types(data)
        has = bool(_MED_TYPES & found)
        return SignalResult("schema_medico", "Tem schema médico (Physician/MedicalClinic)",
            Status.pass_ if has else Status.fail, has, 5, 0.97, "schema_parse",
            [{"fonte": "site", "url": url, "resumo": f"tipos JSON-LD: {sorted(found) or 'nenhum'}"}])

    def _specialty_page(self, soup, ctx, url) -> SignalResult:
        esp = _norm(ctx.doctor.especialidade_principal)
        has = any(esp in _norm(a.get("href", "") + " " + a.get_text(" ")) for a in soup.find_all("a"))
        return SignalResult("pagina_especialidade", "Tem página por especialidade",
            Status.pass_ if has else Status.fail, has, 5, 0.9, "site_scrape",
            [{"fonte": "site", "url": url, "resumo": f"link p/ '{esp}': {has}"}])

    def _procedure_pages(self, soup, ctx, url) -> SignalResult:
        procs = [_norm(p) for p in ctx.doctor.procedimentos_foco]
        haystack = " ".join(_norm(a.get("href", "") + " " + a.get_text(" ")) for a in soup.find_all("a"))
        hits = [p for p in procs if p in haystack]
        if not procs:
            status = Status.unknown
        elif len(hits) == len(procs):
            status = Status.pass_
        elif hits:
            status = Status.partial
        else:
            status = Status.fail
        return SignalResult("pagina_procedimento", "Tem página por procedimento", status,
            len(hits), 5, 0.85, "site_scrape",
            [{"fonte": "site", "url": url, "resumo": f"{len(hits)}/{len(procs)} procedimentos com página"}],
            None if status in (Status.pass_, Status.unknown) else f"Faltam: {sorted(set(procs) - set(hits))}")

    def _qa_content(self, soup, data: dict, url) -> SignalResult:
        has_faq = "faqpage" in self._schema_types(data)
        questions = [h.get_text(strip=True) for h in soup.find_all(["h2", "h3"])
                     if h.get_text(strip=True).endswith("?")]
        has = has_faq or len(questions) >= 3
        return SignalResult("conteudo_perguntas", "Conteúdo que responde perguntas reais",
            Status.pass_ if has else Status.fail, has, 5, 0.8, "site_scrape",
            [{"fonte": "site", "url": url,
              "resumo": f"FAQPage={has_faq}; headings-pergunta={len(questions)}"}])

    # --- helpers ---
    def _schema_types(self, data: dict) -> set[str]:
        types: set[str] = set()
        for syntax in ("json-ld", "microdata"):
            for item in data.get(syntax, []):
                t = item.get("@type")
                for v in ([t] if isinstance(t, str) else t or []):
                    types.add(_norm(str(v)))
        return types

    def _labels(self):
        return [("crm_rqe_visivel", "CRM/RQE visível no site"),
                ("schema_medico", "Tem schema médico (Physician/MedicalClinic)"),
                ("pagina_especialidade", "Tem página por especialidade"),
                ("pagina_procedimento", "Tem página por procedimento"),
                ("conteudo_perguntas", "Conteúdo que responde perguntas reais")]

    def _unknown(self, id_: str, label: str,
                 resumo: str = "Médico sem site informado.",
                 obs: str = "Sem site para analisar.") -> SignalResult:
        return SignalResult(id_, label, Status.unknown, False, 5, 0.0, "site_scrape",
                            [{"fonte": "site", "resumo": resumo}], obs)
