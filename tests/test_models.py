from visibility.models import (
    Evidencia, Sinal, Categoria, CategoriaScore, Score, DoctorMeta, RunMeta,
    Meta, Ofensor, Concorrentes, PromptIA, VisibilityReport, Status,
)

def _sinal(id_="google_marca", status=Status.fail, weight=12.5):
    return Sinal(
        id=id_, label="x", status=status, valor=False, weight=weight, pontos=0.0,
        confianca=0.9, metodo="serp_scrape",
        evidencia=[Evidencia(fonte="google_search", capturado_em="2026-06-28T14:00:00Z",
                             resumo="nada")],
    )

def test_report_round_trips_to_dict():
    report = VisibilityReport(
        schema_version="1.0",
        meta=Meta(
            doctor=DoctorMeta(nome="Dra. Fulana", especialidade_principal="Dermatologia",
                              cidade="São Paulo", uf="SP"),
            run=RunMeta(gerado_em="2026-06-28T14:00:00Z", pipeline_version="0.1.0"),
        ),
        score=Score(total=0, max=100, tier="Bronze",
                    categorias={"busca_tradicional": CategoriaScore(score=0, max=25)}),
        categorias={"busca_tradicional": Categoria(
            label="Busca tradicional", score=0, max=25, weight=25, sinais=[_sinal()])},
        concorrentes=Concorrentes(resumo="r", ofensores_recorrentes=[
            Ofensor(nome="Dr. X", aparicoes=6)]),
        prompts_ia=[PromptIA(id="p1", prompt="q", tipo="procedimento", engine="chatgpt",
                             medico_citado=False)],
    )
    data = report.model_dump(mode="json", exclude_none=True)
    assert data["categorias"]["busca_tradicional"]["sinais"][0]["id"] == "google_marca"
    assert VisibilityReport.model_validate(data).score.tier == "Bronze"
