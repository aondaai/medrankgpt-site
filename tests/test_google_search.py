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
