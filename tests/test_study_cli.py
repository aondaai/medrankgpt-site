import json
from visibility.study.cli import run

def _study_cfg(tmp_path, roster_path):
    cfg = {
        "demand": {"especialidades": ["Dermatologia"], "cidades": ["SP"],
                   "procedimentos": {"Dermatologia": ["botox"]},
                   "prompt_tipos": ["melhor_especialista", "procedimento"],
                   "engines": ["chatgpt"], "repeticoes": 1},
        "rosters": [{"especialidade": "Dermatologia", "arquivo": roster_path}],
    }
    p = tmp_path / "study.json"
    p.write_text(json.dumps(cfg), encoding="utf-8")
    return str(p)

def test_plan_imprime_estimativa(tmp_path, capsys):
    cfg = _study_cfg(tmp_path, "rosters/x.json")
    rc = run(["plan", "--config", cfg, "--roster-size", "50"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "chamadas" in out.lower() and "usd" in out.lower()

def test_demand_escreve_respostas(tmp_path):
    cfg = _study_cfg(tmp_path, "rosters/x.json")
    out = tmp_path / "raw_demand.json"
    # engine factory scriptado: nunca toca a rede
    def fake_engines(settings):
        class L:
            name = "chatgpt"
            def ask(self, p): return "Indico a Dra. Ana Lima."
        return {"chatgpt": L()}
    rc = run(["demand", "--config", cfg, "--out", str(out),
              "--now", "2026-06-28T14:00:00Z"], engines_factory=fake_engines)
    assert rc == 0
    data = json.loads(out.read_text(encoding="utf-8"))
    # 1 melhor + 1 procedimento = 2 prompts × 1 engine × 1 rep
    assert len(data) == 2
    assert data[0]["engine"] == "chatgpt"

def test_aggregate_gera_aggregates_valido(tmp_path):
    # respostas de demanda mínimas
    demand = [{"especialidade": "Dermatologia", "cidade": "SP",
               "tipo": "melhor_especialista", "procedimento": None,
               "engine": "chatgpt", "rep": 1, "capturado_em": "t",
               "texto": "Indico a Dra. Ana Lima."}]
    dpath = tmp_path / "raw_demand.json"
    dpath.write_text(json.dumps(demand), encoding="utf-8")
    # supply vazio é válido (sem rosters rodados)
    spath = tmp_path / "raw_supply.json"
    spath.write_text(json.dumps({}), encoding="utf-8")
    out = tmp_path / "aggregates.json"
    rc = run(["aggregate", "--demand", str(dpath), "--supply", str(spath),
              "--out", str(out), "--now", "2026-06-28T14:00:00Z"])
    assert rc == 0
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema_version"] == "1.0"
    assert data["demanda"]["total_respostas"] == 1
