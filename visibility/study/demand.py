from __future__ import annotations
from dataclasses import dataclass
from visibility.clients import LLMClient
from visibility.study.config import DemandMatrix, PROMPT_TEMPLATES

@dataclass
class DemandPrompt:
    especialidade: str
    cidade: str
    tipo: str
    procedimento: str | None
    texto: str

def build_demand_prompts(m: DemandMatrix) -> list[DemandPrompt]:
    out: list[DemandPrompt] = []
    for esp in m.especialidades:
        for cidade in m.cidades:
            for tipo in m.prompt_tipos:
                tmpl = PROMPT_TEMPLATES[tipo]
                if tipo == "procedimento":
                    for proc in m.procedimentos.get(esp, []):
                        out.append(DemandPrompt(
                            esp, cidade, tipo, proc,
                            tmpl.format(procedimento=proc, cidade=cidade)))
                else:
                    out.append(DemandPrompt(
                        esp, cidade, tipo, None,
                        tmpl.format(especialidade=esp, cidade=cidade)))
    return out

@dataclass
class DemandResponse:
    especialidade: str
    cidade: str
    tipo: str
    procedimento: str | None
    engine: str
    rep: int
    capturado_em: str
    texto: str

class DemandRunner:
    def __init__(self, engines: dict[str, LLMClient], repeticoes: int = 1):
        self.engines = engines          # nome do motor -> cliente
        self.repeticoes = repeticoes

    def run(self, prompts: list[DemandPrompt], now: str) -> list[DemandResponse]:
        out: list[DemandResponse] = []
        for p in prompts:
            for engine_name, client in self.engines.items():
                for rep in range(1, self.repeticoes + 1):
                    texto = client.ask(p.texto)
                    out.append(DemandResponse(
                        especialidade=p.especialidade, cidade=p.cidade, tipo=p.tipo,
                        procedimento=p.procedimento, engine=engine_name, rep=rep,
                        capturado_em=now, texto=texto))
        return out
