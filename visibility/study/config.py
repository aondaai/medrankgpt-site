from __future__ import annotations
import json
from dataclasses import dataclass, field

# Templates dos prompts "de paciente". Placeholders: {especialidade}, {cidade}, {procedimento}.
PROMPT_TEMPLATES: dict[str, str] = {
    "melhor_especialista": "Quem é o melhor médico de {especialidade} em {cidade}?",
    "procedimento": "Quem faz {procedimento} em {cidade}?",
    "confianca": "Indique um(a) médico(a) de {especialidade} de confiança em {cidade}.",
}

@dataclass
class DemandMatrix:
    especialidades: list[str]
    cidades: list[str]
    procedimentos: dict[str, list[str]]   # especialidade -> lista de procedimentos
    prompt_tipos: list[str]               # chaves de PROMPT_TEMPLATES
    engines: list[str]                    # subconjunto de Engine (chatgpt/gemini/perplexity/google_ai)
    repeticoes: int = 1

    @classmethod
    def from_dict(cls, d: dict) -> "DemandMatrix":
        return cls(
            especialidades=list(d["especialidades"]),
            cidades=list(d["cidades"]),
            procedimentos={k: list(v) for k, v in d.get("procedimentos", {}).items()},
            prompt_tipos=list(d["prompt_tipos"]),
            engines=list(d["engines"]),
            repeticoes=int(d.get("repeticoes", 1)),
        )

@dataclass
class RosterSpec:
    especialidade: str
    arquivo: str   # caminho de um JSON: lista de dicts DoctorMeta

    @classmethod
    def from_dict(cls, d: dict) -> "RosterSpec":
        return cls(especialidade=d["especialidade"], arquivo=d["arquivo"])

@dataclass
class StudyConfig:
    demand: DemandMatrix
    rosters: list[RosterSpec] = field(default_factory=list)

    @classmethod
    def from_dict(cls, d: dict) -> "StudyConfig":
        return cls(
            demand=DemandMatrix.from_dict(d["demand"]),
            rosters=[RosterSpec.from_dict(r) for r in d.get("rosters", [])],
        )

    @classmethod
    def from_file(cls, path: str) -> "StudyConfig":
        with open(path, encoding="utf-8") as fh:
            return cls.from_dict(json.load(fh))
