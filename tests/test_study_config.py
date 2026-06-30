from visibility.study.config import StudyConfig, DemandMatrix, PROMPT_TEMPLATES

RAW = {
    "demand": {
        "especialidades": ["Dermatologia", "Cirurgia Plástica"],
        "cidades": ["São Paulo", "Rio de Janeiro"],
        "procedimentos": {"Dermatologia": ["botox", "preenchimento"],
                          "Cirurgia Plástica": ["rinoplastia"]},
        "prompt_tipos": ["melhor_especialista", "procedimento"],
        "engines": ["chatgpt", "gemini"],
        "repeticoes": 2,
    },
    "rosters": [
        {"especialidade": "Dermatologia", "arquivo": "rosters/derm.json"},
    ],
}

def test_from_dict_parses_all_fields():
    cfg = StudyConfig.from_dict(RAW)
    assert isinstance(cfg.demand, DemandMatrix)
    assert cfg.demand.especialidades == ["Dermatologia", "Cirurgia Plástica"]
    assert cfg.demand.procedimentos["Cirurgia Plástica"] == ["rinoplastia"]
    assert cfg.demand.repeticoes == 2
    assert cfg.rosters[0].especialidade == "Dermatologia"
    assert cfg.rosters[0].arquivo == "rosters/derm.json"

def test_repeticoes_defaults_to_one():
    raw = {"demand": {"especialidades": ["X"], "cidades": ["Y"],
                      "procedimentos": {}, "prompt_tipos": ["melhor_especialista"],
                      "engines": ["chatgpt"]}}
    cfg = StudyConfig.from_dict(raw)
    assert cfg.demand.repeticoes == 1
    assert cfg.rosters == []

def test_prompt_templates_cover_declared_tipos():
    for tipo in ["melhor_especialista", "procedimento", "confianca"]:
        assert tipo in PROMPT_TEMPLATES

def test_from_file_roundtrips(tmp_path):
    import json
    p = tmp_path / "study.json"
    p.write_text(json.dumps(RAW), encoding="utf-8")
    cfg = StudyConfig.from_file(str(p))
    assert cfg.demand.cidades == ["São Paulo", "Rio de Janeiro"]
