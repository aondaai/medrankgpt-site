from pathlib import Path
from visibility.collectors.base import CollectorContext
from visibility.collectors.site_analysis import SiteAnalysisCollector
from visibility.models import DoctorMeta, Status

FIXTURE = (Path(__file__).parent / "fixtures" / "site_drafulana.html").read_text()

class FakeHttp:
    def __init__(self, body): self.body = body
    def get_text(self, url: str) -> str: return self.body

def _ctx():
    return CollectorContext(
        doctor=DoctorMeta(nome="Dra. Fulana de Tal", especialidade_principal="Dermatologia",
                          cidade="São Paulo", uf="SP", site="https://drafulana.com.br",
                          procedimentos_foco=["botox", "preenchimento", "acne"]),
        now="2026-06-28T14:00:00Z")

def _by_id(out):
    return {s.id: s for s in out.signals}

def test_site_signals():
    out = SiteAnalysisCollector(http=FakeHttp(FIXTURE)).collect(_ctx())
    sig = _by_id(out)
    assert sig["crm_rqe_visivel"].status == Status.pass_
    assert sig["schema_medico"].status == Status.pass_
    assert sig["pagina_especialidade"].status == Status.pass_
    assert sig["pagina_procedimento"].status == Status.partial   # botox only, not all 3
    assert sig["conteudo_perguntas"].status == Status.pass_      # 3 question headings

def test_no_site_yields_unknown():
    ctx = _ctx(); ctx.doctor.site = None
    out = SiteAnalysisCollector(http=FakeHttp("")).collect(ctx)
    assert all(s.status == Status.unknown for s in out.signals)
