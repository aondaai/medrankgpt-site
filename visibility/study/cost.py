from __future__ import annotations
from visibility.study.config import DemandMatrix
from visibility.study.demand import build_demand_prompts

# Preços aproximados por chamada, em USD. Ajustar num só lugar conforme contratos reais.
CUSTO_LLM = 0.02
CUSTO_SERPAPI = 0.01
CUSTO_PLACES = 0.005

def estimate_demand_calls(m: DemandMatrix) -> int:
    return len(build_demand_prompts(m)) * len(m.engines) * m.repeticoes

def estimate_supply_calls(n_medicos: int, media_procedimentos: int, n_motores: int
                          ) -> dict[str, int]:
    llm_por_medico = (1 + media_procedimentos) * n_motores   # 1 prompt de marca + procedimentos
    return {"llm": n_medicos * llm_por_medico,
            "serpapi": n_medicos, "places": n_medicos}

def estimate_cost(llm: int = 0, serpapi: int = 0, places: int = 0) -> float:
    return llm * CUSTO_LLM + serpapi * CUSTO_SERPAPI + places * CUSTO_PLACES
