from __future__ import annotations
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from urllib.parse import urlparse
from visibility.study.config import DemandMatrix
from visibility.study.serp_classify import classify_serp_item, summarize_serp

def _host(link: str) -> str:
    h = (urlparse(link).hostname or "").lower()
    return h[4:] if h.startswith("www.") else h

def build_serp_queries(m: DemandMatrix, praticantes: dict[str, str] | None = None) -> list[dict]:
    prat = praticantes or {}
    out: list[dict] = []
    for esp in m.especialidades:
        termo = prat.get(esp, esp)
        for cidade in m.cidades:
            out.append({"especialidade": esp, "cidade": cidade, "tipo": "melhor",
                        "procedimento": None, "query": f"melhor {termo} em {cidade}"})
            for proc in m.procedimentos.get(esp, []):
                out.append({"especialidade": esp, "cidade": cidade, "tipo": "procedimento",
                            "procedimento": proc, "query": f"{proc} em {cidade}"})
    return out

@dataclass
class SerpRecord:
    especialidade: str
    cidade: str
    tipo: str
    procedimento: str | None
    query: str
    capturado_em: str
    posicao_1_tipo: str | None
    por_tipo: dict
    dominios: list   # top resultados: [{"position","tipo","link"}]

def run_serp(queries: list[dict], client, now: str, top_k: int = 10) -> list[SerpRecord]:
    out: list[SerpRecord] = []
    for q in queries:
        items = client.search(q["query"], location="Brazil")
        s = summarize_serp(items, top_k=top_k)
        dom = [{"position": it["position"],
                "tipo": classify_serp_item(it["link"], it.get("title", "")),
                "link": it["link"]} for it in items[:top_k]]
        out.append(SerpRecord(q["especialidade"], q["cidade"], q["tipo"], q["procedimento"],
                              q["query"], now, s["posicao_1_tipo"], s["por_tipo"], dom))
    return out

@dataclass
class SerpAggregate:
    total_queries: int
    pos1_por_tipo: dict                # tipo -> fração das queries com esse tipo na posição 1
    share_medio_por_tipo: dict         # tipo -> média da fração da 1ª página
    por_especialidade: dict = field(default_factory=dict)
    por_cidade: dict = field(default_factory=dict)
    top_dominios_pos1: list = field(default_factory=list)   # [[host, contagem], ...]

def _safe_div(a, b): return a / b if b else 0.0

def aggregate_serp(records: list[SerpRecord], top_n: int = 20) -> SerpAggregate:
    total = len(records)
    pos1 = Counter(r.posicao_1_tipo for r in records if r.posicao_1_tipo)
    pos1_pct = {k: _safe_div(v, total) for k, v in pos1.items()}

    share = defaultdict(float)
    for r in records:
        n = sum(r.por_tipo.values()) or 1
        for tipo, c in r.por_tipo.items():
            share[tipo] += c / n
    share_medio = {k: _safe_div(v, total) for k, v in share.items()}

    def pct_mkt(rs):
        return _safe_div(sum(1 for r in rs if r.posicao_1_tipo == "marketplace"), len(rs))
    by_esp = defaultdict(list)
    by_cid = defaultdict(list)
    for r in records:
        by_esp[r.especialidade].append(r)
        by_cid[r.cidade].append(r)
    por_esp = {e: {"total": len(rs), "pct_pos1_marketplace": pct_mkt(rs)} for e, rs in by_esp.items()}
    por_cid = {c: {"total": len(rs), "pct_pos1_marketplace": pct_mkt(rs)} for c, rs in by_cid.items()}

    pos1_doms = Counter()
    for r in records:
        if r.dominios:
            h = _host(r.dominios[0]["link"])
            if h:
                pos1_doms[h] += 1

    return SerpAggregate(
        total_queries=total, pos1_por_tipo=pos1_pct, share_medio_por_tipo=share_medio,
        por_especialidade=por_esp, por_cidade=por_cid,
        top_dominios_pos1=[[h, c] for h, c in pos1_doms.most_common(top_n)])
