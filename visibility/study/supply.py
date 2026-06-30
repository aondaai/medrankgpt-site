from __future__ import annotations
import json
from typing import Callable
from visibility.assembler import assemble_report
from visibility.models import DoctorMeta, VisibilityReport
from visibility.study.config import RosterSpec

def load_roster(path: str) -> list[DoctorMeta]:
    with open(path, encoding="utf-8") as fh:
        return [DoctorMeta.model_validate(d) for d in json.load(fh)]

def run_supply(rosters: list[RosterSpec], collector_factory: Callable[[object], list],
               settings: object, *, now: str, pipeline_version: str
               ) -> dict[str, list[VisibilityReport]]:
    out: dict[str, list[VisibilityReport]] = {}
    for spec in rosters:
        reports: list[VisibilityReport] = []
        for doc in load_roster(spec.arquivo):
            collectors = collector_factory(settings)
            regiao = f"{doc.cidade}, {doc.uf}"
            reports.append(assemble_report(
                doc, collectors, now=now, pipeline_version=pipeline_version,
                regiao_busca=regiao))
        out[spec.especialidade] = reports
    return out
