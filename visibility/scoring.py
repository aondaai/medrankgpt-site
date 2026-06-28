from __future__ import annotations
from visibility.models import VisibilityReport, Categoria, Sinal, Status, CategoriaScore, Tier

_POINTS = {Status.pass_: 1.0, Status.partial: 0.5, Status.fail: 0.0, Status.unknown: 0.0}

def points_for(sinal: Sinal) -> float:
    return round(sinal.weight * _POINTS[sinal.status], 4)

def tier_for(total: float) -> Tier:
    if total >= 70:
        return "Ouro"
    if total >= 40:
        return "Prata"
    return "Bronze"

def score_category(cat: Categoria) -> float:
    for s in cat.sinais:
        s.pontos = points_for(s)
    cat.score = round(sum(s.pontos for s in cat.sinais), 4)
    return cat.score

def score_report(report: VisibilityReport) -> VisibilityReport:
    cat_scores: dict[str, CategoriaScore] = {}
    total = 0.0
    for key, cat in report.categorias.items():
        score_category(cat)
        cat_scores[key] = CategoriaScore(score=cat.score, max=cat.max)
        total += cat.score
    total = round(total, 4)
    report.score.total = total
    report.score.max = 100
    report.score.tier = tier_for(total)
    report.score.categorias = cat_scores
    return report
