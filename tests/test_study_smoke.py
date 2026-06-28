import json
from visibility.study.cli import run

def test_pipeline_demand_para_aggregate(tmp_path):
    cfg = {"demand": {"especialidades": ["Dermatologia"], "cidades": ["SP"],
                      "procedimentos": {"Dermatologia": ["botox"]},
                      "prompt_tipos": ["melhor_especialista"],
                      "engines": ["chatgpt"], "repeticoes": 1},
           "rosters": []}
    cfgp = tmp_path / "study.json"; cfgp.write_text(json.dumps(cfg), encoding="utf-8")

    def fake_engines(settings):
        class L:
            name = "chatgpt"
            def ask(self, p): return "Indico a Dra. Ana Lima; veja no Doctoralia."
        return {"chatgpt": L()}

    dem = tmp_path / "demand.json"
    assert run(["demand", "--config", str(cfgp), "--out", str(dem),
                "--now", "2026-06-28T14:00:00Z"], engines_factory=fake_engines) == 0

    sup = tmp_path / "supply.json"; sup.write_text("{}", encoding="utf-8")
    agg = tmp_path / "aggregates.json"
    assert run(["aggregate", "--demand", str(dem), "--supply", str(sup),
                "--out", str(agg), "--now", "2026-06-28T14:00:00Z"]) == 0

    data = json.loads(agg.read_text(encoding="utf-8"))
    assert data["demanda"]["pct_com_medico_nominal"] == 1.0
    assert ["doctoralia", 1] in data["demanda"]["top_marketplaces"]
