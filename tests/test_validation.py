import pytest
from visibility.validation import validate_report, SchemaValidationError
from tests.test_models import _sinal  # reuse helper
from visibility.models import (
    VisibilityReport, Meta, DoctorMeta, RunMeta, Score, CategoriaScore,
    Categoria, Concorrentes, Ofensor, PromptIA,
)


def _valid_report() -> VisibilityReport:
    return VisibilityReport(
        meta=Meta(
            doctor=DoctorMeta(nome="Dra. Fulana", especialidade_principal="Dermatologia",
                              cidade="São Paulo", uf="SP"),
            run=RunMeta(gerado_em="2026-06-28T14:00:00Z", pipeline_version="0.1.0")),
        score=Score(total=0, max=100, tier="Bronze",
                    categorias={"busca_tradicional": CategoriaScore(score=0, max=25)}),
        categorias={"busca_tradicional": Categoria(
            label="Busca tradicional", score=0, max=25, weight=25, sinais=[_sinal()])},
        concorrentes=Concorrentes(resumo="r", ofensores_recorrentes=[Ofensor(nome="Dr. X", aparicoes=6)]),
        prompts_ia=[PromptIA(id="p1", prompt="q", tipo="procedimento", engine="chatgpt", medico_citado=False)],
    )


def test_serialized_model_validates_against_schema():
    data = _valid_report().model_dump(mode="json", exclude_none=True)
    validate_report(data)  # must not raise


def test_invalid_report_raises():
    data = _valid_report().model_dump(mode="json", exclude_none=True)
    data["score"]["tier"] = "Platinum"  # not in enum
    with pytest.raises(SchemaValidationError):
        validate_report(data)
