# AI Visibility Score Pipeline — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Python pipeline that, given a doctor's identity, runs all visibility checks (Google, Maps, medical platforms, AI engines, site/E-E-A-T), scores them 0–100 across 4 categories, and emits a JSON report that validates against the AI Visibility Score schema.

**Architecture:** A package of independent **collectors** (one per data source), each implementing a common `Collector` protocol and returning `SignalResult`s. External I/O (search, maps, LLMs, HTTP) sits behind injectable **client protocols** so collectors are unit-tested against recorded fixtures. An **assembler** runs the collectors, a **scoring** module fills points/tiers, a **competitors** module aggregates the AI-prompt log, and a **CLI** wires real clients together and validates output against the canonical JSON Schema.

**Tech Stack:** Python 3.11+, pydantic v2 (models), httpx (HTTP), BeautifulSoup4 + extruct (site/schema parsing), jsonschema (contract validation), pytest + respx (tests).

**Spec:** [docs/superpowers/specs/2026-06-28-ai-visibility-score-index-design.md](../specs/2026-06-28-ai-visibility-score-index-design.md)

---

## Prerequisites (live-run only — not needed to build/test)

Environment variables, read by `visibility/config.py`:

| Var | Used by | Notes |
|---|---|---|
| `SERPAPI_KEY` | google_search | SerpAPI (or compatible) JSON SERP |
| `GOOGLE_PLACES_KEY` | google_maps | Google Places Text Search API |
| `OPENAI_API_KEY` | ai_engines (chatgpt) | OpenAI chat completions |
| `PERPLEXITY_API_KEY` | ai_engines (perplexity) | OpenAI-compatible endpoint |
| `GEMINI_API_KEY` | ai_engines (gemini, google_ai) | Google Generative Language API |

All tests mock these — the build is green with no keys set.

---

## File Structure

```
pyproject.toml                          # package + deps + pytest config
visibility/
  __init__.py
  models.py                             # pydantic models = the schema in code
  schema/ai_visibility_score_1_0.json   # canonical JSON Schema (spec §9)
  validation.py                         # validate a report dict against the schema
  scoring.py                            # status→points, category sums, total, tier
  clients.py                            # client protocols + concrete HTTP/LLM clients
  collectors/
    __init__.py
    base.py                             # SignalResult, CollectorContext, Collector protocol
    site_analysis.py                    # 5 site/E-E-A-T signals
    google_search.py                    # google_marca
    google_maps.py                      # google_maps
    medical_platforms.py               # doctoralia, boaconsulta
    ai_engines.py                       # ia_marca, ia_procedimento + prompts_ia log
  competitors.py                        # concorrentes from prompts_ia
  assembler.py                          # orchestrate collectors → VisibilityReport
  config.py                            # env settings + real-client factory
  cli.py                               # entrypoint: doctor input → validated report JSON
tests/
  fixtures/                             # recorded HTML/JSON used by collector tests
  test_models.py
  test_validation.py
  test_scoring.py
  test_collectors_base.py
  test_site_analysis.py
  test_google_search.py
  test_google_maps.py
  test_medical_platforms.py
  test_ai_engines.py
  test_competitors.py
  test_assembler.py
  test_cli.py
```

**Decomposition rationale:** one file per collector (they change for independent reasons — a Doctoralia HTML change must not touch SERP logic). Clients are isolated so collectors hold only parsing/decision logic. Scoring, validation, and aggregation are pure functions over the models — trivially testable.

---

## Task 1: Package scaffold

**Files:**
- Create: `pyproject.toml`
- Create: `visibility/__init__.py`
- Create: `tests/__init__.py`
- Test: `tests/test_smoke.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_smoke.py
def test_package_imports():
    import visibility
    assert visibility.__version__ == "0.1.0"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_smoke.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'visibility'`

- [ ] **Step 3: Create the package and config**

```toml
# pyproject.toml
[project]
name = "medrank-visibility"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
  "pydantic>=2.6",
  "httpx>=0.27",
  "beautifulsoup4>=4.12",
  "extruct>=0.16",
  "jsonschema>=4.21",
]

[project.optional-dependencies]
dev = ["pytest>=8.0", "respx>=0.21"]

[project.scripts]
medrank-visibility = "visibility.cli:main"

[tool.pytest.ini_options]
testpaths = ["tests"]
```

```python
# visibility/__init__.py
__version__ = "0.1.0"
```

```python
# tests/__init__.py
```

- [ ] **Step 4: Install and run the test to verify it passes**

Run: `pip install -e ".[dev]" && pytest tests/test_smoke.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml visibility/__init__.py tests/__init__.py tests/test_smoke.py
git commit -m "chore: scaffold medrank-visibility package"
```

---

## Task 2: Data model (pydantic)

**Files:**
- Create: `visibility/models.py`
- Test: `tests/test_models.py`

The models mirror the spec exactly. `Status` and tiers are enums; `Sinal.pontos`/`Categoria.score`/`Score.total` start at 0 and are filled by the scoring module.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_models.py
from visibility.models import (
    Evidencia, Sinal, Categoria, CategoriaScore, Score, DoctorMeta, RunMeta,
    Meta, Ofensor, Concorrentes, PromptIA, VisibilityReport, Status,
)

def _sinal(id_="google_marca", status=Status.fail, weight=12.5):
    return Sinal(
        id=id_, label="x", status=status, valor=False, weight=weight, pontos=0.0,
        confianca=0.9, metodo="serp_scrape",
        evidencia=[Evidencia(fonte="google_search", capturado_em="2026-06-28T14:00:00Z",
                             resumo="nada")],
    )

def test_report_round_trips_to_dict():
    report = VisibilityReport(
        schema_version="1.0",
        meta=Meta(
            doctor=DoctorMeta(nome="Dra. Fulana", especialidade_principal="Dermatologia",
                              cidade="São Paulo", uf="SP"),
            run=RunMeta(gerado_em="2026-06-28T14:00:00Z", pipeline_version="0.1.0"),
        ),
        score=Score(total=0, max=100, tier="Bronze",
                    categorias={"busca_tradicional": CategoriaScore(score=0, max=25)}),
        categorias={"busca_tradicional": Categoria(
            label="Busca tradicional", score=0, max=25, weight=25, sinais=[_sinal()])},
        concorrentes=Concorrentes(resumo="r", ofensores_recorrentes=[
            Ofensor(nome="Dr. X", aparicoes=6)]),
        prompts_ia=[PromptIA(id="p1", prompt="q", tipo="procedimento", engine="chatgpt",
                             medico_citado=False)],
    )
    data = report.model_dump(mode="json", exclude_none=True)
    assert data["categorias"]["busca_tradicional"]["sinais"][0]["id"] == "google_marca"
    assert VisibilityReport.model_validate(data).score.tier == "Bronze"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_models.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'visibility.models'`

- [ ] **Step 3: Write the models**

```python
# visibility/models.py
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_models.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add visibility/models.py tests/test_models.py
git commit -m "feat: pydantic models for the visibility report"
```

---

## Task 3: Canonical JSON Schema file

**Files:**
- Create: `visibility/schema/ai_visibility_score_1_0.json`
- Create: `visibility/schema/__init__.py`

Copy the schema verbatim from spec §9. No test in this task — Task 4 tests it.

- [ ] **Step 1: Create the schema package marker**

```python
# visibility/schema/__init__.py
```

- [ ] **Step 2: Create the schema file**

Copy the full JSON Schema from the spec (§9, "JSON Schema draft 2020-12") into
`visibility/schema/ai_visibility_score_1_0.json`. It is the block beginning
`{ "$schema": "https://json-schema.org/draft/2020-12/schema", ... }`.

- [ ] **Step 3: Sanity-check it parses**

Run: `python -c "import json,importlib.resources as r; json.loads(r.files('visibility.schema').joinpath('ai_visibility_score_1_0.json').read_text()); print('ok')"`
Expected: prints `ok`

- [ ] **Step 4: Commit**

```bash
git add visibility/schema/
git commit -m "feat: add canonical AI Visibility Score JSON Schema"
```

---

## Task 4: Schema validation

**Files:**
- Create: `visibility/validation.py`
- Test: `tests/test_validation.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_validation.py
import pytest
from visibility.validation import validate_report, SchemaValidationError
from tests.test_models import _sinal  # reuse helper
from visibility.models import (
    VisibilityReport, Meta, DoctorMeta, RunMeta, Score, CategoriaScore,
    Categoria, Concorrentes, Ofensor, PromptIA,
)

def _valid_report() -> VisibilityReport:
    return VisibilityReport(
        meta=Meta(
            doctor=DoctorMeta(nome="Dra. Fulana", especialidade_principal="Dermatologia",
                              cidade="São Paulo", uf="SP"),
            run=RunMeta(gerado_em="2026-06-28T14:00:00Z", pipeline_version="0.1.0")),
        score=Score(total=0, max=100, tier="Bronze",
                    categorias={"busca_tradicional": CategoriaScore(score=0, max=25)}),
        categorias={"busca_tradicional": Categoria(
            label="Busca tradicional", score=0, max=25, weight=25, sinais=[_sinal()])},
        concorrentes=Concorrentes(resumo="r", ofensores_recorrentes=[Ofensor(nome="Dr. X", aparicoes=6)]),
        prompts_ia=[PromptIA(id="p1", prompt="q", tipo="procedimento", engine="chatgpt", medico_citado=False)],
    )

def test_serialized_model_validates_against_schema():
    data = _valid_report().model_dump(mode="json", exclude_none=True)
    validate_report(data)  # must not raise

def test_invalid_report_raises():
    data = _valid_report().model_dump(mode="json", exclude_none=True)
    data["score"]["tier"] = "Platinum"  # not in enum
    with pytest.raises(SchemaValidationError):
        validate_report(data)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_validation.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'visibility.validation'`

- [ ] **Step 3: Write the validator**

```python
# visibility/validation.py
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_validation.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add visibility/validation.py tests/test_validation.py
git commit -m "feat: validate reports against the canonical JSON Schema"
```

---

## Task 5: Scoring engine

**Files:**
- Create: `visibility/scoring.py`
- Test: `tests/test_scoring.py`

Rules (spec §5): pass=weight, partial=weight/2, fail/unknown=0. Category score = sum of signal points. Total = sum of category scores. Tier: 0–39 Bronze, 40–69 Prata, 70–100 Ouro. The function mutates points/scores in place and fills `report.score`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_scoring.py
from visibility.models import (
    VisibilityReport, Meta, DoctorMeta, RunMeta, Score, CategoriaScore,
    Categoria, Sinal, Evidencia, Status, Concorrentes,
)
from visibility.scoring import score_report, tier_for

def _ev():
    return [Evidencia(fonte="x", capturado_em="2026-06-28T14:00:00Z", resumo="r")]

def _sig(id_, status, weight):
    return Sinal(id=id_, label=id_, status=status, valor=True, weight=weight,
                 confianca=1.0, metodo="m", evidencia=_ev())

def _report_with(categorias):
    return VisibilityReport(
        meta=Meta(doctor=DoctorMeta(nome="D", especialidade_principal="X", cidade="C", uf="SP"),
                  run=RunMeta(gerado_em="2026-06-28T14:00:00Z", pipeline_version="0.1.0")),
        score=Score(total=0, tier="Bronze", categorias={}),
        categorias=categorias,
        concorrentes=Concorrentes(resumo="r"),
        prompts_ia=[],
    )

def test_points_and_total():
    report = _report_with({
        "busca_tradicional": Categoria(label="Busca", score=0, max=25, weight=25, sinais=[
            _sig("google_marca", Status.partial, 12.5),  # 6.25
            _sig("google_maps", Status.fail, 12.5),       # 0
        ]),
        "site_conteudo": Categoria(label="Site", score=0, max=25, weight=25, sinais=[
            _sig("crm_rqe_visivel", Status.pass_, 5),      # 5
            _sig("schema_medico", Status.fail, 5),         # 0
            _sig("pagina_especialidade", Status.pass_, 5), # 5
            _sig("pagina_procedimento", Status.partial, 5),# 2.5
            _sig("conteudo_perguntas", Status.fail, 5),    # 0
        ]),
    })
    score_report(report)
    cats = report.categorias
    assert cats["busca_tradicional"].sinais[0].pontos == 6.25
    assert cats["busca_tradicional"].score == 6.25
    assert cats["site_conteudo"].score == 12.5
    assert report.score.total == 18.75
    assert report.score.categorias["site_conteudo"].score == 12.5
    assert report.score.tier == "Bronze"

def test_tier_bands():
    assert tier_for(0) == "Bronze"
    assert tier_for(39) == "Bronze"
    assert tier_for(40) == "Prata"
    assert tier_for(69) == "Prata"
    assert tier_for(70) == "Ouro"
    assert tier_for(100) == "Ouro"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_scoring.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'visibility.scoring'`

- [ ] **Step 3: Write the scoring engine**

```python
# visibility/scoring.py
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_scoring.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add visibility/scoring.py tests/test_scoring.py
git commit -m "feat: scoring engine (points, category sums, total, tier)"
```

---

## Task 6: Collector interface + context

**Files:**
- Create: `visibility/collectors/__init__.py`
- Create: `visibility/collectors/base.py`
- Test: `tests/test_collectors_base.py`

A `Collector` returns one or more `SignalResult`s and (optionally) `PromptIA` log entries. `CollectorContext` carries the doctor input + a clock. `SignalResult` is a lightweight pre-scoring carrier the assembler turns into a `Sinal`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_collectors_base.py
from visibility.collectors.base import SignalResult, CollectorContext, CollectorOutput
from visibility.models import Status, DoctorMeta

def _ctx():
    return CollectorContext(
        doctor=DoctorMeta(nome="Dra. Fulana", especialidade_principal="Dermatologia",
                          cidade="São Paulo", uf="SP", site="https://drafulana.com.br"),
        now="2026-06-28T14:00:00Z", regiao_busca="São Paulo, SP")

def test_signal_result_to_sinal():
    ctx = _ctx()
    res = SignalResult(
        id="google_marca", label="Aparece no Google", status=Status.fail, valor=False,
        weight=12.5, confianca=0.9, metodo="serp_scrape", observacao="nada",
        evidencia=[{"fonte": "google_search", "resumo": "0 no top 10"}])
    sinal = res.to_sinal(ctx)
    assert sinal.id == "google_marca"
    assert sinal.evidencia[0].capturado_em == "2026-06-28T14:00:00Z"  # clock injected
    assert sinal.evidencia[0].fonte == "google_search"

def test_collector_output_defaults():
    out = CollectorOutput(signals=[])
    assert out.prompts == []
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_collectors_base.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'visibility.collectors'`

- [ ] **Step 3: Write the base module**

```python
# visibility/collectors/__init__.py
```

```python
# visibility/collectors/base.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable
from visibility.models import Sinal, Evidencia, Status, DoctorMeta, PromptIA

@dataclass
class CollectorContext:
    doctor: DoctorMeta
    now: str                     # ISO timestamp, injected for determinism
    regiao_busca: str | None = None

@dataclass
class SignalResult:
    id: str
    label: str
    status: Status
    valor: bool | float | str
    weight: float
    confianca: float
    metodo: str
    evidencia: list[dict]        # each: fonte/url/query/resumo/raw (capturado_em auto-filled)
    observacao: str | None = None

    def to_sinal(self, ctx: CollectorContext) -> Sinal:
        ev = [Evidencia(capturado_em=e.get("capturado_em", ctx.now),
                        fonte=e["fonte"], url=e.get("url"), query=e.get("query"),
                        resumo=e["resumo"], raw=e.get("raw")) for e in self.evidencia]
        return Sinal(id=self.id, label=self.label, status=self.status, valor=self.valor,
                     weight=self.weight, confianca=self.confianca, metodo=self.metodo,
                     observacao=self.observacao, evidencia=ev)

@dataclass
class CollectorOutput:
    signals: list[SignalResult]
    prompts: list[PromptIA] = field(default_factory=list)

@runtime_checkable
class Collector(Protocol):
    category: str                # which category these signals belong to
    def collect(self, ctx: CollectorContext) -> CollectorOutput: ...
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_collectors_base.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add visibility/collectors/ tests/test_collectors_base.py
git commit -m "feat: collector protocol, context, and signal carrier"
```

---

## Task 7: Site / E-E-A-T collector (5 signals)

**Files:**
- Create: `visibility/clients.py` (start it here — `HttpClient` protocol + httpx impl)
- Create: `visibility/collectors/site_analysis.py`
- Create: `tests/fixtures/site_drafulana.html`
- Test: `tests/test_site_analysis.py`

Signals: `crm_rqe_visivel` (regex on text), `schema_medico` (JSON-LD Physician/MedicalClinic via extruct), `pagina_especialidade` (link/url for the specialty), `pagina_procedimento` (links for procedimentos_foco — partial if some, pass if all), `conteudo_perguntas` (FAQPage schema OR ≥3 question headings).

- [ ] **Step 1: Create the test fixture**

```html
<!-- tests/fixtures/site_drafulana.html -->
<!doctype html><html lang="pt-BR"><head>
<script type="application/ld+json">
{"@context":"https://schema.org","@type":"Physician","name":"Dra. Fulana de Tal"}
</script>
</head><body>
<footer>CRM-SP 123456 · RQE 12345</footer>
<nav>
  <a href="/dermatologia">Dermatologia</a>
  <a href="/botox">Botox</a>
</nav>
<h2>O botox é seguro?</h2>
<h2>Quanto tempo dura o preenchimento?</h2>
<h2>A acne tem cura?</h2>
</body></html>
```

- [ ] **Step 2: Write the failing test**

```python
# tests/test_site_analysis.py
from pathlib import Path
from visibility.collectors.base import CollectorContext
from visibility.collectors.site_analysis import SiteAnalysisCollector
from visibility.models import DoctorMeta, Status

FIXTURE = (Path(__file__).parent / "fixtures" / "site_drafulana.html").read_text()

class FakeHttp:
    def __init__(self, body): self.body = body
    def get_text(self, url: str) -> str: return self.body

def _ctx():
    return CollectorContext(
        doctor=DoctorMeta(nome="Dra. Fulana de Tal", especialidade_principal="Dermatologia",
                          cidade="São Paulo", uf="SP", site="https://drafulana.com.br",
                          procedimentos_foco=["botox", "preenchimento", "acne"]),
        now="2026-06-28T14:00:00Z")

def _by_id(out):
    return {s.id: s for s in out.signals}

def test_site_signals():
    out = SiteAnalysisCollector(http=FakeHttp(FIXTURE)).collect(_ctx())
    sig = _by_id(out)
    assert sig["crm_rqe_visivel"].status == Status.pass_
    assert sig["schema_medico"].status == Status.pass_
    assert sig["pagina_especialidade"].status == Status.pass_
    assert sig["pagina_procedimento"].status == Status.partial   # botox only, not all 3
    assert sig["conteudo_perguntas"].status == Status.pass_      # 3 question headings

def test_no_site_yields_unknown():
    ctx = _ctx(); ctx.doctor.site = None
    out = SiteAnalysisCollector(http=FakeHttp("")).collect(ctx)
    assert all(s.status == Status.unknown for s in out.signals)
```

- [ ] **Step 3: Run test to verify it fails**

Run: `pytest tests/test_site_analysis.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'visibility.collectors.site_analysis'`

- [ ] **Step 4: Write the HTTP client protocol + site collector**

```python
# visibility/clients.py
from __future__ import annotations
from typing import Protocol
import httpx

class HttpClient(Protocol):
    def get_text(self, url: str) -> str: ...

class HttpxClient:
    def __init__(self, timeout: float = 15.0):
        self._client = httpx.Client(timeout=timeout, follow_redirects=True,
                                    headers={"User-Agent": "MedRankGPT-VisibilityBot/0.1"})
    def get_text(self, url: str) -> str:
        r = self._client.get(url)
        r.raise_for_status()
        return r.text
```

```python
# visibility/collectors/site_analysis.py
from __future__ import annotations
import re
import unicodedata
import extruct
from bs4 import BeautifulSoup
from visibility.clients import HttpClient
from visibility.collectors.base import CollectorContext, CollectorOutput, SignalResult
from visibility.models import Status

CRM_RE = re.compile(r"\bCRM[\s./-]*[A-Z]{0,2}[\s-]*\d{4,6}\b", re.IGNORECASE)
RQE_RE = re.compile(r"\bRQE[\s.:-]*\d{3,6}\b", re.IGNORECASE)
_MED_TYPES = {"physician", "medicalclinic", "medicalorganization", "dentist", "hospital"}

def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    return s.lower()

class SiteAnalysisCollector:
    category = "site_conteudo"

    def __init__(self, http: HttpClient):
        self.http = http

    def collect(self, ctx: CollectorContext) -> CollectorOutput:
        site = ctx.doctor.site
        if not site:
            return CollectorOutput(signals=[self._unknown(i, l) for i, l in self._labels()])
        html = self.http.get_text(site)
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(" ", strip=True)
        data = extruct.extract(html, base_url=site, syntaxes=["json-ld", "microdata"])
        return CollectorOutput(signals=[
            self._crm_rqe(text, site),
            self._schema(data, site),
            self._specialty_page(soup, ctx, site),
            self._procedure_pages(soup, ctx, site),
            self._qa_content(soup, data, site),
        ])

    # --- signals ---
    def _crm_rqe(self, text: str, url: str) -> SignalResult:
        has_crm = bool(CRM_RE.search(text)); has_rqe = bool(RQE_RE.search(text))
        status = Status.pass_ if (has_crm and has_rqe) else Status.partial if has_crm else Status.fail
        return SignalResult("crm_rqe_visivel", "CRM/RQE visível no site", status,
            has_crm, 5, 0.95, "site_scrape",
            [{"fonte": "site", "url": url, "resumo": f"CRM={has_crm} RQE={has_rqe}"}],
            None if has_crm else "Nenhum CRM encontrado no texto do site.")

    def _schema(self, data: dict, url: str) -> SignalResult:
        found = self._schema_types(data)
        has = bool(_MED_TYPES & found)
        return SignalResult("schema_medico", "Tem schema médico (Physician/MedicalClinic)",
            Status.pass_ if has else Status.fail, has, 5, 0.97, "schema_parse",
            [{"fonte": "site", "url": url, "resumo": f"tipos JSON-LD: {sorted(found) or 'nenhum'}"}])

    def _specialty_page(self, soup, ctx, url) -> SignalResult:
        esp = _norm(ctx.doctor.especialidade_principal)
        has = any(esp in _norm(a.get("href", "") + " " + a.get_text(" ")) for a in soup.find_all("a"))
        return SignalResult("pagina_especialidade", "Tem página por especialidade",
            Status.pass_ if has else Status.fail, has, 5, 0.9, "site_scrape",
            [{"fonte": "site", "url": url, "resumo": f"link p/ '{esp}': {has}"}])

    def _procedure_pages(self, soup, ctx, url) -> SignalResult:
        procs = [_norm(p) for p in ctx.doctor.procedimentos_foco]
        haystack = " ".join(_norm(a.get("href", "") + " " + a.get_text(" ")) for a in soup.find_all("a"))
        hits = [p for p in procs if p in haystack]
        if not procs:
            status = Status.unknown
        elif len(hits) == len(procs):
            status = Status.pass_
        elif hits:
            status = Status.partial
        else:
            status = Status.fail
        return SignalResult("pagina_procedimento", "Tem página por procedimento", status,
            len(hits), 5, 0.85, "site_scrape",
            [{"fonte": "site", "url": url, "resumo": f"{len(hits)}/{len(procs)} procedimentos com página"}],
            None if status in (Status.pass_, Status.unknown) else f"Faltam: {sorted(set(procs) - set(hits))}")

    def _qa_content(self, soup, data: dict, url) -> SignalResult:
        has_faq = "faqpage" in self._schema_types(data)
        questions = [h.get_text(strip=True) for h in soup.find_all(["h2", "h3"])
                     if h.get_text(strip=True).endswith("?")]
        has = has_faq or len(questions) >= 3
        return SignalResult("conteudo_perguntas", "Conteúdo que responde perguntas reais",
            Status.pass_ if has else Status.fail, has, 5, 0.8, "site_scrape",
            [{"fonte": "site", "url": url,
              "resumo": f"FAQPage={has_faq}; headings-pergunta={len(questions)}"}])

    # --- helpers ---
    def _schema_types(self, data: dict) -> set[str]:
        types: set[str] = set()
        for syntax in ("json-ld", "microdata"):
            for item in data.get(syntax, []):
                t = item.get("@type")
                for v in ([t] if isinstance(t, str) else t or []):
                    types.add(_norm(str(v)))
        return types

    def _labels(self):
        return [("crm_rqe_visivel", "CRM/RQE visível no site"),
                ("schema_medico", "Tem schema médico (Physician/MedicalClinic)"),
                ("pagina_especialidade", "Tem página por especialidade"),
                ("pagina_procedimento", "Tem página por procedimento"),
                ("conteudo_perguntas", "Conteúdo que responde perguntas reais")]

    def _unknown(self, id_: str, label: str) -> SignalResult:
        return SignalResult(id_, label, Status.unknown, False, 5, 0.0, "site_scrape",
                            [{"fonte": "site", "resumo": "Médico sem site informado."}],
                            "Sem site para analisar.")
```

- [ ] **Step 5: Run test to verify it passes**

Run: `pytest tests/test_site_analysis.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add visibility/clients.py visibility/collectors/site_analysis.py tests/fixtures/site_drafulana.html tests/test_site_analysis.py
git commit -m "feat: site/E-E-A-T collector (5 signals) + http client"
```

---

## Task 8: Google search collector (`google_marca`)

**Files:**
- Modify: `visibility/clients.py` (add `SearchClient` protocol + SerpAPI impl)
- Create: `visibility/collectors/google_search.py`
- Create: `tests/fixtures/serp_drafulana.json`
- Test: `tests/test_google_search.py`

Logic: search the doctor's name + specialty; **pass** if the doctor's own domain appears in the top 10; **partial** if they appear only via a third-party profile (Doctoralia etc.); **fail** otherwise.

- [ ] **Step 1: Create the fixture**

```json
// tests/fixtures/serp_drafulana.json
{"organic_results": [
  {"position": 1, "title": "Dra. Fulana - Doctoralia", "link": "https://www.doctoralia.com.br/dra-fulana"},
  {"position": 2, "title": "Outra clínica", "link": "https://clinicaxyz.com.br"}
]}
```

- [ ] **Step 2: Write the failing test**

```python
# tests/test_google_search.py
import json
from pathlib import Path
from visibility.collectors.base import CollectorContext
from visibility.collectors.google_search import GoogleSearchCollector
from visibility.models import DoctorMeta, Status

SERP = json.loads((Path(__file__).parent / "fixtures" / "serp_drafulana.json").read_text())

class FakeSearch:
    def __init__(self, payload): self.payload = payload
    def search(self, query: str, location: str | None = None) -> dict: return self.payload

def _ctx(site="https://drafulana.com.br"):
    return CollectorContext(
        doctor=DoctorMeta(nome="Dra. Fulana", especialidade_principal="Dermatologia",
                          cidade="São Paulo", uf="SP", site=site),
        now="2026-06-28T14:00:00Z", regiao_busca="São Paulo, SP")

def test_partial_when_only_third_party():
    out = GoogleSearchCollector(search=FakeSearch(SERP)).collect(_ctx())
    s = out.signals[0]
    assert s.id == "google_marca"
    assert s.status == Status.partial  # appears via Doctoralia, not own domain

def test_pass_when_own_domain_present():
    payload = {"organic_results": [
        {"position": 1, "title": "Dra. Fulana", "link": "https://drafulana.com.br/sobre"}]}
    out = GoogleSearchCollector(search=FakeSearch(payload)).collect(_ctx())
    assert out.signals[0].status == Status.pass_

def test_fail_when_absent():
    payload = {"organic_results": [{"position": 1, "title": "Z", "link": "https://z.com"}]}
    out = GoogleSearchCollector(search=FakeSearch(payload)).collect(_ctx())
    assert out.signals[0].status == Status.fail
```

- [ ] **Step 3: Run test to verify it fails**

Run: `pytest tests/test_google_search.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'visibility.collectors.google_search'`

- [ ] **Step 4: Add the SearchClient + write the collector**

```python
# add to visibility/clients.py
class SearchClient(Protocol):
    def search(self, query: str, location: str | None = None) -> dict: ...

class SerpApiClient:
    def __init__(self, api_key: str, timeout: float = 20.0):
        self.api_key = api_key
        self._client = httpx.Client(timeout=timeout)
    def search(self, query: str, location: str | None = None) -> dict:
        params = {"engine": "google", "q": query, "api_key": self.api_key,
                  "hl": "pt-br", "google_domain": "google.com.br", "num": 10}
        if location:
            params["location"] = location
        r = self._client.get("https://serpapi.com/search.json", params=params)
        r.raise_for_status()
        return r.json()
```

```python
# visibility/collectors/google_search.py
from __future__ import annotations
from urllib.parse import urlparse
from visibility.clients import SearchClient
from visibility.collectors.base import CollectorContext, CollectorOutput, SignalResult
from visibility.models import Status

def _domain(url: str) -> str:
    return (urlparse(url).hostname or "").lower().removeprefix("www.")

class GoogleSearchCollector:
    category = "busca_tradicional"

    def __init__(self, search: SearchClient):
        self.search = search

    def collect(self, ctx: CollectorContext) -> CollectorOutput:
        query = f"{ctx.doctor.nome} {ctx.doctor.especialidade_principal}"
        payload = self.search.search(query, location=ctx.regiao_busca)
        results = payload.get("organic_results", [])[:10]
        own = _domain(ctx.doctor.site) if ctx.doctor.site else None
        own_hit = bool(own) and any(_domain(r.get("link", "")) == own for r in results)
        any_hit = len(results) > 0 and any(
            _domain(r.get("link", "")) for r in results)  # at least appears somewhere
        # appears at all = name surfaced via any result; refine: only count if results non-empty
        name_hit = len(results) > 0
        if own_hit:
            status, obs = Status.pass_, None
        elif name_hit:
            status, obs = Status.partial, "Aparece só via perfis de terceiros, não com domínio próprio."
        else:
            status, obs = Status.fail, "Não aparece no top 10 ao buscar o nome."
        top = [{"position": r.get("position"), "link": r.get("link")} for r in results[:5]]
        return CollectorOutput(signals=[SignalResult(
            "google_marca", "Aparece no Google ao buscar o nome", status, own_hit, 12.5,
            0.9, "serp_scrape",
            [{"fonte": "google_search", "query": query, "resumo": f"top10={len(results)}, domínio próprio={own_hit}",
              "raw": top}], obs)])
```

- [ ] **Step 5: Run test to verify it passes**

Run: `pytest tests/test_google_search.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add visibility/clients.py visibility/collectors/google_search.py tests/fixtures/serp_drafulana.json tests/test_google_search.py
git commit -m "feat: google search collector (google_marca) + SERP client"
```

---

## Task 9: Google Maps collector (`google_maps`)

**Files:**
- Modify: `visibility/clients.py` (add `PlacesClient` protocol + Google Places impl)
- Create: `visibility/collectors/google_maps.py`
- Create: `tests/fixtures/places_drafulana.json`
- Test: `tests/test_google_maps.py`

Logic: Places Text Search for `"{nome} {cidade}"`; **pass** if a result name fuzzy-matches the doctor, **fail** if none.

- [ ] **Step 1: Create the fixture**

```json
// tests/fixtures/places_drafulana.json
{"results": [
  {"name": "Dra. Fulana de Tal - Dermatologia", "formatted_address": "São Paulo, SP",
   "place_id": "abc123", "user_ratings_total": 42}
]}
```

- [ ] **Step 2: Write the failing test**

```python
# tests/test_google_maps.py
import json
from pathlib import Path
from visibility.collectors.base import CollectorContext
from visibility.collectors.google_maps import GoogleMapsCollector
from visibility.models import DoctorMeta, Status

PLACES = json.loads((Path(__file__).parent / "fixtures" / "places_drafulana.json").read_text())

class FakePlaces:
    def __init__(self, payload): self.payload = payload
    def text_search(self, query: str) -> dict: return self.payload

def _ctx():
    return CollectorContext(
        doctor=DoctorMeta(nome="Dra. Fulana de Tal", especialidade_principal="Dermatologia",
                          cidade="São Paulo", uf="SP"),
        now="2026-06-28T14:00:00Z")

def test_pass_when_listing_found():
    out = GoogleMapsCollector(places=FakePlaces(PLACES)).collect(_ctx())
    assert out.signals[0].id == "google_maps"
    assert out.signals[0].status == Status.pass_

def test_fail_when_no_match():
    out = GoogleMapsCollector(places=FakePlaces({"results": [
        {"name": "Padaria do Zé", "place_id": "x"}]})).collect(_ctx())
    assert out.signals[0].status == Status.fail
```

- [ ] **Step 3: Run test to verify it fails**

Run: `pytest tests/test_google_maps.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'visibility.collectors.google_maps'`

- [ ] **Step 4: Add PlacesClient + write the collector**

```python
# add to visibility/clients.py
class PlacesClient(Protocol):
    def text_search(self, query: str) -> dict: ...

class GooglePlacesClient:
    def __init__(self, api_key: str, timeout: float = 20.0):
        self.api_key = api_key
        self._client = httpx.Client(timeout=timeout)
    def text_search(self, query: str) -> dict:
        r = self._client.get(
            "https://maps.googleapis.com/maps/api/place/textsearch/json",
            params={"query": query, "key": self.api_key, "language": "pt-BR"})
        r.raise_for_status()
        return r.json()
```

```python
# visibility/collectors/google_maps.py
from __future__ import annotations
import unicodedata
from visibility.clients import PlacesClient
from visibility.collectors.base import CollectorContext, CollectorOutput, SignalResult
from visibility.models import Status

def _norm(s: str) -> str:
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii").lower()

def _name_tokens(name: str) -> set[str]:
    drop = {"dr", "dra", "de", "da", "do", "dos", "das"}
    return {t for t in _norm(name).replace(".", " ").split() if t and t not in drop}

class GoogleMapsCollector:
    category = "busca_tradicional"

    def __init__(self, places: PlacesClient):
        self.places = places

    def collect(self, ctx: CollectorContext) -> CollectorOutput:
        query = f"{ctx.doctor.nome} {ctx.doctor.cidade}"
        payload = self.places.text_search(query)
        wanted = _name_tokens(ctx.doctor.nome)
        match = None
        for r in payload.get("results", []):
            if wanted and wanted <= _name_tokens(r.get("name", "")):
                match = r
                break
        status = Status.pass_ if match else Status.fail
        resumo = (f"Ficha encontrada: {match['name']}" if match
                  else "Nenhuma ficha verificada para o nome na cidade.")
        return CollectorOutput(signals=[SignalResult(
            "google_maps", "Aparece no Google Maps / Perfil de Empresa", status, bool(match),
            12.5, 0.92, "gmaps_api",
            [{"fonte": "google_maps", "query": query, "resumo": resumo,
              "raw": match}], None if match else "Sem perfil de empresa verificado.")])
```

- [ ] **Step 5: Run test to verify it passes**

Run: `pytest tests/test_google_maps.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add visibility/clients.py visibility/collectors/google_maps.py tests/fixtures/places_drafulana.json tests/test_google_maps.py
git commit -m "feat: google maps collector (google_maps) + places client"
```

---

## Task 10: Medical platforms collector (`doctoralia`, `boaconsulta`)

**Files:**
- Create: `visibility/collectors/medical_platforms.py`
- Create: `tests/fixtures/doctoralia_results.html`
- Test: `tests/test_medical_platforms.py`

Logic: query each platform's public search URL (via the existing `HttpClient`) and detect a profile card whose name matches the doctor. **pass** if a matching profile link is found, **fail** otherwise. Reuses `_name_tokens` matching.

- [ ] **Step 1: Create the fixture**

```html
<!-- tests/fixtures/doctoralia_results.html -->
<html><body>
<div class="result">
  <a href="/dermatologista/fulana-de-tal" data-test-id="doctor-link">Dra. Fulana de Tal</a>
</div>
<div class="result">
  <a href="/dermatologista/outro-medico">Dr. Outro Medico</a>
</div>
</body></html>
```

- [ ] **Step 2: Write the failing test**

```python
# tests/test_medical_platforms.py
from pathlib import Path
from visibility.collectors.base import CollectorContext
from visibility.collectors.medical_platforms import MedicalPlatformsCollector
from visibility.models import DoctorMeta, Status

DOCTORALIA = (Path(__file__).parent / "fixtures" / "doctoralia_results.html").read_text()

class FakeHttp:
    def __init__(self, by_host): self.by_host = by_host
    def get_text(self, url: str) -> str:
        for host, body in self.by_host.items():
            if host in url:
                return body
        return "<html></html>"

def _ctx():
    return CollectorContext(
        doctor=DoctorMeta(nome="Dra. Fulana de Tal", especialidade_principal="Dermatologia",
                          cidade="São Paulo", uf="SP"),
        now="2026-06-28T14:00:00Z")

def test_doctoralia_found_boaconsulta_absent():
    http = FakeHttp({"doctoralia.com.br": DOCTORALIA})  # boaconsulta returns empty
    out = MedicalPlatformsCollector(http=http).collect(_ctx())
    sig = {s.id: s for s in out.signals}
    assert sig["doctoralia"].status == Status.pass_
    assert sig["boaconsulta"].status == Status.fail
```

- [ ] **Step 3: Run test to verify it fails**

Run: `pytest tests/test_medical_platforms.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'visibility.collectors.medical_platforms'`

- [ ] **Step 4: Write the collector**

```python
# visibility/collectors/medical_platforms.py
from __future__ import annotations
import unicodedata
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from visibility.clients import HttpClient
from visibility.collectors.base import CollectorContext, CollectorOutput, SignalResult
from visibility.models import Status

def _norm(s: str) -> str:
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii").lower()

def _tokens(name: str) -> set[str]:
    drop = {"dr", "dra", "de", "da", "do", "dos", "das"}
    return {t for t in _norm(name).replace(".", " ").split() if t and t not in drop}

_PLATFORMS = [
    ("doctoralia", "Doctoralia", "https://www.doctoralia.com.br/pesquisa?q={q}"),
    ("boaconsulta", "BoaConsulta", "https://www.boaconsulta.com/busca/?q={q}"),
]

class MedicalPlatformsCollector:
    category = "plataformas_medicas"

    def __init__(self, http: HttpClient):
        self.http = http

    def collect(self, ctx: CollectorContext) -> CollectorOutput:
        wanted = _tokens(ctx.doctor.nome)
        signals = []
        for id_, label, tmpl in _PLATFORMS:
            url = tmpl.format(q=quote_plus(ctx.doctor.nome))
            try:
                html = self.http.get_text(url)
            except Exception:
                html = ""
            found_href = self._match(html, wanted)
            status = Status.pass_ if found_href else Status.fail
            signals.append(SignalResult(
                id_, f"Tem perfil na {label}", status, bool(found_href), 12.5, 0.85,
                "profile_scrape",
                [{"fonte": id_, "url": url,
                  "resumo": f"perfil encontrado: {found_href or 'não'}"}],
                None if found_href else f"Sem perfil na {label} para o nome."))
        return CollectorOutput(signals=signals)

    def _match(self, html: str, wanted: set[str]) -> str | None:
        if not html or not wanted:
            return None
        soup = BeautifulSoup(html, "html.parser")
        for a in soup.find_all("a"):
            if wanted <= _tokens(a.get_text(" ")):
                return a.get("href")
        return None
```

- [ ] **Step 5: Run test to verify it passes**

Run: `pytest tests/test_medical_platforms.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add visibility/collectors/medical_platforms.py tests/fixtures/doctoralia_results.html tests/test_medical_platforms.py
git commit -m "feat: medical platforms collector (doctoralia, boaconsulta)"
```

---

## Task 11: AI engines collector (`ia_marca`, `ia_procedimento`) + prompts_ia

**Files:**
- Modify: `visibility/clients.py` (add `LLMClient` protocol + OpenAI-compatible + Gemini impls)
- Create: `visibility/collectors/ai_engines.py`
- Test: `tests/test_ai_engines.py`

Logic: build prompts a patient would ask — one **marca** prompt ("o que sabe sobre {nome}…") and one **procedimento** prompt per procedimento_foco ("melhor médico para {proc} em {cidade}"). Ask each configured engine. Detect citation by name-token match in the response. Record a `PromptIA` per prompt×engine. Signals: `ia_marca` = pass if cited in ≥1 marca prompt; `ia_procedimento` = pass if cited in all procedure prompts, partial if some, fail if none.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_ai_engines.py
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_ai_engines.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'visibility.collectors.ai_engines'`

- [ ] **Step 3: Add LLMClient impls + write the collector**

```python
# add to visibility/clients.py
class LLMClient(Protocol):
    name: str
    def ask(self, prompt: str) -> str: ...

class OpenAICompatibleClient:
    """Works for OpenAI (chatgpt) and Perplexity — same chat-completions shape."""
    def __init__(self, name: str, api_key: str, model: str,
                 base_url: str = "https://api.openai.com/v1", timeout: float = 60.0):
        self.name = name; self.model = model; self.base_url = base_url.rstrip("/")
        self._client = httpx.Client(timeout=timeout,
                                    headers={"Authorization": f"Bearer {api_key}"})
    def ask(self, prompt: str) -> str:
        r = self._client.post(f"{self.base_url}/chat/completions",
            json={"model": self.model, "messages": [{"role": "user", "content": prompt}]})
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]

class GeminiClient:
    def __init__(self, name: str, api_key: str, model: str = "gemini-1.5-pro",
                 timeout: float = 60.0):
        self.name = name; self.model = model; self.api_key = api_key
        self._client = httpx.Client(timeout=timeout)
    def ask(self, prompt: str) -> str:
        r = self._client.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent",
            params={"key": self.api_key},
            json={"contents": [{"parts": [{"text": prompt}]}]})
        r.raise_for_status()
        return r.json()["candidates"][0]["content"]["parts"][0]["text"]
```

```python
# visibility/collectors/ai_engines.py
from __future__ import annotations
import re
import unicodedata
from visibility.clients import LLMClient
from visibility.collectors.base import CollectorContext, CollectorOutput, SignalResult
from visibility.models import Status, PromptIA, DoctorMeta

# "Dr." / "Dra." followed by 1–3 capitalized (incl. accented) name words.
_DOCTOR_NAME_RE = re.compile(
    r"\bDr[a]?\.?\s+[A-ZÀ-Ý][\wÀ-ÿ]+(?:\s+[A-ZÀ-Ý][\wÀ-ÿ]+){0,2}")

def _norm(s: str) -> str:
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii").lower()

def _tokens(name: str) -> set[str]:
    drop = {"dr", "dra", "de", "da", "do", "dos", "das"}
    return {t for t in _norm(name).replace(".", " ").split() if t and t not in drop}

def _cited(answer: str, name: str) -> bool:
    return bool(_tokens(name)) and _tokens(name) <= set(_norm(answer).replace(".", " ").split())

def extract_competitors(answer: str, own_name: str) -> list[str]:
    """Pull 'Dr./Dra. Nome' mentions from a free-text answer, excluding the doctor.
    Deduplicates while preserving first-seen order."""
    own = _tokens(own_name)
    seen: list[str] = []
    for raw in _DOCTOR_NAME_RE.findall(answer):
        name = re.sub(r"\s+", " ", raw).strip()
        # skip if this mention is the doctor herself (name tokens overlap fully)
        if own and own <= _tokens(name):
            continue
        if name not in seen:
            seen.append(name)
    return seen

def build_prompts(doctor: DoctorMeta, regiao: str | None) -> list[dict]:
    loc = regiao or f"{doctor.cidade}, {doctor.uf}"
    prompts = [{"tipo": "marca",
                "prompt": f"O que você sabe sobre a médica {doctor.nome}, "
                          f"{doctor.especialidade_principal} em {loc}?"}]
    for proc in doctor.procedimentos_foco:
        prompts.append({"tipo": "procedimento",
                        "prompt": f"Quem é o melhor médico para {proc} em {loc}?"})
    return prompts

class AiEnginesCollector:
    category = "visibilidade_ia"

    def __init__(self, engines: dict[str, LLMClient]):
        self.engines = engines  # engine name (schema enum) -> client

    def collect(self, ctx: CollectorContext) -> CollectorOutput:
        prompts = build_prompts(ctx.doctor, ctx.regiao_busca)
        log: list[PromptIA] = []
        idx = 0
        for spec in prompts:
            for engine_name, client in self.engines.items():
                answer = client.ask(spec["prompt"])
                cited = _cited(answer, ctx.doctor.nome)
                idx += 1
                log.append(PromptIA(
                    id=f"p{idx}", prompt=spec["prompt"], tipo=spec["tipo"],
                    engine=engine_name, regiao=ctx.regiao_busca, medico_citado=cited,
                    concorrentes_citados=extract_competitors(answer, ctx.doctor.nome),
                    capturado_em=ctx.now, raw_resposta=answer))
        marca = [p for p in log if p.tipo == "marca"]
        proc = [p for p in log if p.tipo == "procedimento"]
        return CollectorOutput(signals=[
            self._signal("ia_marca", "Aparece em respostas de IA pela marca", marca, 0.8),
            self._signal("ia_procedimento", "Aparece em perguntas de procedimento", proc, 0.8),
        ], prompts=log)

    def _signal(self, id_, label, entries: list[PromptIA], conf) -> SignalResult:
        if not entries:
            status, valor, obs = Status.unknown, False, "Nenhum prompt deste tipo executado."
        else:
            hits = sum(p.medico_citado for p in entries)
            if hits == len(entries):
                status, obs = Status.pass_, None
            elif hits:
                status, obs = Status.partial, f"Citado em {hits}/{len(entries)} prompts."
            else:
                status, obs = Status.fail, "Não citado em nenhum prompt."
            valor = hits > 0
        return SignalResult(id_, label, status, valor, 12.5, conf, "llm_prompt",
            [{"fonte": "ai_engines",
              "resumo": f"{sum(p.medico_citado for p in entries)}/{len(entries)} prompts citaram o médico"}],
            obs)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_ai_engines.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add visibility/clients.py visibility/collectors/ai_engines.py tests/test_ai_engines.py
git commit -m "feat: AI engines collector (ia_marca, ia_procedimento) + prompts_ia log"
```

---

## Task 12: Competitors aggregation

**Files:**
- Create: `visibility/competitors.py`
- Test: `tests/test_competitors.py`

Logic: from `prompts_ia`, count each name in `concorrentes_citados` across prompts where the doctor was NOT cited; produce `ofensores_recorrentes` sorted by appearances (desc) and a human `resumo`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_competitors.py
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_competitors.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'visibility.competitors'`

- [ ] **Step 3: Write the aggregator**

```python
# visibility/competitors.py
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_competitors.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add visibility/competitors.py tests/test_competitors.py
git commit -m "feat: competitors aggregation from prompts_ia"
```

---

## Task 13: Assembler

**Files:**
- Create: `visibility/assembler.py`
- Test: `tests/test_assembler.py`

Logic: given a `DoctorMeta`, a list of collectors, a clock, and a pipeline version, run every collector, group `SignalResult`s into categories (by each collector's `category`), build `Categoria` objects with the right `max`/`weight` (25 each), run `score_report`, aggregate competitors from the collected prompts, and return a fully-scored `VisibilityReport`. Each signal's `weight` already comes from the collector; category `max` = sum of its signals' weights, capped at 25.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_assembler.py
from visibility.assembler import assemble_report, CATEGORY_LABELS
from visibility.collectors.base import CollectorContext, CollectorOutput, SignalResult
from visibility.models import DoctorMeta, Status, PromptIA

class FakeCollector:
    def __init__(self, category, signals, prompts=None):
        self.category = category; self._signals = signals; self._prompts = prompts or []
    def collect(self, ctx) -> CollectorOutput:
        return CollectorOutput(signals=self._signals, prompts=self._prompts)

def _sr(id_, status, weight, cat_specific=True):
    return SignalResult(id_, id_, status, True, weight, 1.0, "m",
                        [{"fonte": "x", "resumo": "r"}])

def _doctor():
    return DoctorMeta(nome="Dra. Fulana", especialidade_principal="Dermatologia",
                      cidade="São Paulo", uf="SP")

def test_assemble_groups_scores_and_validates():
    collectors = [
        FakeCollector("busca_tradicional", [
            _sr("google_marca", Status.partial, 12.5), _sr("google_maps", Status.fail, 12.5)]),
        FakeCollector("visibilidade_ia",
            [_sr("ia_marca", Status.fail, 12.5), _sr("ia_procedimento", Status.fail, 12.5)],
            prompts=[PromptIA(id="p1", prompt="q", tipo="procedimento", engine="chatgpt",
                              medico_citado=False, concorrentes_citados=["Dr. X"])]),
    ]
    report = assemble_report(_doctor(), collectors, now="2026-06-28T14:00:00Z",
                             pipeline_version="0.1.0", regiao_busca="São Paulo, SP")
    assert report.categorias["busca_tradicional"].label == CATEGORY_LABELS["busca_tradicional"]
    assert report.categorias["busca_tradicional"].score == 6.25
    assert report.score.total == 6.25
    assert report.score.tier == "Bronze"
    assert report.concorrentes.ofensores_recorrentes[0].nome == "Dr. X"
    # serializes + validates against the schema
    from visibility.validation import validate_report
    validate_report(report.model_dump(mode="json", exclude_none=True))
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_assembler.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'visibility.assembler'`

- [ ] **Step 3: Write the assembler**

```python
# visibility/assembler.py
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_assembler.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add visibility/assembler.py tests/test_assembler.py
git commit -m "feat: assembler orchestrates collectors into a scored report"
```

---

## Task 14: Config + real-collector factory

**Files:**
- Create: `visibility/config.py`
- Test: `tests/test_config.py`

Logic: read API keys from env; build the real collector list and the engine map. Engines present only if their key is set (so a partial run is possible). `chatgpt`→OpenAI, `perplexity`→OpenAI-compatible (Perplexity base+model), `gemini`/`google_ai`→Gemini.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_config.py
from visibility.config import Settings, build_engines

def test_engines_only_when_keys_present(monkeypatch):
    s = Settings(openai_api_key="x", gemini_api_key=None, perplexity_api_key=None)
    engines = build_engines(s)
    assert set(engines) == {"chatgpt"}

def test_all_engines(monkeypatch):
    s = Settings(openai_api_key="x", gemini_api_key="y", perplexity_api_key="z")
    engines = build_engines(s)
    assert set(engines) == {"chatgpt", "perplexity", "gemini", "google_ai"}

def test_from_env(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "abc")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    s = Settings.from_env()
    assert s.openai_api_key == "abc"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_config.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'visibility.config'`

- [ ] **Step 3: Write config + factories**

```python
# visibility/config.py
from __future__ import annotations
import os
from dataclasses import dataclass
from visibility.clients import (
    HttpxClient, SerpApiClient, GooglePlacesClient,
    OpenAICompatibleClient, GeminiClient, LLMClient,
)
from visibility.collectors.site_analysis import SiteAnalysisCollector
from visibility.collectors.google_search import GoogleSearchCollector
from visibility.collectors.google_maps import GoogleMapsCollector
from visibility.collectors.medical_platforms import MedicalPlatformsCollector
from visibility.collectors.ai_engines import AiEnginesCollector

@dataclass
class Settings:
    serpapi_key: str | None = None
    google_places_key: str | None = None
    openai_api_key: str | None = None
    perplexity_api_key: str | None = None
    gemini_api_key: str | None = None

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            serpapi_key=os.getenv("SERPAPI_KEY"),
            google_places_key=os.getenv("GOOGLE_PLACES_KEY"),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            perplexity_api_key=os.getenv("PERPLEXITY_API_KEY"),
            gemini_api_key=os.getenv("GEMINI_API_KEY"),
        )

def build_engines(s: Settings) -> dict[str, LLMClient]:
    engines: dict[str, LLMClient] = {}
    if s.openai_api_key:
        engines["chatgpt"] = OpenAICompatibleClient("chatgpt", s.openai_api_key, "gpt-4o")
    if s.perplexity_api_key:
        engines["perplexity"] = OpenAICompatibleClient(
            "perplexity", s.perplexity_api_key, "sonar",
            base_url="https://api.perplexity.ai")
    if s.gemini_api_key:
        engines["gemini"] = GeminiClient("gemini", s.gemini_api_key)
        engines["google_ai"] = GeminiClient("google_ai", s.gemini_api_key)
    return engines

def build_collectors(s: Settings) -> list:
    http = HttpxClient()
    collectors: list = [
        SiteAnalysisCollector(http=http),
        MedicalPlatformsCollector(http=http),
        AiEnginesCollector(engines=build_engines(s)),
    ]
    if s.serpapi_key:
        collectors.append(GoogleSearchCollector(search=SerpApiClient(s.serpapi_key)))
    if s.google_places_key:
        collectors.append(GoogleMapsCollector(places=GooglePlacesClient(s.google_places_key)))
    return collectors
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_config.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add visibility/config.py tests/test_config.py
git commit -m "feat: env settings + real collector/engine factory"
```

---

## Task 15: CLI

**Files:**
- Create: `visibility/cli.py`
- Create: `tests/fixtures/doctor_input.json`
- Test: `tests/test_cli.py`

Logic: `medrank-visibility --doctor input.json [--out report.json] [--pipeline-version 0.1.0]`.
Reads a `DoctorMeta` JSON, builds collectors from env, assembles + validates the report, writes JSON to `--out` (or stdout). The timestamp comes from `--now` (default: real UTC now) so tests are deterministic. Collector construction is injectable for testing.

- [ ] **Step 1: Create the input fixture**

```json
// tests/fixtures/doctor_input.json
{"nome": "Dra. Fulana de Tal", "crm": "SP 123456", "rqe": "12345",
 "especialidade_principal": "Dermatologia", "especialidades": ["Dermatologia"],
 "procedimentos_foco": ["botox", "acne"], "cidade": "São Paulo", "uf": "SP",
 "site": "https://drafulana.com.br"}
```

- [ ] **Step 2: Write the failing test**

```python
# tests/test_cli.py
import json
from pathlib import Path
from visibility.cli import run
from visibility.collectors.base import CollectorOutput, SignalResult
from visibility.models import Status

INPUT = str(Path(__file__).parent / "fixtures" / "doctor_input.json")

class FakeCollector:
    category = "site_conteudo"
    def collect(self, ctx):
        return CollectorOutput(signals=[
            SignalResult("crm_rqe_visivel", "CRM/RQE", Status.pass_, True, 5, 1.0, "m",
                         [{"fonte": "site", "resumo": "ok"}])])

def test_run_writes_valid_report(tmp_path):
    out = tmp_path / "report.json"
    code = run(["--doctor", INPUT, "--out", str(out), "--now", "2026-06-28T14:00:00Z",
                "--pipeline-version", "0.1.0"],
               collector_factory=lambda settings: [FakeCollector()])
    assert code == 0
    data = json.loads(out.read_text())
    assert data["meta"]["doctor"]["nome"] == "Dra. Fulana de Tal"
    assert data["score"]["tier"] in ("Bronze", "Prata", "Ouro")
    assert data["categorias"]["site_conteudo"]["sinais"][0]["id"] == "crm_rqe_visivel"
    # output is schema-valid
    from visibility.validation import validate_report
    validate_report(data)
```

- [ ] **Step 3: Run test to verify it fails**

Run: `pytest tests/test_cli.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'visibility.cli'`

- [ ] **Step 4: Write the CLI**

```python
# visibility/cli.py
from __future__ import annotations
import argparse
import json
import sys
from datetime import datetime, timezone
from typing import Callable
from visibility.assembler import assemble_report
from visibility.config import Settings, build_collectors
from visibility.models import DoctorMeta
from visibility.validation import validate_report

def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def run(argv: list[str],
        collector_factory: Callable[[Settings], list] = build_collectors) -> int:
    parser = argparse.ArgumentParser(prog="medrank-visibility")
    parser.add_argument("--doctor", required=True, help="path to doctor input JSON")
    parser.add_argument("--out", help="output path (default: stdout)")
    parser.add_argument("--now", default=None, help="ISO timestamp override")
    parser.add_argument("--pipeline-version", default="0.1.0")
    args = parser.parse_args(argv)

    doctor = DoctorMeta.model_validate(json.loads(open(args.doctor, encoding="utf-8").read()))
    now = args.now or _utc_now()
    settings = Settings.from_env()
    collectors = collector_factory(settings)
    regiao = f"{doctor.cidade}, {doctor.uf}"
    report = assemble_report(doctor, collectors, now=now,
                             pipeline_version=args.pipeline_version, regiao_busca=regiao)
    data = report.model_dump(mode="json", exclude_none=True)
    validate_report(data)
    text = json.dumps(data, ensure_ascii=False, indent=2)
    if args.out:
        open(args.out, "w", encoding="utf-8").write(text)
    else:
        sys.stdout.write(text + "\n")
    return 0

def main() -> None:
    raise SystemExit(run(sys.argv[1:]))
```

- [ ] **Step 5: Run test to verify it passes**

Run: `pytest tests/test_cli.py -v`
Expected: PASS

- [ ] **Step 6: Run the full suite**

Run: `pytest -v`
Expected: all tests PASS

- [ ] **Step 7: Commit**

```bash
git add visibility/cli.py tests/fixtures/doctor_input.json tests/test_cli.py
git commit -m "feat: CLI assembles, validates, and writes a doctor report"
```

---

## Self-Review (completed during planning)

**Spec coverage:**
- 5 top-level blocks → models (Task 2) + schema (Task 3) + assembler builds all of them (Task 13). ✓
- `sinal` unit fields → `Sinal`/`SignalResult` (Tasks 2, 6). ✓
- 12 signals → site (Task 7: 5), google_marca (8), google_maps (9), doctoralia+boaconsulta (10), ia_marca+ia_procedimento (11), competitors block = signal #12 (12). ✓
- Scoring rules + tier bands (spec §5) → Task 5. ✓
- `concorrentes` derived from `prompts_ia` (spec §6–7) → Task 12. ✓
- JSON Schema validation (spec §9) → Tasks 3–4, re-checked in 13 & 15. ✓

**Type consistency:** `SignalResult.to_sinal` → `Sinal`; collectors expose `.category` matching `CATEGORY_LABELS` keys (`busca_tradicional`, `plataformas_medicas`, `visibilidade_ia`, `site_conteudo`); `LLMClient.ask`, `SearchClient.search`, `PlacesClient.text_search`, `HttpClient.get_text` used consistently across collectors and config. ✓

**Competitor extraction (signal #12):** `extract_competitors` (Task 11) pulls `Dr./Dra. Nome`
mentions from each answer via regex, excluding the doctor herself, and feeds
`concorrentes_citados` → the `concorrentes` block is populated end-to-end. The regex is a
pragmatic v1: it catches the dominant Brazilian "Dr./Dra. + Nome" pattern but will miss
clinics/brands named without a title (e.g. "Clínica X") and bare first-name mentions. A
follow-up could upgrade to an LLM extraction pass; the data model and aggregation already
support whatever names are supplied, so that upgrade needs no schema change.

**Known v1 approximations (documented, not gaps):**
- `google_ai` engine is backed by the Gemini client (Google AI Overviews has no public
  API); treated as a proxy and labeled as such in `prompts_ia.engine`.
- `google_marca` "appears via third-party" detection keys off *any* top-10 result when the
  own domain is absent — it does not yet confirm the result is specifically the doctor's
  profile vs. a namesake. Acceptable for a diagnostic; tighten with name-match if needed.
