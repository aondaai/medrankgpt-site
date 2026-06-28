from __future__ import annotations
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from visibility.clients import HttpClient
from visibility.collectors.base import CollectorContext, CollectorOutput, SignalResult
from visibility.models import Status
from visibility.names import tokens, same_person

_PLATFORMS = [
    ("doctoralia", "Doctoralia", "https://www.doctoralia.com.br/pesquisa?q={q}"),
    ("boaconsulta", "BoaConsulta", "https://www.boaconsulta.com/busca/?q={q}"),
]

class MedicalPlatformsCollector:
    category = "plataformas_medicas"

    def __init__(self, http: HttpClient):
        self.http = http

    def collect(self, ctx: CollectorContext) -> CollectorOutput:
        wanted = tokens(ctx.doctor.nome)
        signals = []
        for id_, label, tmpl in _PLATFORMS:
            url = tmpl.format(q=quote_plus(ctx.doctor.nome))
            try:
                html = self.http.get_text(url)
            except Exception:
                html = ""
            found_href = self._match(html, wanted)
            status = Status.pass_ if found_href else Status.fail
            signals.append(SignalResult(
                id_, f"Tem perfil na {label}", status, bool(found_href), 12.5, 0.85,
                "profile_scrape",
                [{"fonte": id_, "url": url,
                  "resumo": f"perfil encontrado: {found_href or 'nao'}"}],
                None if found_href else f"Sem perfil na {label} para o nome."))
        return CollectorOutput(signals=signals)

    def _match(self, html: str, wanted: set[str]) -> str | None:
        if not html or not wanted:
            return None
        soup = BeautifulSoup(html, "html.parser")
        for a in soup.find_all("a"):
            if same_person(wanted, tokens(a.get_text(" "))):
                return a.get("href")
        return None
