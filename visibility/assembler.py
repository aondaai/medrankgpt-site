from __future__ import annotations
from visibility.collectors.base import Collector, CollectorContext
from visibility.competitors import build_concorrentes
from visibility.scoring import score_report
from visibility.models import (
    VisibilityReport, Meta, RunMeta, DoctorMeta, Categoria, Score, PromptIA,
)

CATEGORY_LABELS = {
    "busca_tradicional": "Busca tradicional",
    "plataformas_medicas": "Plataformas médicas",
    "visibilidade_ia": "Visibilidade em IA",
    "site_conteudo": "Site / E-E-A-T técnico",
}
CATEGORY_MAX = 25.0

def assemble_report(doctor: DoctorMeta, collectors: list[Collector], *, now: str,
                    pipeline_version: str, regiao_busca: str | None = None) -> VisibilityReport:
    ctx = CollectorContext(doctor=doctor, now=now, regiao_busca=regiao_busca)
    grouped: dict[str, list] = {}
    prompts: list[PromptIA] = []
    for collector in collectors:
        out = collector.collect(ctx)
        grouped.setdefault(collector.category, []).extend(s.to_sinal(ctx) for s in out.signals)
        prompts.extend(out.prompts)

    categorias = {
        key: Categoria(label=CATEGORY_LABELS.get(key, key), max=CATEGORY_MAX,
                       weight=CATEGORY_MAX, sinais=sinais)
        for key, sinais in grouped.items()
    }
    report = VisibilityReport(
        meta=Meta(doctor=doctor,
                  run=RunMeta(gerado_em=now, pipeline_version=pipeline_version,
                              regiao_busca=regiao_busca)),
        score=Score(total=0, max=100, tier="Bronze", categorias={}),
        categorias=categorias,
        concorrentes=build_concorrentes(prompts),
        prompts_ia=prompts,
    )
    return score_report(report)
