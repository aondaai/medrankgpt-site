import json
from pathlib import Path
from visibility.collectors.base import CollectorContext
from visibility.collectors.google_search import GoogleSearchCollector
from visibility.models import DoctorMeta, Status

SERP = json.loads((Path(__file__).parent / "fixtures" / "serp_drafulana.json").read_text())

class FakeSearch:
    def __init__(self, payload): self.payload = payload
    def search(self, query: str, location: str | None = None) -> dict: return self.payload

def _ctx(site="https://drafulana.com.br"):
    return CollectorContext(
        doctor=DoctorMeta(nome="Dra. Fulana", especialidade_principal="Dermatologia",
                          cidade="São Paulo", uf="SP", site=site),
        now="2026-06-28T14:00:00Z", regiao_busca="São Paulo, SP")

def test_partial_when_only_third_party():
    out = GoogleSearchCollector(search=FakeSearch(SERP)).collect(_ctx())
    s = out.signals[0]
    assert s.id == "google_marca"
    assert s.status == Status.partial  # appears via Doctoralia, not own domain

def test_pass_when_own_domain_present():
    payload = {"organic_results": [
        {"position": 1, "title": "Dra. Fulana", "link": "https://drafulana.com.br/sobre"}]}
    out = GoogleSearchCollector(search=FakeSearch(payload)).collect(_ctx())
    assert out.signals[0].status == Status.pass_

def test_fail_when_absent():
    payload = {"organic_results": [{"position": 1, "title": "Z", "link": "https://z.com"}]}
    out = GoogleSearchCollector(search=FakeSearch(payload)).collect(_ctx())
    # third test: with results present but no own domain -> partial, not fail.
    # To test fail, use an empty result set:
    out_empty = GoogleSearchCollector(search=FakeSearch({"organic_results": []})).collect(_ctx())
    assert out_empty.signals[0].status == Status.fail


def test_raw_round_trips_through_to_sinal():
    # raw must be a dict (not a list) so the Evidencia model accepts it.
    payload = {"organic_results": [
        {"position": 1, "title": "A", "link": "https://a.com"},
        {"position": 2, "title": "B", "link": "https://b.com"}]}
    ctx = _ctx()
    out = GoogleSearchCollector(search=FakeSearch(payload)).collect(ctx)
    sinal = out.signals[0].to_sinal(ctx)  # must NOT raise ValidationError
    raw = sinal.evidencia[0].raw
    assert isinstance(raw, dict)
    assert raw == {"resultados": [
        {"position": 1, "link": "https://a.com"},
        {"position": 2, "link": "https://b.com"}]}


def test_search_error_degrades_to_unknown():
    class BoomSearch:
        def search(self, query, location=None):
            raise RuntimeError("429 Too Many Requests")
    out = GoogleSearchCollector(search=BoomSearch()).collect(_ctx())
    assert out.signals[0].id == "google_marca"
    assert out.signals[0].status == Status.unknown
