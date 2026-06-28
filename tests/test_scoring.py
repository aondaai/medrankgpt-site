from visibility.models import (
    VisibilityReport, Meta, DoctorMeta, RunMeta, Score, CategoriaScore,
    Categoria, Sinal, Evidencia, Status, Concorrentes,
)
from visibility.scoring import score_report, tier_for

def _ev():
    return [Evidencia(fonte="x", capturado_em="2026-06-28T14:00:00Z", resumo="r")]

def _sig(id_, status, weight):
    return Sinal(id=id_, label=id_, status=status, valor=True, weight=weight,
                 confianca=1.0, metodo="m", evidencia=_ev())

def _report_with(categorias):
    return VisibilityReport(
        meta=Meta(doctor=DoctorMeta(nome="D", especialidade_principal="X", cidade="C", uf="SP"),
                  run=RunMeta(gerado_em="2026-06-28T14:00:00Z", pipeline_version="0.1.0")),
        score=Score(total=0, tier="Bronze", categorias={}),
        categorias=categorias,
        concorrentes=Concorrentes(resumo="r"),
        prompts_ia=[],
    )

def test_points_and_total():
    report = _report_with({
        "busca_tradicional": Categoria(label="Busca", score=0, max=25, weight=25, sinais=[
            _sig("google_marca", Status.partial, 12.5),  # 6.25
            _sig("google_maps", Status.fail, 12.5),       # 0
        ]),
        "site_conteudo": Categoria(label="Site", score=0, max=25, weight=25, sinais=[
            _sig("crm_rqe_visivel", Status.pass_, 5),      # 5
            _sig("schema_medico", Status.fail, 5),         # 0
            _sig("pagina_especialidade", Status.pass_, 5), # 5
            _sig("pagina_procedimento", Status.partial, 5),# 2.5
            _sig("conteudo_perguntas", Status.fail, 5),    # 0
        ]),
    })
    score_report(report)
    cats = report.categorias
    assert cats["busca_tradicional"].sinais[0].pontos == 6.25
    assert cats["busca_tradicional"].score == 6.25
    assert cats["site_conteudo"].score == 12.5
    assert report.score.total == 18.75
    assert report.score.categorias["site_conteudo"].score == 12.5
    assert report.score.tier == "Bronze"

def test_tier_bands():
    assert tier_for(0) == "Bronze"
    assert tier_for(39) == "Bronze"
    assert tier_for(40) == "Prata"
    assert tier_for(69) == "Prata"
    assert tier_for(70) == "Ouro"
    assert tier_for(100) == "Ouro"
