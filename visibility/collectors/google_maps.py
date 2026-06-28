from __future__ import annotations
import unicodedata
from visibility.clients import PlacesClient
from visibility.collectors.base import CollectorContext, CollectorOutput, SignalResult
from visibility.models import Status

def _norm(s: str) -> str:
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii").lower()

def _name_tokens(name: str) -> set[str]:
    drop = {"dr", "dra", "de", "da", "do", "dos", "das"}
    return {t for t in _norm(name).replace(".", " ").split() if t and t not in drop}

class GoogleMapsCollector:
    category = "busca_tradicional"

    def __init__(self, places: PlacesClient):
        self.places = places

    def collect(self, ctx: CollectorContext) -> CollectorOutput:
        query = f"{ctx.doctor.nome} {ctx.doctor.cidade}"
        payload = self.places.text_search(query)
        wanted = _name_tokens(ctx.doctor.nome)
        match = None
        for r in payload.get("results", []):
            if wanted and wanted <= _name_tokens(r.get("name", "")):
                match = r
                break
        status = Status.pass_ if match else Status.fail
        resumo = (f"Ficha encontrada: {match['name']}" if match
                  else "Nenhuma ficha verificada para o nome na cidade.")
        return CollectorOutput(signals=[SignalResult(
            "google_maps", "Aparece no Google Maps / Perfil de Empresa", status, bool(match),
            12.5, 0.92, "gmaps_api",
            [{"fonte": "google_maps", "query": query, "resumo": resumo,
              "raw": match}], None if match else "Sem perfil de empresa verificado.")])
