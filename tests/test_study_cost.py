from visibility.study.config import DemandMatrix
from visibility.study.cost import estimate_demand_calls, estimate_supply_calls, estimate_cost

def _matrix():
    return DemandMatrix(
        especialidades=["Dermatologia"], cidades=["SP", "RJ"],
        procedimentos={"Dermatologia": ["botox", "acne"]},
        prompt_tipos=["melhor_especialista", "procedimento"],
        engines=["chatgpt", "gemini"], repeticoes=3)

def test_demand_calls():
    # prompts: 1 esp × 2 cidades × (1 melhor + 2 procedimentos) = 6 prompts
    # chamadas: 6 × 2 engines × 3 reps = 36
    assert estimate_demand_calls(_matrix()) == 36

def test_supply_calls_usa_premissas():
    # 50 médicos, 4 procedimentos médios, 2 motores -> por médico:
    # (1 marca + 4 proc) × 2 motores = 10 chamadas LLM + 1 serp + 1 places = 12
    calls = estimate_supply_calls(n_medicos=50, media_procedimentos=4, n_motores=2)
    assert calls["llm"] == 50 * 10
    assert calls["serpapi"] == 50
    assert calls["places"] == 50

def test_estimate_cost_soma_em_usd():
    custo = estimate_cost(llm=100, serpapi=50, places=50)
    # constantes default: llm 0.02, serpapi 0.01, places 0.005
    assert round(custo, 4) == round(100 * 0.02 + 50 * 0.01 + 50 * 0.005, 4)
