from __future__ import annotations
import json
import importlib.resources as resources
from dataclasses import asdict
from functools import lru_cache
from jsonschema import Draft202012Validator
from visibility.study.aggregate import DemandAggregate, SupplyAggregate

class SchemaValidationError(ValueError):
    pass

@lru_cache(maxsize=1)
def _validator() -> Draft202012Validator:
    text = resources.files("visibility.study.schema").joinpath(
        "study_aggregates_1_0.json").read_text()
    return Draft202012Validator(json.loads(text))

def build_aggregates(demand: DemandAggregate, supply: SupplyAggregate, *,
                     now: str, pipeline_version: str) -> dict:
    return {
        "schema_version": "1.0",
        "meta": {"gerado_em": now, "pipeline_version": pipeline_version, "idioma": "pt-BR"},
        "demanda": asdict(demand),
        "oferta": asdict(supply),
    }

def validate_aggregates(data: dict) -> None:
    errors = sorted(_validator().iter_errors(data), key=lambda e: list(e.path))
    if errors:
        first = errors[0]
        loc = "/".join(str(p) for p in first.path) or "<root>"
        raise SchemaValidationError(f"{loc}: {first.message}")
