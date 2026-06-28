import json
from visibility.study.config import RosterSpec
from visibility.study.supply import load_roster, run_supply
from visibility.models import DoctorMeta, VisibilityReport
from visibility.collectors.base import CollectorContext, CollectorOutput, SignalResult
from visibility.models import Status

def _doc(nome):
    return {"nome": nome, "especialidade_principal": "Dermatologia",
            "cidade": "São Paulo", "uf": "SP", "procedimentos_foco": ["botox"]}

def test_load_roster(tmp_path):
    p = tmp_path / "derm.json"
    p.write_text(json.dumps([_doc("Dra. Ana Lima"), _doc("Dr. Bruno Souza")]),
                 encoding="utf-8")
    docs = load_roster(str(p))
    assert [d.nome for d in docs] == ["Dra. Ana Lima", "Dr. Bruno Souza"]
    assert isinstance(docs[0], DoctorMeta)

class _FakeCollector:
    category = "site_conteudo"
    def collect(self, ctx: CollectorContext) -> CollectorOutput:
        return CollectorOutput(signals=[SignalResult(
            "tem_site", "Tem site", Status.pass_, True, 12.5, 0.9, "stub",
            [{"fonte": "stub", "resumo": "ok"}])])

def test_run_supply_one_report_per_doctor(tmp_path):
    p = tmp_path / "derm.json"
    p.write_text(json.dumps([_doc("Dra. Ana Lima"), _doc("Dr. Bruno Souza")]),
                 encoding="utf-8")
    rosters = [RosterSpec("Dermatologia", str(p))]
    out = run_supply(rosters, collector_factory=lambda s: [_FakeCollector()],
                     settings=None, now="2026-06-28T14:00:00Z", pipeline_version="0.1.0")
    assert set(out) == {"Dermatologia"}
    reports = out["Dermatologia"]
    assert len(reports) == 2
    assert all(isinstance(r, VisibilityReport) for r in reports)
    assert reports[0].score.total > 0   # FakeCollector dá 1 sinal pass
