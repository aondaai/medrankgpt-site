from __future__ import annotations
import math
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from statistics import median
from visibility.study.demand import DemandResponse
from visibility.study.classify import classify_response
from visibility.models import VisibilityReport

@dataclass
class DemandAggregate:
    total_respostas: int
    pct_com_medico_nominal: float
    pct_marketplace: float
    pct_nenhum: float
    cfm_risco_pct: float
    divergencia_motores_pct: float
    por_especialidade: dict[str, dict] = field(default_factory=dict)
    top_medicos: list[list] = field(default_factory=list)        # [[nome, contagem], ...]
    top_marketplaces: list[list] = field(default_factory=list)   # [[id, contagem], ...]

def _safe_div(a: float, b: float) -> float:
    return a / b if b else 0.0

def aggregate_demand(responses: list[DemandResponse], top_n: int = 20) -> DemandAggregate:
    classifs = [(r, classify_response(r.texto)) for r in responses]
    total = len(classifs)

    n_medico = sum(1 for _, c in classifs if c.tipo_resposta == "medico_nominal")
    n_market = sum(1 for _, c in classifs if c.tipo_resposta == "marketplace")
    n_nenhum = sum(1 for _, c in classifs if c.tipo_resposta == "nenhum")
    n_cfm = sum(1 for _, c in classifs if c.cfm_risco)

    medicos: Counter[str] = Counter()
    markets: Counter[str] = Counter()
    for _, c in classifs:
        for m in c.medicos:
            medicos[m] += 1
        for mk in c.marketplaces:
            markets[mk] += 1

    # por especialidade
    por_esp: dict[str, dict] = {}
    by_esp: dict[str, list] = defaultdict(list)
    for r, c in classifs:
        by_esp[r.especialidade].append(c)
    for esp, cs in by_esp.items():
        n = len(cs)
        por_esp[esp] = {
            "total": n,
            "pct_com_medico_nominal": _safe_div(
                sum(1 for c in cs if c.tipo_resposta == "medico_nominal"), n),
            "pct_marketplace": _safe_div(
                sum(1 for c in cs if c.tipo_resposta == "marketplace"), n),
            "pct_nenhum": _safe_div(sum(1 for c in cs if c.tipo_resposta == "nenhum"), n),
            "cfm_risco_pct": _safe_div(sum(1 for c in cs if c.cfm_risco), n),
        }

    # divergência entre motores: por célula (esp,cidade,tipo,procedimento),
    # olha o "top médico" (1º citado) de cada motor; diverge se há >1 médico distinto.
    cells: dict[tuple, dict[str, str | None]] = defaultdict(dict)
    for r, c in classifs:
        key = (r.especialidade, r.cidade, r.tipo, r.procedimento)
        top = c.medicos[0] if c.medicos else None
        cells[key][r.engine] = top
    multi = [d for d in cells.values() if len(d) >= 2]
    divergentes = sum(1 for d in multi if len({v for v in d.values() if v}) > 1
                      or any(v is None for v in d.values()))
    divergencia = _safe_div(divergentes, len(multi))

    return DemandAggregate(
        total_respostas=total,
        pct_com_medico_nominal=_safe_div(n_medico, total),
        pct_marketplace=_safe_div(n_market, total),
        pct_nenhum=_safe_div(n_nenhum, total),
        cfm_risco_pct=_safe_div(n_cfm, total),
        divergencia_motores_pct=divergencia,
        por_especialidade=por_esp,
        top_medicos=[[n, c] for n, c in medicos.most_common(top_n)],
        top_marketplaces=[[n, c] for n, c in markets.most_common(top_n)],
    )

@dataclass
class SupplyAggregate:
    por_especialidade: dict[str, dict] = field(default_factory=dict)

def _percentile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    s = sorted(values)
    if len(s) == 1:
        return float(s[0])
    pos = q * (len(s) - 1)
    lo = math.floor(pos)
    hi = math.ceil(pos)
    if lo == hi:
        return float(s[lo])
    return float(s[lo] + (s[hi] - s[lo]) * (pos - lo))

def _media_categorias(reports: list[VisibilityReport]) -> dict[str, float]:
    soma: dict[str, float] = defaultdict(float)
    cont: dict[str, int] = defaultdict(int)
    for r in reports:
        for key, cs in r.score.categorias.items():
            soma[key] += cs.score
            cont[key] += 1
    return {k: round(soma[k] / cont[k], 4) for k in soma}

def aggregate_supply(reports_by_esp: dict[str, list[VisibilityReport]]) -> SupplyAggregate:
    por_esp: dict[str, dict] = {}
    for esp, reports in reports_by_esp.items():
        totais = [r.score.total for r in reports]
        n = len(reports)
        limiar = _percentile(totais, 0.9) if n > 1 else (totais[0] if totais else 0.0)
        top = [r for r in reports if r.score.total >= limiar] or reports[:]
        por_esp[esp] = {
            "n": n,
            "mediana": round(median(totais), 4) if totais else 0.0,
            "p25": round(_percentile(totais, 0.25), 4),
            "p75": round(_percentile(totais, 0.75), 4),
            "pct_abaixo_50": round(sum(1 for t in totais if t < 50) / n, 4) if n else 0.0,
            "media_por_categoria": _media_categorias(reports),
            "top_decil": {
                "n": len(top),
                "media_por_categoria": _media_categorias(top),
            },
        }
    return SupplyAggregate(por_especialidade=por_esp)
