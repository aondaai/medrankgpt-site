from __future__ import annotations
import re
import unicodedata
from visibility.clients import LLMClient
from visibility.collectors.base import CollectorContext, CollectorOutput, SignalResult
from visibility.models import Status, PromptIA, DoctorMeta

# "Dr." / "Dra." followed by 1–3 capitalized (incl. accented) name words.
_DOCTOR_NAME_RE = re.compile(
    r"\bDr[a]?\.?\s+[A-ZÀ-Ý][\wÀ-ÿ]+(?:\s+[A-ZÀ-Ý][\wÀ-ÿ]+){0,2}")

def _norm(s: str) -> str:
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii").lower()

def _tokens(name: str) -> set[str]:
    drop = {"dr", "dra", "de", "da", "do", "dos", "das"}
    return {t for t in _norm(name).replace(".", " ").split() if t and t not in drop}

def _cited(answer: str, name: str) -> bool:
    return bool(_tokens(name)) and _tokens(name) <= set(_norm(answer).replace(".", " ").split())

def extract_competitors(answer: str, own_name: str) -> list[str]:
    """Pull 'Dr./Dra. Nome' mentions from a free-text answer, excluding the doctor.
    Deduplicates while preserving first-seen order."""
    own = _tokens(own_name)
    seen: list[str] = []
    for raw in _DOCTOR_NAME_RE.findall(answer):
        name = re.sub(r"\s+", " ", raw).strip()
        cand = _tokens(name)
        # skip if this mention IS the doctor — the regex stops at lowercase connectives
        # ("Dra. Fulana de Tal" -> "Dra. Fulana"), so match a subset in EITHER direction.
        if own and cand and (cand <= own or own <= cand):
            continue
        if name not in seen:
            seen.append(name)
    return seen

def build_prompts(doctor: DoctorMeta, regiao: str | None) -> list[dict]:
    loc = regiao or f"{doctor.cidade}, {doctor.uf}"
    prompts = [{"tipo": "marca",
                "prompt": f"O que você sabe sobre a médica {doctor.nome}, "
                          f"{doctor.especialidade_principal} em {loc}?"}]
    for proc in doctor.procedimentos_foco:
        prompts.append({"tipo": "procedimento",
                        "prompt": f"Quem é o melhor médico para {proc} em {loc}?"})
    return prompts

class AiEnginesCollector:
    category = "visibilidade_ia"

    def __init__(self, engines: dict[str, LLMClient]):
        self.engines = engines  # engine name (schema enum) -> client

    def collect(self, ctx: CollectorContext) -> CollectorOutput:
        prompts = build_prompts(ctx.doctor, ctx.regiao_busca)
        log: list[PromptIA] = []
        idx = 0
        for spec in prompts:
            for engine_name, client in self.engines.items():
                answer = client.ask(spec["prompt"])
                cited = _cited(answer, ctx.doctor.nome)
                idx += 1
                log.append(PromptIA(
                    id=f"p{idx}", prompt=spec["prompt"], tipo=spec["tipo"],
                    engine=engine_name, regiao=ctx.regiao_busca, medico_citado=cited,
                    concorrentes_citados=extract_competitors(answer, ctx.doctor.nome),
                    capturado_em=ctx.now, raw_resposta=answer))
        marca = [p for p in log if p.tipo == "marca"]
        proc = [p for p in log if p.tipo == "procedimento"]
        return CollectorOutput(signals=[
            self._signal("ia_marca", "Aparece em respostas de IA pela marca", marca, 0.8),
            self._signal("ia_procedimento", "Aparece em perguntas de procedimento", proc, 0.8),
        ], prompts=log)

    def _signal(self, id_, label, entries: list[PromptIA], conf) -> SignalResult:
        if not entries:
            status, valor, obs = Status.unknown, False, "Nenhum prompt deste tipo executado."
        else:
            hits = sum(p.medico_citado for p in entries)
            if hits == len(entries):
                status, obs = Status.pass_, None
            elif hits:
                status, obs = Status.partial, f"Citado em {hits}/{len(entries)} prompts."
            else:
                status, obs = Status.fail, "Não citado em nenhum prompt."
            valor = hits > 0
        return SignalResult(id_, label, status, valor, 12.5, conf, "llm_prompt",
            [{"fonte": "ai_engines",
              "resumo": f"{sum(p.medico_citado for p in entries)}/{len(entries)} prompts citaram o médico"}],
            obs)
