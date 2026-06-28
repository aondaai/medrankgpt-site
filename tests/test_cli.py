import json
from pathlib import Path
from visibility.cli import run
from visibility.collectors.base import CollectorOutput, SignalResult
from visibility.models import Status

INPUT = str(Path(__file__).parent / "fixtures" / "doctor_input.json")

class FakeCollector:
    category = "site_conteudo"
    def collect(self, ctx):
        return CollectorOutput(signals=[
            SignalResult("crm_rqe_visivel", "CRM/RQE", Status.pass_, True, 5, 1.0, "m",
                         [{"fonte": "site", "resumo": "ok"}])])

def test_run_writes_valid_report(tmp_path):
    out = tmp_path / "report.json"
    code = run(["--doctor", INPUT, "--out", str(out), "--now", "2026-06-28T14:00:00Z",
                "--pipeline-version", "0.1.0"],
               collector_factory=lambda settings: [FakeCollector()])
    assert code == 0
    data = json.loads(out.read_text())
    assert data["meta"]["doctor"]["nome"] == "Dra. Fulana de Tal"
    assert data["score"]["tier"] in ("Bronze", "Prata", "Ouro")
    assert data["categorias"]["site_conteudo"]["sinais"][0]["id"] == "crm_rqe_visivel"
    # output is schema-valid
    from visibility.validation import validate_report
    validate_report(data)
