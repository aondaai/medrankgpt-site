from visibility.study.config import DemandMatrix
from visibility.study.demand import build_demand_prompts, DemandPrompt

def _matrix(**kw):
    base = dict(especialidades=["Dermatologia"], cidades=["São Paulo"],
                procedimentos={"Dermatologia": ["botox", "acne"]},
                prompt_tipos=["melhor_especialista", "procedimento"],
                engines=["chatgpt"], repeticoes=1)
    base.update(kw)
    return DemandMatrix(**base)

def test_builds_one_prompt_per_non_procedure_tipo():
    prompts = build_demand_prompts(_matrix(prompt_tipos=["melhor_especialista"]))
    assert len(prompts) == 1
    p = prompts[0]
    assert isinstance(p, DemandPrompt)
    assert p.tipo == "melhor_especialista" and p.procedimento is None
    assert p.texto == "Quem é o melhor médico de Dermatologia em São Paulo?"

def test_procedure_tipo_expands_over_procedimentos():
    prompts = build_demand_prompts(_matrix(prompt_tipos=["procedimento"]))
    procs = sorted(p.procedimento for p in prompts)
    assert procs == ["acne", "botox"]
    assert all(p.tipo == "procedimento" for p in prompts)
    botox = next(p for p in prompts if p.procedimento == "botox")
    assert botox.texto == "Quem faz botox em São Paulo?"

def test_full_cartesian_product():
    m = _matrix(especialidades=["Dermatologia", "Oftalmologia"],
                cidades=["São Paulo", "Rio de Janeiro"],
                procedimentos={"Dermatologia": ["botox"], "Oftalmologia": ["lasik"]},
                prompt_tipos=["melhor_especialista", "procedimento"])
    # 2 esp × 2 cidades × (1 melhor + 1 procedimento por esp) = 8
    assert len(build_demand_prompts(m)) == 8

from visibility.study.demand import DemandResponse, DemandRunner

class ScriptedLLM:
    """Resposta canônica por substring do prompt."""
    def __init__(self, name, answers): self.name = name; self.answers = answers
    def ask(self, prompt: str) -> str:
        for needle, ans in self.answers.items():
            if needle in prompt:
                return ans
        return "Não tenho informação."

def test_runner_one_response_per_prompt_engine_rep():
    prompts = build_demand_prompts(_matrix(prompt_tipos=["melhor_especialista"]))
    engines = {"chatgpt": ScriptedLLM("chatgpt", {"melhor": "R1"}),
               "gemini": ScriptedLLM("gemini", {"melhor": "R2"})}
    runner = DemandRunner(engines=engines, repeticoes=2)
    res = runner.run(prompts, now="2026-06-28T14:00:00Z")
    # 1 prompt × 2 engines × 2 reps
    assert len(res) == 4
    assert {r.engine for r in res} == {"chatgpt", "gemini"}
    assert {r.rep for r in res} == {1, 2}
    r0 = res[0]
    assert isinstance(r0, DemandResponse)
    assert r0.capturado_em == "2026-06-28T14:00:00Z"
    assert r0.especialidade == "Dermatologia" and r0.cidade == "São Paulo"

def test_runner_passes_prompt_text_to_client():
    prompts = build_demand_prompts(_matrix(prompt_tipos=["procedimento"]))
    engines = {"chatgpt": ScriptedLLM("chatgpt",
               {"botox": "indico a Dra. A", "acne": "indico o Dr. B"})}
    res = DemandRunner(engines=engines).run(prompts, now="2026-06-28T14:00:00Z")
    botox = next(r for r in res if r.procedimento == "botox")
    assert botox.texto == "indico a Dra. A"
