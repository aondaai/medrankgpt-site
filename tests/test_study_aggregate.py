from visibility.study.demand import DemandResponse
from visibility.study.aggregate import aggregate_demand, DemandAggregate

def _r(esp, cidade, tipo, engine, texto, rep=1, proc=None):
    return DemandResponse(esp, cidade, tipo, proc, engine, rep,
                          "2026-06-28T14:00:00Z", texto)

def test_demand_pcts_e_contagens():
    res = [
        _r("Dermatologia", "SP", "melhor_especialista", "chatgpt", "Recomendo a Dra. Ana Lima."),
        _r("Dermatologia", "SP", "melhor_especialista", "gemini", "Busque no Doctoralia."),
        _r("Dermatologia", "SP", "melhor_especialista", "perplexity",
           "Não tenho informações para recomendar."),
    ]
    agg = aggregate_demand(res)
    assert isinstance(agg, DemandAggregate)
    assert agg.total_respostas == 3
    assert round(agg.pct_com_medico_nominal, 3) == round(1/3, 3)
    assert round(agg.pct_marketplace, 3) == round(1/3, 3)
    assert round(agg.pct_nenhum, 3) == round(1/3, 3)

def test_demand_top_medicos_e_marketplaces():
    res = [
        _r("Dermatologia", "SP", "melhor_especialista", "chatgpt", "Indico a Dra. Ana Lima."),
        _r("Dermatologia", "RJ", "melhor_especialista", "chatgpt", "Indico a Dra. Ana Lima."),
        _r("Dermatologia", "SP", "melhor_especialista", "gemini", "Veja no Doctoralia."),
    ]
    agg = aggregate_demand(res)
    assert agg.top_medicos[0] == ["Dra. Ana Lima", 2]
    assert ["doctoralia", 1] in agg.top_marketplaces

def test_demand_por_especialidade():
    res = [
        _r("Dermatologia", "SP", "melhor_especialista", "chatgpt", "Dra. Ana Lima."),
        _r("Oftalmologia", "SP", "melhor_especialista", "chatgpt", "Busque no Doctoralia."),
    ]
    agg = aggregate_demand(res)
    assert agg.por_especialidade["Dermatologia"]["pct_com_medico_nominal"] == 1.0
    assert agg.por_especialidade["Oftalmologia"]["pct_com_medico_nominal"] == 0.0

def test_demand_cfm_risco_pct():
    res = [
        _r("Dermatologia", "SP", "melhor_especialista", "chatgpt",
           "A Dra. Ana garante resultado garantido."),
        _r("Dermatologia", "SP", "melhor_especialista", "gemini", "Dra. Bia Costa atende lá."),
    ]
    agg = aggregate_demand(res)
    assert round(agg.cfm_risco_pct, 3) == 0.5

def test_demand_divergencia_motores():
    # mesma célula (esp/cidade/tipo), motores nomeiam médicos diferentes -> divergência
    res = [
        _r("Dermatologia", "SP", "melhor_especialista", "chatgpt", "Dra. Ana Lima."),
        _r("Dermatologia", "SP", "melhor_especialista", "gemini", "Dr. Bruno Souza."),
    ]
    agg = aggregate_demand(res)
    assert agg.divergencia_motores_pct == 1.0

from visibility.study.aggregate import aggregate_supply, SupplyAggregate
from visibility.models import (
    VisibilityReport, Meta, RunMeta, DoctorMeta, Score, CategoriaScore)

def _report(total, cats):
    doc = DoctorMeta(nome="X", especialidade_principal="Dermatologia",
                     cidade="SP", uf="SP")
    return VisibilityReport(
        meta=Meta(doctor=doc, run=RunMeta(gerado_em="t", pipeline_version="0.1.0")),
        score=Score(total=total, max=100,
                    tier="Ouro" if total >= 70 else "Prata" if total >= 40 else "Bronze",
                    categorias={k: CategoriaScore(score=v, max=25) for k, v in cats.items()}),
        categorias={}, concorrentes={"resumo": "", "ofensores_recorrentes": []})

def test_supply_distribuicao():
    reports = {"Dermatologia": [
        _report(20, {"visibilidade_ia": 5}),
        _report(40, {"visibilidade_ia": 10}),
        _report(60, {"visibilidade_ia": 20}),
        _report(80, {"visibilidade_ia": 25}),
    ]}
    agg = aggregate_supply(reports)
    assert isinstance(agg, SupplyAggregate)
    d = agg.por_especialidade["Dermatologia"]
    assert d["n"] == 4
    assert d["mediana"] == 50.0
    assert d["pct_abaixo_50"] == 0.5
    assert d["media_por_categoria"]["visibilidade_ia"] == 15.0

def test_supply_top_decil_profile():
    reports = {"Dermatologia": [_report(10 * i, {"visibilidade_ia": float(i)})
                                for i in range(1, 11)]}  # 10..100
    agg = aggregate_supply(reports)
    d = agg.por_especialidade["Dermatologia"]
    # top 10% = 1 médico (o de score 100), media_por_categoria do topo destaca-se
    assert d["top_decil"]["n"] >= 1
    assert d["top_decil"]["media_por_categoria"]["visibilidade_ia"] >= d["media_por_categoria"]["visibilidade_ia"]

def test_demand_divergencia_ignora_concordancia_em_nenhum():
    # ambos os motores não nomeiam médico (marketplace) -> CONCORDAM -> não diverge
    res = [
        _r("Dermatologia", "SP", "melhor_especialista", "chatgpt", "Busque no Doctoralia."),
        _r("Dermatologia", "SP", "melhor_especialista", "gemini", "Busque no BoaConsulta."),
    ]
    agg = aggregate_demand(res)
    assert agg.divergencia_motores_pct == 0.0

def test_demand_divergencia_usa_moda_das_repeticoes():
    # chatgpt: Ana (2x) e Bruno (1x) -> moda Ana; gemini: Ana (1x) -> concordam -> 0
    res = [
        _r("Dermatologia", "SP", "melhor_especialista", "chatgpt", "Dra. Ana Lima.", rep=1),
        _r("Dermatologia", "SP", "melhor_especialista", "chatgpt", "Dra. Ana Lima.", rep=2),
        _r("Dermatologia", "SP", "melhor_especialista", "chatgpt", "Dr. Bruno Souza.", rep=3),
        _r("Dermatologia", "SP", "melhor_especialista", "gemini", "Dra. Ana Lima.", rep=1),
    ]
    agg = aggregate_demand(res)
    assert agg.divergencia_motores_pct == 0.0

def test_demand_divergencia_nomeia_vs_ninguem():
    # chatgpt nomeia, gemini não -> divergem
    res = [
        _r("Dermatologia", "SP", "melhor_especialista", "chatgpt", "Dra. Ana Lima."),
        _r("Dermatologia", "SP", "melhor_especialista", "gemini", "Busque no Doctoralia."),
    ]
    agg = aggregate_demand(res)
    assert agg.divergencia_motores_pct == 1.0
