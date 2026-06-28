from __future__ import annotations
from visibility.clients import LLMClient
from visibility.collectors.base import CollectorContext, CollectorOutput, SignalResult
from visibility.models import Status, PromptIA, DoctorMeta
from visibility.names import tokens, same_person, mentioned_names

def _cited(answer: str, doctor_name: str) -> bool:
    own = tokens(doctor_name)
    return any(same_person(own, tokens(span)) for span in mentioned_names(answer))

def extract_competitors(answer: str, own_name: str) -> list[str]:
    own = tokens(own_name)
    out: list[str] = []
    for span in mentioned_names(answer):
        if same_person(own, tokens(span)):   # skip the doctor herself
            continue
        if span not in out:
            out.append(span)
    return out

def build_prompts(doctor: DoctorMeta, regiao: str | None) -> list[dict]:
    loc = regiao or f"{doctor.cidade}, {doctor.uf}"
    prompts = [{"tipo": "marca",
                "prompt": f"O que você sabe sobre {doctor.nome}, "
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
