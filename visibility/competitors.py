from __future__ import annotations
from collections import Counter
from visibility.models import PromptIA, Concorrentes, Ofensor

def build_concorrentes(prompts: list[PromptIA]) -> Concorrentes:
    counter: Counter[str] = Counter()
    for p in prompts:
        if p.medico_citado:
            continue
        for name in p.concorrentes_citados:
            counter[name] += 1
    ofensores = [Ofensor(nome=n, aparicoes=c)
                 for n, c in counter.most_common()]
    total = len(prompts)
    not_cited = sum(1 for p in prompts if not p.medico_citado)
    if total and ofensores:
        resumo = (f"Em {not_cited} de {total} prompts, a IA cita concorrentes — "
                  f"não o médico. Mais recorrente: {ofensores[0].nome} "
                  f"({ofensores[0].aparicoes}x).")
    elif total:
        resumo = f"Em {total} prompts, nenhum concorrente recorrente foi citado."
    else:
        resumo = "Nenhum prompt de IA executado."
    return Concorrentes(resumo=resumo, ofensores_recorrentes=ofensores)
