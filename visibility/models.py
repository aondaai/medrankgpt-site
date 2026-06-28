from __future__ import annotations
from enum import Enum
from typing import Literal, Union
from pydantic import BaseModel, Field

class Status(str, Enum):
    pass_ = "pass"
    partial = "partial"
    fail = "fail"
    unknown = "unknown"

Tier = Literal["Bronze", "Prata", "Ouro"]
Engine = Literal["chatgpt", "gemini", "perplexity", "google_ai"]
PromptTipo = Literal["marca", "especialidade", "procedimento"]

class Evidencia(BaseModel):
    fonte: str
    url: str | None = None
    query: str | None = None
    capturado_em: str
    resumo: str
    raw: Union[str, dict, None] = None

class Sinal(BaseModel):
    id: str
    label: str
    status: Status
    valor: Union[bool, float, str]
    weight: float
    pontos: float = 0.0
    confianca: float = Field(ge=0.0, le=1.0)
    metodo: str
    observacao: str | None = None
    evidencia: list[Evidencia] = Field(default_factory=list)

class Categoria(BaseModel):
    label: str
    score: float = 0.0
    max: float
    weight: float
    sinais: list[Sinal]

class CategoriaScore(BaseModel):
    score: float
    max: float

class Score(BaseModel):
    total: float
    max: float = 100
    tier: Tier
    categorias: dict[str, CategoriaScore]

class DoctorMeta(BaseModel):
    nome: str
    crm: str | None = None
    rqe: str | None = None
    especialidade_principal: str
    especialidades: list[str] = Field(default_factory=list)
    procedimentos_foco: list[str] = Field(default_factory=list)
    cidade: str
    uf: str
    site: str | None = None
    perfil_google: str | None = None

class RunMeta(BaseModel):
    gerado_em: str
    pipeline_version: str
    idioma: str = "pt-BR"
    regiao_busca: str | None = None

class Meta(BaseModel):
    doctor: DoctorMeta
    run: RunMeta

class Ofensor(BaseModel):
    nome: str
    aparicoes: int
    especialidade: str | None = None
    fonte_citada: str | None = None

class Concorrentes(BaseModel):
    resumo: str
    ofensores_recorrentes: list[Ofensor] = Field(default_factory=list)

class PromptIA(BaseModel):
    id: str
    prompt: str
    tipo: PromptTipo
    engine: Engine
    regiao: str | None = None
    medico_citado: bool
    posicao: int | None = None
    concorrentes_citados: list[str] = Field(default_factory=list)
    capturado_em: str | None = None
    raw_resposta: str | None = None

class VisibilityReport(BaseModel):
    schema_version: str = "1.0"
    meta: Meta
    score: Score
    categorias: dict[str, Categoria]
    concorrentes: Concorrentes
    prompts_ia: list[PromptIA] = Field(default_factory=list)
