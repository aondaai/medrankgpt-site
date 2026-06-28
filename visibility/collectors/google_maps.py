from __future__ import annotations
from visibility.clients import PlacesClient
from visibility.collectors.base import CollectorContext, CollectorOutput, SignalResult
from visibility.models import Status
from visibility.names import tokens, same_person

class GoogleMapsCollector:
    category = "busca_tradicional"

    def __init__(self, places: PlacesClient):
        self.places = places

    def collect(self, ctx: CollectorContext) -> CollectorOutput:
        query = f"{ctx.doctor.nome} {ctx.doctor.cidade}"
        try:
            payload = self.places.text_search(query)
        except Exception as exc:
            return CollectorOutput(signals=[SignalResult(
                "google_maps", "Aparece no Google Maps / Perfil de Empresa", Status.unknown,
                False, 12.5, 0.0, "gmaps_api",
                [{"fonte": "google_maps", "query": query,
                  "resumo": f"Maps indisponível: {type(exc).__name__}."}],
                "Não foi possível consultar o Google Maps.")])
        wanted = tokens(ctx.doctor.nome)
        match = None
        for r in payload.get("results", []):
            if same_person(wanted, tokens(r.get("name", ""))):
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
