from __future__ import annotations
from urllib.parse import urlparse
from visibility.clients import SearchClient
from visibility.collectors.base import CollectorContext, CollectorOutput, SignalResult
from visibility.models import Status

def _domain(url: str) -> str:
    return (urlparse(url).hostname or "").lower().removeprefix("www.")

class GoogleSearchCollector:
    category = "busca_tradicional"

    def __init__(self, search: SearchClient):
        self.search = search

    def collect(self, ctx: CollectorContext) -> CollectorOutput:
        query = f"{ctx.doctor.nome} {ctx.doctor.especialidade_principal}"
        try:
            payload = self.search.search(query, location=ctx.regiao_busca)
        except Exception as exc:
            return CollectorOutput(signals=[SignalResult(
                "google_marca", "Aparece no Google ao buscar o nome", Status.unknown,
                False, 12.5, 0.0, "serp_scrape",
                [{"fonte": "google_search", "query": query,
                  "resumo": f"Busca indisponível: {type(exc).__name__}."}],
                "Não foi possível consultar o Google.")])
        results = payload.get("organic_results", [])[:10]
        own = _domain(ctx.doctor.site) if ctx.doctor.site else None
        own_hit = bool(own) and any(_domain(r.get("link", "")) == own for r in results)
        name_hit = len(results) > 0
        if own_hit:
            status, obs = Status.pass_, None
        elif name_hit:
            status, obs = Status.partial, "Aparece só via perfis de terceiros, não com domínio próprio."
        else:
            status, obs = Status.fail, "Não aparece no top 10 ao buscar o nome."
        top = [{"position": r.get("position"), "link": r.get("link")} for r in results[:5]]
        return CollectorOutput(signals=[SignalResult(
            "google_marca", "Aparece no Google ao buscar o nome", status, own_hit, 12.5,
            0.9, "serp_scrape",
            [{"fonte": "google_search", "query": query,
              "resumo": f"top10={len(results)}, dominio proprio={own_hit}",
              "raw": {"resultados": top}}], obs)])
