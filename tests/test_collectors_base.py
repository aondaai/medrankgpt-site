from visibility.collectors.base import SignalResult, CollectorContext, CollectorOutput
from visibility.models import Status, DoctorMeta

def _ctx():
    return CollectorContext(
        doctor=DoctorMeta(nome="Dra. Fulana", especialidade_principal="Dermatologia",
                          cidade="São Paulo", uf="SP", site="https://drafulana.com.br"),
        now="2026-06-28T14:00:00Z", regiao_busca="São Paulo, SP")

def test_signal_result_to_sinal():
    ctx = _ctx()
    res = SignalResult(
        id="google_marca", label="Aparece no Google", status=Status.fail, valor=False,
        weight=12.5, confianca=0.9, metodo="serp_scrape", observacao="nada",
        evidencia=[{"fonte": "google_search", "resumo": "0 no top 10"}])
    sinal = res.to_sinal(ctx)
    assert sinal.id == "google_marca"
    assert sinal.evidencia[0].capturado_em == "2026-06-28T14:00:00Z"  # clock injected
    assert sinal.evidencia[0].fonte == "google_search"

def test_collector_output_defaults():
    out = CollectorOutput(signals=[])
    assert out.prompts == []
