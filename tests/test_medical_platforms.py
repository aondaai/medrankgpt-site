from pathlib import Path
from visibility.collectors.base import CollectorContext
from visibility.collectors.medical_platforms import MedicalPlatformsCollector
from visibility.models import DoctorMeta, Status

DOCTORALIA = (Path(__file__).parent / "fixtures" / "doctoralia_results.html").read_text()

class FakeHttp:
    def __init__(self, by_host): self.by_host = by_host
    def get_text(self, url: str) -> str:
        for host, body in self.by_host.items():
            if host in url:
                return body
        return "<html></html>"

def _ctx():
    return CollectorContext(
        doctor=DoctorMeta(nome="Dra. Fulana de Tal", especialidade_principal="Dermatologia",
                          cidade="São Paulo", uf="SP"),
        now="2026-06-28T14:00:00Z")

def test_doctoralia_found_boaconsulta_absent():
    http = FakeHttp({"doctoralia.com.br": DOCTORALIA})  # boaconsulta returns empty
    out = MedicalPlatformsCollector(http=http).collect(_ctx())
    sig = {s.id: s for s in out.signals}
    assert sig["doctoralia"].status == Status.pass_
    assert sig["boaconsulta"].status == Status.fail
