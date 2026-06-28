from visibility.collectors.base import CollectorContext
from visibility.collectors.ai_engines import AiEnginesCollector, build_prompts
from visibility.models import DoctorMeta, Status

class ScriptedLLM:
    """Returns a canned answer per (engine, prompt-substring)."""
    def __init__(self, name, answers): self.name = name; self.answers = answers
    def ask(self, prompt: str) -> str:
        for needle, ans in self.answers.items():
            if needle in prompt:
                return ans
        return "Não tenho informação."

def _ctx():
    return CollectorContext(
        doctor=DoctorMeta(nome="Dra. Fulana de Tal", especialidade_principal="Dermatologia",
                          cidade="São Paulo", uf="SP", procedimentos_foco=["botox", "acne"]),
        now="2026-06-28T14:00:00Z", regiao_busca="São Paulo, SP")

def test_prompts_built():
    prompts = build_prompts(_ctx().doctor, _ctx().regiao_busca)
    tipos = {p["tipo"] for p in prompts}
    assert "marca" in tipos and "procedimento" in tipos
    assert sum(p["tipo"] == "procedimento" for p in prompts) == 2  # botox, acne

def test_signals_and_log():
    # chatgpt cites her for botox only; never by brand
    engine = ScriptedLLM("chatgpt", {
        "botox": "Recomendo a Dra. Fulana de Tal e o Dr. Outro.",
        "acne": "Recomendo o Dr. Concorrente.",
    })
    out = AiEnginesCollector(engines={"chatgpt": engine}).collect(_ctx())
    sig = {s.id: s for s in out.signals}
    assert sig["ia_marca"].status == Status.fail
    assert sig["ia_procedimento"].status == Status.partial   # botox yes, acne no
    # one marca prompt + two procedure prompts = 3 log entries
    assert len(out.prompts) == 3
    botox_log = next(p for p in out.prompts if "botox" in p.prompt)
    assert botox_log.medico_citado is True
    assert botox_log.engine == "chatgpt"
    # competitors are extracted from the answer, excluding the doctor herself
    assert "Dr. Outro" in botox_log.concorrentes_citados
    assert "Dra. Fulana de Tal" not in botox_log.concorrentes_citados
    acne_log = next(p for p in out.prompts if "acne" in p.prompt)
    assert acne_log.concorrentes_citados == ["Dr. Concorrente"]

def test_extract_competitors_excludes_self():
    from visibility.collectors.ai_engines import extract_competitors
    ans = "Recomendo a Dra. Fulana de Tal e também o Dr. João Silva e a Dra. Ana."
    comps = extract_competitors(ans, "Dra. Fulana de Tal")
    assert "Dr. João Silva" in comps
    assert "Dra. Ana" in comps
    assert all("Fulana" not in c for c in comps)


def test_cited_does_not_fire_across_different_names():
    from visibility.collectors.ai_engines import _cited
    # 'Ana Silva' must not be considered cited just because 'Ana Costa' and
    # 'Bruno Silva' each share one token with her.
    assert _cited("Recomendo a Dra. Ana Costa e o Dr. Bruno Silva.",
                  "Dra. Ana Silva") is False


def test_extract_competitors_keeps_same_first_name_doctor():
    from visibility.collectors.ai_engines import extract_competitors
    # 'Dr. João Pedro Costa' shares only 'joao' with 'Dra. Maria João Silva'
    # → different person → kept as a competitor.
    comps = extract_competitors("Quem indica? O Dr. João Pedro Costa.",
                                "Dra. Maria João Silva")
    assert "Dr. João Pedro Costa" in comps
