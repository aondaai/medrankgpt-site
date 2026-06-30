from visibility.study.aggregate import DemandAggregate, SupplyAggregate
from visibility.study.export import build_aggregates, validate_aggregates, SchemaValidationError
import pytest

def _demand():
    return DemandAggregate(
        total_respostas=3, pct_com_medico_nominal=0.33, pct_marketplace=0.33,
        pct_nenhum=0.34, cfm_risco_pct=0.1, divergencia_motores_pct=0.5,
        por_especialidade={"Dermatologia": {"total": 3, "pct_com_medico_nominal": 0.33,
                            "pct_marketplace": 0.33, "pct_nenhum": 0.34, "cfm_risco_pct": 0.1}},
        top_medicos=[["Dra. Ana Lima", 2]], top_marketplaces=[["doctoralia", 1]])

def _supply():
    return SupplyAggregate(por_especialidade={"Dermatologia": {
        "n": 4, "mediana": 50.0, "p25": 30.0, "p75": 70.0, "pct_abaixo_50": 0.5,
        "media_por_categoria": {"visibilidade_ia": 15.0},
        "top_decil": {"n": 1, "media_por_categoria": {"visibilidade_ia": 25.0}}}})

def test_build_aggregates_estrutura_e_sem_pii():
    data = build_aggregates(_demand(), _supply(), now="2026-06-28T14:00:00Z",
                            pipeline_version="0.1.0")
    assert data["schema_version"] == "1.0"
    assert data["meta"]["gerado_em"] == "2026-06-28T14:00:00Z"
    assert data["demanda"]["total_respostas"] == 3
    assert data["oferta"]["por_especialidade"]["Dermatologia"]["n"] == 4
    # top_medicos é share-of-voice agregado (aparece), mas NÃO há blocos por-médico nominais na oferta
    assert "medicos" not in data["oferta"]

def test_validate_aggregates_aceita_documento_valido():
    data = build_aggregates(_demand(), _supply(), now="2026-06-28T14:00:00Z",
                            pipeline_version="0.1.0")
    validate_aggregates(data)   # não levanta

def test_validate_aggregates_rejeita_documento_invalido():
    with pytest.raises(SchemaValidationError):
        validate_aggregates({"schema_version": "1.0"})   # faltam campos obrigatórios
