from __future__ import annotations
import json
import importlib.resources as resources
from functools import lru_cache
from jsonschema import Draft202012Validator


class SchemaValidationError(ValueError):
    pass


@lru_cache(maxsize=1)
def _validator() -> Draft202012Validator:
    text = resources.files("visibility.schema").joinpath("ai_visibility_score_1_0.json").read_text()
    return Draft202012Validator(json.loads(text))


def validate_report(data: dict) -> None:
    errors = sorted(_validator().iter_errors(data), key=lambda e: e.path)
    if errors:
        first = errors[0]
        loc = "/".join(str(p) for p in first.path) or "<root>"
        raise SchemaValidationError(f"{loc}: {first.message}")
