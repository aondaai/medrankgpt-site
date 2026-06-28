from visibility.models import PromptIA
from visibility.competitors import build_concorrentes

def _p(id_, cited, comps):
    return PromptIA(id=id_, prompt="q", tipo="procedimento", engine="chatgpt",
                    medico_citado=cited, concorrentes_citados=comps)

def test_aggregates_offenders():
    log = [
        _p("p1", False, ["Dr. X", "Dra. Y"]),
        _p("p2", False, ["Dr. X"]),
        _p("p3", True,  ["Dr. X"]),   # doctor cited here → ignore
    ]
    c = build_concorrentes(log)
    names = [o.nome for o in c.ofensores_recorrentes]
    assert names[0] == "Dr. X"               # 2 appearances, ranked first
    assert c.ofensores_recorrentes[0].aparicoes == 2
    assert "2 de 3" in c.resumo or "2/3" in c.resumo

def test_empty_log():
    c = build_concorrentes([])
    assert c.ofensores_recorrentes == []
