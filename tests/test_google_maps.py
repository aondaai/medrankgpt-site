import json
from pathlib import Path
from visibility.collectors.base import CollectorContext
from visibility.collectors.google_maps import GoogleMapsCollector
from visibility.models import DoctorMeta, Status

PLACES = json.loads((Path(__file__).parent / "fixtures" / "places_drafulana.json").read_text())

class FakePlaces:
    def __init__(self, payload): self.payload = payload
    def text_search(self, query: str) -> dict: return self.payload

def _ctx():
    return CollectorContext(
        doctor=DoctorMeta(nome="Dra. Fulana de Tal", especialidade_principal="Dermatologia",
                          cidade="São Paulo", uf="SP"),
        now="2026-06-28T14:00:00Z")

def test_pass_when_listing_found():
    out = GoogleMapsCollector(places=FakePlaces(PLACES)).collect(_ctx())
    assert out.signals[0].id == "google_maps"
    assert out.signals[0].status == Status.pass_

def test_fail_when_no_match():
    out = GoogleMapsCollector(places=FakePlaces({"results": [
        {"name": "Padaria do Zé", "place_id": "x"}]})).collect(_ctx())
    assert out.signals[0].status == Status.fail


def test_search_error_degrades_to_unknown():
    class BoomPlaces:
        def text_search(self, query):
            raise RuntimeError("500 Server Error")
    out = GoogleMapsCollector(places=BoomPlaces()).collect(_ctx())
    assert out.signals[0].id == "google_maps"
    assert out.signals[0].status == Status.unknown
