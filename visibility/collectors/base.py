from __future__ import annotations
from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable
from visibility.models import Sinal, Evidencia, Status, DoctorMeta, PromptIA

@dataclass
class CollectorContext:
    doctor: DoctorMeta
    now: str                     # ISO timestamp, injected for determinism
    regiao_busca: str | None = None

@dataclass
class SignalResult:
    id: str
    label: str
    status: Status
    valor: bool | float | str
    weight: float
    confianca: float
    metodo: str
    evidencia: list[dict]        # each: fonte/url/query/resumo/raw (capturado_em auto-filled)
    observacao: str | None = None

    def to_sinal(self, ctx: CollectorContext) -> Sinal:
        ev = [Evidencia(capturado_em=e.get("capturado_em", ctx.now),
                        fonte=e["fonte"], url=e.get("url"), query=e.get("query"),
                        resumo=e["resumo"], raw=e.get("raw")) for e in self.evidencia]
        return Sinal(id=self.id, label=self.label, status=self.status, valor=self.valor,
                     weight=self.weight, confianca=self.confianca, metodo=self.metodo,
                     observacao=self.observacao, evidencia=ev)

@dataclass
class CollectorOutput:
    signals: list[SignalResult]
    prompts: list[PromptIA] = field(default_factory=list)

@runtime_checkable
class Collector(Protocol):
    category: str                # which category these signals belong to
    def collect(self, ctx: CollectorContext) -> CollectorOutput: ...
