# Frente 1 — Engine de Dados (Índice MedRank 2026) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Construir a engine de dados que produz o `aggregates.json` do relatório — lado da demanda (o que a IA responde ao paciente), lado da oferta (distribuição de AI Visibility Scores) e um modelo de custo — reaproveitando a CLI `visibility/` existente.

**Architecture:** Novo subpacote `visibility/study/`. Um **runner de demanda** roda prompts de paciente nos motores de IA (reaproveita `build_engines`); um **classificador** tipa cada resposta (médico nominal / marketplace / clínica / hospital / nenhum) e marca risco-CFM; **agregadores** transformam respostas brutas e relatórios de Visibility Score em estatísticas anonimizadas; um **export** monta e valida o `aggregates.json` contra um JSON Schema novo. Tudo orquestrado por uma CLI `medrank-study` com subcomandos (`plan`, `demand`, `supply`, `aggregate`).

**Tech Stack:** Python 3.11+, pydantic v2, dataclasses, jsonschema (Draft 2020-12), pytest + respx (já no `pyproject.toml`). Sem rede nos testes — usa clientes/coletores scriptados, padrão de `tests/test_ai_engines.py`.

**Convenções do repo (seguir):**
- Coletores reais ficam atrás de `LLMClient.ask(prompt) -> str` e de factories em `visibility/config.py`. Os testes injetam fakes.
- Determinismo via `now` ISO injetado (igual `--now` da CLI atual).
- Schemas em `visibility/<pkg>/schema/*.json`, validados com o padrão de `visibility/validation.py`.
- Testes flat em `tests/test_*.py`, asserts simples.

**Itens abertos herdados do spec (NÃO bloqueiam esta frente; viram dados de entrada):**
- Sourcing do roster (lado da oferta): o runner recebe um arquivo JSON de médicos pronto; *de onde vem a lista* é decidido fora desta engine.
- Preços exatos de API: o modelo de custo usa constantes ajustáveis num só lugar.

---

## File Structure

**Criar:**
- `visibility/study/__init__.py` — marca o subpacote.
- `visibility/study/config.py` — `DemandMatrix`, `RosterSpec`, `StudyConfig`, `PROMPT_TEMPLATES`; loaders de dict/arquivo.
- `visibility/study/demand.py` — `DemandPrompt`, `build_demand_prompts`, `DemandResponse`, `DemandRunner`.
- `visibility/study/classify.py` — `ResponseClassification`, `classify_response`, listas de marketplaces e frases de risco-CFM.
- `visibility/study/aggregate.py` — `aggregate_demand`, `aggregate_supply` e seus dataclasses de saída.
- `visibility/study/supply.py` — `load_roster`, `run_supply` (batch do Visibility Score).
- `visibility/study/cost.py` — `estimate_demand_calls`, `estimate_supply_calls`, `estimate_cost`.
- `visibility/study/export.py` — `build_aggregates`, `validate_aggregates`.
- `visibility/study/schema/__init__.py` — pacote do schema.
- `visibility/study/schema/study_aggregates_1_0.json` — JSON Schema do `aggregates.json`.
- `visibility/study/cli.py` — CLI `medrank-study` (`plan`/`demand`/`supply`/`aggregate`).
- `tests/test_study_config.py`, `tests/test_study_demand.py`, `tests/test_study_classify.py`, `tests/test_study_aggregate.py`, `tests/test_study_supply.py`, `tests/test_study_cost.py`, `tests/test_study_export.py`, `tests/test_study_cli.py`.

**Modificar:**
- `pyproject.toml` — adicionar entry point `medrank-study` e incluir o pacote `visibility.study` (+ schema) em `[tool.setuptools] packages`.

---

## Task 0: Scaffolding do subpacote

**Files:**
- Create: `visibility/study/__init__.py`
- Create: `visibility/study/schema/__init__.py`
- Modify: `pyproject.toml:23-24` (lista de packages) e `pyproject.toml:20-21` (scripts)

- [ ] **Step 1: Criar os `__init__.py` vazios**

```bash
mkdir -p visibility/study/schema
printf '' > visibility/study/__init__.py
printf '' > visibility/study/schema/__init__.py
```

- [ ] **Step 2: Registrar pacotes e entry point no `pyproject.toml`**

Substituir o bloco `[project.scripts]` e `[tool.setuptools]` por:

```toml
[project.scripts]
medrank-visibility = "visibility.cli:main"
medrank-study = "visibility.study.cli:main"

[tool.setuptools]
packages = ["visibility", "visibility.schema", "visibility.collectors", "visibility.study", "visibility.study.schema"]

[tool.setuptools.package-data]
"visibility.schema" = ["*.json"]
"visibility.study.schema" = ["*.json"]
```

- [ ] **Step 3: Reinstalar editável para registrar o novo console script**

Run: `.venv/bin/pip install -e ".[dev]" >/dev/null && .venv/bin/python -c "import visibility.study; print('ok')"`
Expected: `ok`

- [ ] **Step 4: Commit**

```bash
git add pyproject.toml visibility/study/__init__.py visibility/study/schema/__init__.py
git commit -m "chore: scaffold visibility.study subpackage + medrank-study entry point"
```

---

## Task 1: Config do estudo (`study/config.py`)

**Files:**
- Create: `visibility/study/config.py`
- Test: `tests/test_study_config.py`

- [ ] **Step 1: Escrever o teste que falha**

```python
# tests/test_study_config.py
from visibility.study.config import StudyConfig, DemandMatrix, PROMPT_TEMPLATES

RAW = {
    "demand": {
        "especialidades": ["Dermatologia", "Cirurgia Plástica"],
        "cidades": ["São Paulo", "Rio de Janeiro"],
        "procedimentos": {"Dermatologia": ["botox", "preenchimento"],
                          "Cirurgia Plástica": ["rinoplastia"]},
        "prompt_tipos": ["melhor_especialista", "procedimento"],
        "engines": ["chatgpt", "gemini"],
        "repeticoes": 2,
    },
    "rosters": [
        {"especialidade": "Dermatologia", "arquivo": "rosters/derm.json"},
    ],
}

def test_from_dict_parses_all_fields():
    cfg = StudyConfig.from_dict(RAW)
    assert isinstance(cfg.demand, DemandMatrix)
    assert cfg.demand.especialidades == ["Dermatologia", "Cirurgia Plástica"]
    assert cfg.demand.procedimentos["Cirurgia Plástica"] == ["rinoplastia"]
    assert cfg.demand.repeticoes == 2
    assert cfg.rosters[0].especialidade == "Dermatologia"
    assert cfg.rosters[0].arquivo == "rosters/derm.json"

def test_repeticoes_defaults_to_one():
    raw = {"demand": {"especialidades": ["X"], "cidades": ["Y"],
                      "procedimentos": {}, "prompt_tipos": ["melhor_especialista"],
                      "engines": ["chatgpt"]}}
    cfg = StudyConfig.from_dict(raw)
    assert cfg.demand.repeticoes == 1
    assert cfg.rosters == []

def test_prompt_templates_cover_declared_tipos():
    for tipo in ["melhor_especialista", "procedimento", "confianca"]:
        assert tipo in PROMPT_TEMPLATES

def test_from_file_roundtrips(tmp_path):
    import json
    p = tmp_path / "study.json"
    p.write_text(json.dumps(RAW), encoding="utf-8")
    cfg = StudyConfig.from_file(str(p))
    assert cfg.demand.cidades == ["São Paulo", "Rio de Janeiro"]
```

- [ ] **Step 2: Rodar e confirmar falha**

Run: `.venv/bin/pytest tests/test_study_config.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'visibility.study.config'`

- [ ] **Step 3: Implementar `config.py`**

```python
# visibility/study/config.py
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
```

- [ ] **Step 4: Rodar e confirmar passagem**

Run: `.venv/bin/pytest tests/test_study_config.py -q`
Expected: PASS (4 passed)

- [ ] **Step 5: Commit**

```bash
git add visibility/study/config.py tests/test_study_config.py
git commit -m "feat(study): config do estudo (matriz de demanda + rosters)"
```

---

## Task 2: Construtor de prompts de demanda (`study/demand.py` — parte 1)

**Files:**
- Create: `visibility/study/demand.py`
- Test: `tests/test_study_demand.py`

- [ ] **Step 1: Escrever o teste que falha**

```python
# tests/test_study_demand.py
from visibility.study.config import DemandMatrix
from visibility.study.demand import build_demand_prompts, DemandPrompt

def _matrix(**kw):
    base = dict(especialidades=["Dermatologia"], cidades=["São Paulo"],
                procedimentos={"Dermatologia": ["botox", "acne"]},
                prompt_tipos=["melhor_especialista", "procedimento"],
                engines=["chatgpt"], repeticoes=1)
    base.update(kw)
    return DemandMatrix(**base)

def test_builds_one_prompt_per_non_procedure_tipo():
    prompts = build_demand_prompts(_matrix(prompt_tipos=["melhor_especialista"]))
    assert len(prompts) == 1
    p = prompts[0]
    assert isinstance(p, DemandPrompt)
    assert p.tipo == "melhor_especialista" and p.procedimento is None
    assert p.texto == "Quem é o melhor médico de Dermatologia em São Paulo?"

def test_procedure_tipo_expands_over_procedimentos():
    prompts = build_demand_prompts(_matrix(prompt_tipos=["procedimento"]))
    procs = sorted(p.procedimento for p in prompts)
    assert procs == ["acne", "botox"]
    assert all(p.tipo == "procedimento" for p in prompts)
    botox = next(p for p in prompts if p.procedimento == "botox")
    assert botox.texto == "Quem faz botox em São Paulo?"

def test_full_cartesian_product():
    m = _matrix(especialidades=["Dermatologia", "Oftalmologia"],
                cidades=["São Paulo", "Rio de Janeiro"],
                procedimentos={"Dermatologia": ["botox"], "Oftalmologia": ["lasik"]},
                prompt_tipos=["melhor_especialista", "procedimento"])
    # 2 esp × 2 cidades × (1 melhor + 1 procedimento por esp) = 8
    assert len(build_demand_prompts(m)) == 8
```

- [ ] **Step 2: Rodar e confirmar falha**

Run: `.venv/bin/pytest tests/test_study_demand.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'visibility.study.demand'`

- [ ] **Step 3: Implementar o construtor de prompts**

```python
# visibility/study/demand.py
from __future__ import annotations
from dataclasses import dataclass
from visibility.clients import LLMClient
from visibility.study.config import DemandMatrix, PROMPT_TEMPLATES

@dataclass
class DemandPrompt:
    especialidade: str
    cidade: str
    tipo: str
    procedimento: str | None
    texto: str

def build_demand_prompts(m: DemandMatrix) -> list[DemandPrompt]:
    out: list[DemandPrompt] = []
    for esp in m.especialidades:
        for cidade in m.cidades:
            for tipo in m.prompt_tipos:
                tmpl = PROMPT_TEMPLATES[tipo]
                if tipo == "procedimento":
                    for proc in m.procedimentos.get(esp, []):
                        out.append(DemandPrompt(
                            esp, cidade, tipo, proc,
                            tmpl.format(procedimento=proc, cidade=cidade)))
                else:
                    out.append(DemandPrompt(
                        esp, cidade, tipo, None,
                        tmpl.format(especialidade=esp, cidade=cidade)))
    return out
```

- [ ] **Step 4: Rodar e confirmar passagem**

Run: `.venv/bin/pytest tests/test_study_demand.py -q`
Expected: PASS (3 passed)

- [ ] **Step 5: Commit**

```bash
git add visibility/study/demand.py tests/test_study_demand.py
git commit -m "feat(study): construtor de prompts de demanda (visão do paciente)"
```

---

## Task 3: Runner de demanda (`study/demand.py` — parte 2)

**Files:**
- Modify: `visibility/study/demand.py` (adicionar `DemandResponse` e `DemandRunner`)
- Test: `tests/test_study_demand.py` (adicionar casos)

- [ ] **Step 1: Adicionar os testes que falham**

```python
# tests/test_study_demand.py  (append)
from visibility.study.demand import DemandResponse, DemandRunner

class ScriptedLLM:
    """Resposta canônica por substring do prompt (padrão de tests/test_ai_engines.py)."""
    def __init__(self, name, answers): self.name = name; self.answers = answers
    def ask(self, prompt: str) -> str:
        for needle, ans in self.answers.items():
            if needle in prompt:
                return ans
        return "Não tenho informação."

def test_runner_one_response_per_prompt_engine_rep():
    prompts = build_demand_prompts(_matrix(prompt_tipos=["melhor_especialista"]))
    engines = {"chatgpt": ScriptedLLM("chatgpt", {"melhor": "R1"}),
               "gemini": ScriptedLLM("gemini", {"melhor": "R2"})}
    runner = DemandRunner(engines=engines, repeticoes=2)
    res = runner.run(prompts, now="2026-06-28T14:00:00Z")
    # 1 prompt × 2 engines × 2 reps
    assert len(res) == 4
    assert {r.engine for r in res} == {"chatgpt", "gemini"}
    assert {r.rep for r in res} == {1, 2}
    r0 = res[0]
    assert isinstance(r0, DemandResponse)
    assert r0.capturado_em == "2026-06-28T14:00:00Z"
    assert r0.especialidade == "Dermatologia" and r0.cidade == "São Paulo"

def test_runner_passes_prompt_text_to_client():
    prompts = build_demand_prompts(_matrix(prompt_tipos=["procedimento"]))
    engines = {"chatgpt": ScriptedLLM("chatgpt",
               {"botox": "indico a Dra. A", "acne": "indico o Dr. B"})}
    res = DemandRunner(engines=engines).run(prompts, now="2026-06-28T14:00:00Z")
    botox = next(r for r in res if r.procedimento == "botox")
    assert botox.texto == "indico a Dra. A"
```

- [ ] **Step 2: Rodar e confirmar falha**

Run: `.venv/bin/pytest tests/test_study_demand.py -q`
Expected: FAIL — `ImportError: cannot import name 'DemandResponse'`

- [ ] **Step 3: Implementar `DemandResponse` e `DemandRunner`** (append em `demand.py`)

```python
# visibility/study/demand.py  (append)
@dataclass
class DemandResponse:
    especialidade: str
    cidade: str
    tipo: str
    procedimento: str | None
    engine: str
    rep: int
    capturado_em: str
    texto: str

class DemandRunner:
    def __init__(self, engines: dict[str, LLMClient], repeticoes: int = 1):
        self.engines = engines          # nome do motor -> cliente
        self.repeticoes = repeticoes

    def run(self, prompts: list[DemandPrompt], now: str) -> list[DemandResponse]:
        out: list[DemandResponse] = []
        for p in prompts:
            for engine_name, client in self.engines.items():
                for rep in range(1, self.repeticoes + 1):
                    texto = client.ask(p.texto)
                    out.append(DemandResponse(
                        especialidade=p.especialidade, cidade=p.cidade, tipo=p.tipo,
                        procedimento=p.procedimento, engine=engine_name, rep=rep,
                        capturado_em=now, texto=texto))
        return out
```

- [ ] **Step 4: Rodar e confirmar passagem**

Run: `.venv/bin/pytest tests/test_study_demand.py -q`
Expected: PASS (5 passed)

- [ ] **Step 5: Commit**

```bash
git add visibility/study/demand.py tests/test_study_demand.py
git commit -m "feat(study): runner de demanda roda prompts nos motores de IA"
```

---

## Task 4: Classificador — tipo de entidade citada (`study/classify.py` — parte 1)

**Files:**
- Create: `visibility/study/classify.py`
- Test: `tests/test_study_classify.py`

- [ ] **Step 1: Escrever o teste que falha**

```python
# tests/test_study_classify.py
from visibility.study.classify import classify_response, ResponseClassification

def test_medico_nominal_quando_cita_dr():
    c = classify_response("Recomendo a Dra. Ana Lima e o Dr. Bruno Souza.")
    assert isinstance(c, ResponseClassification)
    assert c.tipo_resposta == "medico_nominal"
    assert "Dra. Ana Lima" in c.medicos and "Dr. Bruno Souza" in c.medicos

def test_marketplace_quando_so_cita_plataforma():
    c = classify_response("Busque no Doctoralia ou no BoaConsulta por dermatologistas.")
    assert c.tipo_resposta == "marketplace"
    assert "doctoralia" in c.marketplaces and "boaconsulta" in c.marketplaces
    assert c.medicos == []

def test_hospital_tem_prioridade_sobre_clinica_quando_sem_medico_e_sem_marketplace():
    c = classify_response("Procure o Hospital Albert Einstein, que tem ótima clínica.")
    assert c.tipo_resposta == "hospital"
    assert c.tem_hospital is True and c.tem_clinica is True

def test_clinica_quando_so_clinica():
    c = classify_response("Procure uma boa clínica de dermatologia na sua região.")
    assert c.tipo_resposta == "clinica"

def test_nenhum_quando_recusa():
    c = classify_response("Não tenho informações suficientes para recomendar um profissional.")
    assert c.tipo_resposta == "nenhum"
    assert c.medicos == [] and c.marketplaces == []

def test_conteudo_generico_quando_so_orienta():
    c = classify_response("Verifique o registro no CRM e leia avaliações antes de escolher.")
    assert c.tipo_resposta == "conteudo_generico"

def test_medico_tem_prioridade_mesmo_com_marketplace():
    c = classify_response("A Dra. Ana Lima é ótima; o perfil dela está no Doctoralia.")
    assert c.tipo_resposta == "medico_nominal"
    assert "doctoralia" in c.marketplaces   # ainda registrado para share of voice
```

- [ ] **Step 2: Rodar e confirmar falha**

Run: `.venv/bin/pytest tests/test_study_classify.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'visibility.study.classify'`

- [ ] **Step 3: Implementar a tipagem de entidade**

```python
# visibility/study/classify.py
from __future__ import annotations
import re
from dataclasses import dataclass, field
from visibility.names import mentioned_names

# id canônico -> variações textuais (lowercase, sem exigir acento exato)
MARKETPLACES: dict[str, list[str]] = {
    "doctoralia": ["doctoralia"],
    "boaconsulta": ["boaconsulta", "boa consulta"],
    "google_maps": ["google maps", "google meu negócio", "google meu negocio"],
}

_RECUSA = re.compile(
    r"não (tenho|possuo|disponho)|nao (tenho|possuo)|não posso recomendar|"
    r"nao posso recomendar|sem informaç|sem informac", re.IGNORECASE)
_HOSPITAL = re.compile(r"\bhospital\b", re.IGNORECASE)
_CLINICA = re.compile(r"\bcl[íi]nica", re.IGNORECASE)

@dataclass
class ResponseClassification:
    tipo_resposta: str                 # medico_nominal|marketplace|hospital|clinica|conteudo_generico|nenhum
    medicos: list[str] = field(default_factory=list)
    marketplaces: list[str] = field(default_factory=list)
    tem_clinica: bool = False
    tem_hospital: bool = False
    cfm_risco: list[str] = field(default_factory=list)   # preenchido na parte 2

def _norm(s: str) -> str:
    return s.lower()

def _marketplaces_in(text: str) -> list[str]:
    low = _norm(text)
    out: list[str] = []
    for mid, variants in MARKETPLACES.items():
        if any(v in low for v in variants) and mid not in out:
            out.append(mid)
    return out

def classify_response(texto: str) -> ResponseClassification:
    medicos = mentioned_names(texto)
    marketplaces = _marketplaces_in(texto)
    tem_hospital = bool(_HOSPITAL.search(texto))
    tem_clinica = bool(_CLINICA.search(texto))
    recusa = bool(_RECUSA.search(texto))

    if medicos:
        tipo = "medico_nominal"
    elif marketplaces:
        tipo = "marketplace"
    elif tem_hospital:
        tipo = "hospital"
    elif tem_clinica:
        tipo = "clinica"
    elif recusa:
        tipo = "nenhum"
    else:
        tipo = "conteudo_generico"

    return ResponseClassification(
        tipo_resposta=tipo, medicos=medicos, marketplaces=marketplaces,
        tem_clinica=tem_clinica, tem_hospital=tem_hospital)
```

- [ ] **Step 4: Rodar e confirmar passagem**

Run: `.venv/bin/pytest tests/test_study_classify.py -q`
Expected: PASS (7 passed)

- [ ] **Step 5: Commit**

```bash
git add visibility/study/classify.py tests/test_study_classify.py
git commit -m "feat(study): classificador tipa entidade citada na resposta da IA"
```

---

## Task 5: Classificador — flag de risco-CFM (`study/classify.py` — parte 2)

**Files:**
- Modify: `visibility/study/classify.py` (adicionar `CFM_FRASES_RISCO`, `cfm_risk`, preencher `cfm_risco`)
- Test: `tests/test_study_classify.py` (adicionar casos)

- [ ] **Step 1: Adicionar os testes que falham**

```python
# tests/test_study_classify.py  (append)
from visibility.study.classify import cfm_risk

def test_cfm_flag_resultado_garantido():
    achados = cfm_risk("Esse procedimento tem resultado garantido e é 100% indolor.")
    assert any("garantido" in a for a in achados)
    assert any("indolor" in a or "100%" in a for a in achados)

def test_cfm_flag_superlativo_com_escopo():
    achados = cfm_risk("É o melhor dermatologista do Brasil, sem dúvida.")
    assert achados   # "melhor ... do brasil" é superlativo vedado

def test_cfm_sem_flag_em_texto_neutro():
    assert cfm_risk("Verifique o CRM e leia avaliações de pacientes.") == []

def test_classify_preenche_cfm_risco():
    c = classify_response("A Dra. Ana garante cura total e resultado garantido.")
    assert c.tipo_resposta == "medico_nominal"
    assert c.cfm_risco   # não-vazio
```

- [ ] **Step 2: Rodar e confirmar falha**

Run: `.venv/bin/pytest tests/test_study_classify.py -q`
Expected: FAIL — `ImportError: cannot import name 'cfm_risk'`

- [ ] **Step 3: Implementar `cfm_risk` e ligar em `classify_response`**

Adicionar perto do topo de `classify.py` (após os regex existentes):

```python
# Frases que sinalizam possível violação do CFM (heurística; confirmação por LLM é etapa futura).
CFM_FRASES_RISCO: list[re.Pattern] = [
    re.compile(r"resultado[s]? garantido", re.IGNORECASE),
    re.compile(r"cura (total|garantida)", re.IGNORECASE),
    re.compile(r"garante (o|a|um|uma)?\s*(resultado|cura|sucesso)", re.IGNORECASE),
    re.compile(r"100\s*%\s*(indolor|seguro|eficaz|garantido)", re.IGNORECASE),
    re.compile(r"\bindolor\b", re.IGNORECASE),
    re.compile(r"sem (riscos|dor|cicatriz)", re.IGNORECASE),
    re.compile(r"\bmilagr", re.IGNORECASE),
    # superlativo com escopo geográfico (vedado quando afirma "o melhor da cidade/estado/país")
    re.compile(r"melhor\s+\w+\s+d[oa]\s+(brasil|cidade|estado|pa[íi]s|mundo)", re.IGNORECASE),
]

def cfm_risk(texto: str) -> list[str]:
    achados: list[str] = []
    for pat in CFM_FRASES_RISCO:
        m = pat.search(texto)
        if m:
            achados.append(m.group(0).strip().lower())
    return achados
```

E em `classify_response`, antes do `return`, calcular e passar:

```python
    cfm = cfm_risk(texto)
    return ResponseClassification(
        tipo_resposta=tipo, medicos=medicos, marketplaces=marketplaces,
        tem_clinica=tem_clinica, tem_hospital=tem_hospital, cfm_risco=cfm)
```

- [ ] **Step 4: Rodar e confirmar passagem**

Run: `.venv/bin/pytest tests/test_study_classify.py -q`
Expected: PASS (11 passed)

- [ ] **Step 5: Commit**

```bash
git add visibility/study/classify.py tests/test_study_classify.py
git commit -m "feat(study): heurística de risco-CFM nas respostas da IA"
```

---

## Task 6: Agregação do lado da demanda (`study/aggregate.py` — parte 1)

**Files:**
- Create: `visibility/study/aggregate.py`
- Test: `tests/test_study_aggregate.py`

- [ ] **Step 1: Escrever o teste que falha**

```python
# tests/test_study_aggregate.py
from visibility.study.demand import DemandResponse
from visibility.study.aggregate import aggregate_demand, DemandAggregate

def _r(esp, cidade, tipo, engine, texto, rep=1, proc=None):
    return DemandResponse(esp, cidade, tipo, proc, engine, rep,
                          "2026-06-28T14:00:00Z", texto)

def test_demand_pcts_e_contagens():
    res = [
        _r("Dermatologia", "SP", "melhor_especialista", "chatgpt", "Recomendo a Dra. Ana Lima."),
        _r("Dermatologia", "SP", "melhor_especialista", "gemini", "Busque no Doctoralia."),
        _r("Dermatologia", "SP", "melhor_especialista", "perplexity",
           "Não tenho informações para recomendar."),
    ]
    agg = aggregate_demand(res)
    assert isinstance(agg, DemandAggregate)
    assert agg.total_respostas == 3
    assert round(agg.pct_com_medico_nominal, 3) == round(1/3, 3)
    assert round(agg.pct_marketplace, 3) == round(1/3, 3)
    assert round(agg.pct_nenhum, 3) == round(1/3, 3)

def test_demand_top_medicos_e_marketplaces():
    res = [
        _r("Dermatologia", "SP", "melhor_especialista", "chatgpt", "Indico a Dra. Ana Lima."),
        _r("Dermatologia", "RJ", "melhor_especialista", "chatgpt", "Indico a Dra. Ana Lima."),
        _r("Dermatologia", "SP", "melhor_especialista", "gemini", "Veja no Doctoralia."),
    ]
    agg = aggregate_demand(res)
    assert agg.top_medicos[0] == ["Dra. Ana Lima", 2]
    assert ["doctoralia", 1] in agg.top_marketplaces

def test_demand_por_especialidade():
    res = [
        _r("Dermatologia", "SP", "melhor_especialista", "chatgpt", "Dra. Ana Lima."),
        _r("Oftalmologia", "SP", "melhor_especialista", "chatgpt", "Busque no Doctoralia."),
    ]
    agg = aggregate_demand(res)
    assert agg.por_especialidade["Dermatologia"]["pct_com_medico_nominal"] == 1.0
    assert agg.por_especialidade["Oftalmologia"]["pct_com_medico_nominal"] == 0.0

def test_demand_cfm_risco_pct():
    res = [
        _r("Dermatologia", "SP", "melhor_especialista", "chatgpt",
           "A Dra. Ana garante resultado garantido."),
        _r("Dermatologia", "SP", "melhor_especialista", "gemini", "Dra. Bia Costa atende lá."),
    ]
    agg = aggregate_demand(res)
    assert round(agg.cfm_risco_pct, 3) == 0.5

def test_demand_divergencia_motores():
    # mesma célula (esp/cidade/tipo), motores nomeiam médicos diferentes -> divergência
    res = [
        _r("Dermatologia", "SP", "melhor_especialista", "chatgpt", "Dra. Ana Lima."),
        _r("Dermatologia", "SP", "melhor_especialista", "gemini", "Dr. Bruno Souza."),
    ]
    agg = aggregate_demand(res)
    assert agg.divergencia_motores_pct == 1.0
```

- [ ] **Step 2: Rodar e confirmar falha**

Run: `.venv/bin/pytest tests/test_study_aggregate.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'visibility.study.aggregate'`

- [ ] **Step 3: Implementar `aggregate_demand`**

```python
# visibility/study/aggregate.py
from __future__ import annotations
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from visibility.study.demand import DemandResponse
from visibility.study.classify import classify_response

@dataclass
class DemandAggregate:
    total_respostas: int
    pct_com_medico_nominal: float
    pct_marketplace: float
    pct_nenhum: float
    cfm_risco_pct: float
    divergencia_motores_pct: float
    por_especialidade: dict[str, dict] = field(default_factory=dict)
    top_medicos: list[list] = field(default_factory=list)        # [[nome, contagem], ...]
    top_marketplaces: list[list] = field(default_factory=list)   # [[id, contagem], ...]

def _safe_div(a: float, b: float) -> float:
    return a / b if b else 0.0

def aggregate_demand(responses: list[DemandResponse], top_n: int = 20) -> DemandAggregate:
    classifs = [(r, classify_response(r.texto)) for r in responses]
    total = len(classifs)

    n_medico = sum(1 for _, c in classifs if c.tipo_resposta == "medico_nominal")
    n_market = sum(1 for _, c in classifs if c.tipo_resposta == "marketplace")
    n_nenhum = sum(1 for _, c in classifs if c.tipo_resposta == "nenhum")
    n_cfm = sum(1 for _, c in classifs if c.cfm_risco)

    medicos: Counter[str] = Counter()
    markets: Counter[str] = Counter()
    for _, c in classifs:
        for m in c.medicos:
            medicos[m] += 1
        for mk in c.marketplaces:
            markets[mk] += 1

    # por especialidade
    por_esp: dict[str, dict] = {}
    by_esp: dict[str, list] = defaultdict(list)
    for r, c in classifs:
        by_esp[r.especialidade].append(c)
    for esp, cs in by_esp.items():
        n = len(cs)
        por_esp[esp] = {
            "total": n,
            "pct_com_medico_nominal": _safe_div(
                sum(1 for c in cs if c.tipo_resposta == "medico_nominal"), n),
            "pct_marketplace": _safe_div(
                sum(1 for c in cs if c.tipo_resposta == "marketplace"), n),
            "pct_nenhum": _safe_div(sum(1 for c in cs if c.tipo_resposta == "nenhum"), n),
            "cfm_risco_pct": _safe_div(sum(1 for c in cs if c.cfm_risco), n),
        }

    # divergência entre motores: por célula (esp,cidade,tipo,procedimento),
    # olha o "top médico" (1º citado) de cada motor; diverge se há >1 médico distinto.
    cells: dict[tuple, dict[str, str | None]] = defaultdict(dict)
    for r, c in classifs:
        key = (r.especialidade, r.cidade, r.tipo, r.procedimento)
        top = c.medicos[0] if c.medicos else None
        cells[key][r.engine] = top
    multi = [d for d in cells.values() if len(d) >= 2]
    divergentes = sum(1 for d in multi if len({v for v in d.values() if v}) > 1
                      or any(v is None for v in d.values()))
    divergencia = _safe_div(divergentes, len(multi))

    return DemandAggregate(
        total_respostas=total,
        pct_com_medico_nominal=_safe_div(n_medico, total),
        pct_marketplace=_safe_div(n_market, total),
        pct_nenhum=_safe_div(n_nenhum, total),
        cfm_risco_pct=_safe_div(n_cfm, total),
        divergencia_motores_pct=divergencia,
        por_especialidade=por_esp,
        top_medicos=[[n, c] for n, c in medicos.most_common(top_n)],
        top_marketplaces=[[n, c] for n, c in markets.most_common(top_n)],
    )
```

- [ ] **Step 4: Rodar e confirmar passagem**

Run: `.venv/bin/pytest tests/test_study_aggregate.py -q`
Expected: PASS (5 passed)

- [ ] **Step 5: Commit**

```bash
git add visibility/study/aggregate.py tests/test_study_aggregate.py
git commit -m "feat(study): agregação do lado da demanda (share of voice, CFM, divergência)"
```

---

## Task 7: Batch do Visibility Score (`study/supply.py`)

**Files:**
- Create: `visibility/study/supply.py`
- Test: `tests/test_study_supply.py`

- [ ] **Step 1: Escrever o teste que falha**

```python
# tests/test_study_supply.py
import json
from visibility.study.config import RosterSpec
from visibility.study.supply import load_roster, run_supply
from visibility.models import DoctorMeta, VisibilityReport
from visibility.collectors.base import CollectorContext, CollectorOutput, SignalResult
from visibility.models import Status

def _doc(nome):
    return {"nome": nome, "especialidade_principal": "Dermatologia",
            "cidade": "São Paulo", "uf": "SP", "procedimentos_foco": ["botox"]}

def test_load_roster(tmp_path):
    p = tmp_path / "derm.json"
    p.write_text(json.dumps([_doc("Dra. Ana Lima"), _doc("Dr. Bruno Souza")]),
                 encoding="utf-8")
    docs = load_roster(str(p))
    assert [d.nome for d in docs] == ["Dra. Ana Lima", "Dr. Bruno Souza"]
    assert isinstance(docs[0], DoctorMeta)

class _FakeCollector:
    category = "site_conteudo"
    def collect(self, ctx: CollectorContext) -> CollectorOutput:
        return CollectorOutput(signals=[SignalResult(
            "tem_site", "Tem site", Status.pass_, True, 12.5, 0.9, "stub",
            [{"fonte": "stub", "resumo": "ok"}])])

def test_run_supply_one_report_per_doctor(tmp_path):
    p = tmp_path / "derm.json"
    p.write_text(json.dumps([_doc("Dra. Ana Lima"), _doc("Dr. Bruno Souza")]),
                 encoding="utf-8")
    rosters = [RosterSpec("Dermatologia", str(p))]
    out = run_supply(rosters, collector_factory=lambda s: [_FakeCollector()],
                     settings=None, now="2026-06-28T14:00:00Z", pipeline_version="0.1.0")
    assert set(out) == {"Dermatologia"}
    reports = out["Dermatologia"]
    assert len(reports) == 2
    assert all(isinstance(r, VisibilityReport) for r in reports)
    assert reports[0].score.total > 0   # FakeCollector dá 1 sinal pass
```

- [ ] **Step 2: Rodar e confirmar falha**

Run: `.venv/bin/pytest tests/test_study_supply.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'visibility.study.supply'`

- [ ] **Step 3: Implementar `supply.py`**

```python
# visibility/study/supply.py
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
```

- [ ] **Step 4: Rodar e confirmar passagem**

Run: `.venv/bin/pytest tests/test_study_supply.py -q`
Expected: PASS (2 passed)

- [ ] **Step 5: Commit**

```bash
git add visibility/study/supply.py tests/test_study_supply.py
git commit -m "feat(study): batch do Visibility Score sobre rosters de médicos"
```

---

## Task 8: Agregação do lado da oferta (`study/aggregate.py` — parte 2)

**Files:**
- Modify: `visibility/study/aggregate.py` (adicionar `aggregate_supply` + `SupplyAggregate`)
- Test: `tests/test_study_aggregate.py` (adicionar casos)

- [ ] **Step 1: Adicionar os testes que falham**

```python
# tests/test_study_aggregate.py  (append)
from visibility.study.aggregate import aggregate_supply, SupplyAggregate
from visibility.models import (
    VisibilityReport, Meta, RunMeta, DoctorMeta, Score, CategoriaScore)

def _report(total, cats):
    doc = DoctorMeta(nome="X", especialidade_principal="Dermatologia",
                     cidade="SP", uf="SP")
    return VisibilityReport(
        meta=Meta(doctor=doc, run=RunMeta(gerado_em="t", pipeline_version="0.1.0")),
        score=Score(total=total, max=100,
                    tier="Ouro" if total >= 70 else "Prata" if total >= 40 else "Bronze",
                    categorias={k: CategoriaScore(score=v, max=25) for k, v in cats.items()}),
        categorias={}, concorrentes={"resumo": "", "ofensores_recorrentes": []})

def test_supply_distribuicao():
    reports = {"Dermatologia": [
        _report(20, {"visibilidade_ia": 5}),
        _report(40, {"visibilidade_ia": 10}),
        _report(60, {"visibilidade_ia": 20}),
        _report(80, {"visibilidade_ia": 25}),
    ]}
    agg = aggregate_supply(reports)
    assert isinstance(agg, SupplyAggregate)
    d = agg.por_especialidade["Dermatologia"]
    assert d["n"] == 4
    assert d["mediana"] == 50.0
    assert d["pct_abaixo_50"] == 0.5
    assert d["media_por_categoria"]["visibilidade_ia"] == 15.0

def test_supply_top_decil_profile():
    reports = {"Dermatologia": [_report(10 * i, {"visibilidade_ia": float(i)})
                                for i in range(1, 11)]}  # 10..100
    agg = aggregate_supply(reports)
    d = agg.por_especialidade["Dermatologia"]
    # top 10% = 1 médico (o de score 100), media_por_categoria do topo destaca-se
    assert d["top_decil"]["n"] >= 1
    assert d["top_decil"]["media_por_categoria"]["visibilidade_ia"] >= d["media_por_categoria"]["visibilidade_ia"]
```

- [ ] **Step 2: Rodar e confirmar falha**

Run: `.venv/bin/pytest tests/test_study_aggregate.py -q`
Expected: FAIL — `ImportError: cannot import name 'aggregate_supply'`

- [ ] **Step 3: Implementar `aggregate_supply`** (append em `aggregate.py`)

```python
# visibility/study/aggregate.py  (append)
import math
from statistics import median
from visibility.models import VisibilityReport

@dataclass
class SupplyAggregate:
    por_especialidade: dict[str, dict] = field(default_factory=dict)

def _percentile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    s = sorted(values)
    if len(s) == 1:
        return float(s[0])
    pos = q * (len(s) - 1)
    lo = math.floor(pos)
    hi = math.ceil(pos)
    if lo == hi:
        return float(s[lo])
    return float(s[lo] + (s[hi] - s[lo]) * (pos - lo))

def _media_categorias(reports: list[VisibilityReport]) -> dict[str, float]:
    soma: dict[str, float] = defaultdict(float)
    cont: dict[str, int] = defaultdict(int)
    for r in reports:
        for key, cs in r.score.categorias.items():
            soma[key] += cs.score
            cont[key] += 1
    return {k: round(soma[k] / cont[k], 4) for k in soma}

def aggregate_supply(reports_by_esp: dict[str, list[VisibilityReport]]) -> SupplyAggregate:
    por_esp: dict[str, dict] = {}
    for esp, reports in reports_by_esp.items():
        totais = [r.score.total for r in reports]
        n = len(reports)
        limiar = _percentile(totais, 0.9) if n > 1 else (totais[0] if totais else 0.0)
        top = [r for r in reports if r.score.total >= limiar] or reports[:]
        por_esp[esp] = {
            "n": n,
            "mediana": round(median(totais), 4) if totais else 0.0,
            "p25": round(_percentile(totais, 0.25), 4),
            "p75": round(_percentile(totais, 0.75), 4),
            "pct_abaixo_50": round(sum(1 for t in totais if t < 50) / n, 4) if n else 0.0,
            "media_por_categoria": _media_categorias(reports),
            "top_decil": {
                "n": len(top),
                "media_por_categoria": _media_categorias(top),
            },
        }
    return SupplyAggregate(por_especialidade=por_esp)
```

- [ ] **Step 4: Rodar e confirmar passagem**

Run: `.venv/bin/pytest tests/test_study_aggregate.py -q`
Expected: PASS (7 passed)

- [ ] **Step 5: Commit**

```bash
git add visibility/study/aggregate.py tests/test_study_aggregate.py
git commit -m "feat(study): agregação do lado da oferta (distribuição de scores + top decil)"
```

---

## Task 9: Modelo de custo (`study/cost.py`)

**Files:**
- Create: `visibility/study/cost.py`
- Test: `tests/test_study_cost.py`

- [ ] **Step 1: Escrever o teste que falha**

```python
# tests/test_study_cost.py
from visibility.study.config import DemandMatrix
from visibility.study.cost import estimate_demand_calls, estimate_supply_calls, estimate_cost

def _matrix():
    return DemandMatrix(
        especialidades=["Dermatologia"], cidades=["SP", "RJ"],
        procedimentos={"Dermatologia": ["botox", "acne"]},
        prompt_tipos=["melhor_especialista", "procedimento"],
        engines=["chatgpt", "gemini"], repeticoes=3)

def test_demand_calls():
    # prompts: 1 esp × 2 cidades × (1 melhor + 2 procedimentos) = 6 prompts
    # chamadas: 6 × 2 engines × 3 reps = 36
    assert estimate_demand_calls(_matrix()) == 36

def test_supply_calls_usa_premissas():
    # 50 médicos, 4 procedimentos médios, 2 motores -> por médico:
    # (1 marca + 4 proc) × 2 motores = 10 chamadas LLM + 1 serp + 1 places = 12
    calls = estimate_supply_calls(n_medicos=50, media_procedimentos=4, n_motores=2)
    assert calls["llm"] == 50 * 10
    assert calls["serpapi"] == 50
    assert calls["places"] == 50

def test_estimate_cost_soma_em_usd():
    custo = estimate_cost(llm=100, serpapi=50, places=50)
    # constantes default: llm 0.02, serpapi 0.01, places 0.005
    assert round(custo, 4) == round(100 * 0.02 + 50 * 0.01 + 50 * 0.005, 4)
```

- [ ] **Step 2: Rodar e confirmar falha**

Run: `.venv/bin/pytest tests/test_study_cost.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'visibility.study.cost'`

- [ ] **Step 3: Implementar `cost.py`**

```python
# visibility/study/cost.py
from __future__ import annotations
from visibility.study.config import DemandMatrix
from visibility.study.demand import build_demand_prompts

# Preços aproximados por chamada, em USD. Ajustar num só lugar conforme contratos reais.
CUSTO_LLM = 0.02
CUSTO_SERPAPI = 0.01
CUSTO_PLACES = 0.005

def estimate_demand_calls(m: DemandMatrix) -> int:
    return len(build_demand_prompts(m)) * len(m.engines) * m.repeticoes

def estimate_supply_calls(n_medicos: int, media_procedimentos: int, n_motores: int
                          ) -> dict[str, int]:
    llm_por_medico = (1 + media_procedimentos) * n_motores   # 1 prompt de marca + procedimentos
    return {"llm": n_medicos * llm_por_medico,
            "serpapi": n_medicos, "places": n_medicos}

def estimate_cost(llm: int = 0, serpapi: int = 0, places: int = 0) -> float:
    return llm * CUSTO_LLM + serpapi * CUSTO_SERPAPI + places * CUSTO_PLACES
```

- [ ] **Step 4: Rodar e confirmar passagem**

Run: `.venv/bin/pytest tests/test_study_cost.py -q`
Expected: PASS (3 passed)

- [ ] **Step 5: Commit**

```bash
git add visibility/study/cost.py tests/test_study_cost.py
git commit -m "feat(study): modelo de custo de API para dimensionar a amostra"
```

---

## Task 10: Export + JSON Schema do `aggregates.json` (`study/export.py` + schema)

**Files:**
- Create: `visibility/study/schema/study_aggregates_1_0.json`
- Create: `visibility/study/export.py`
- Test: `tests/test_study_export.py`

- [ ] **Step 1: Escrever o teste que falha**

```python
# tests/test_study_export.py
from visibility.study.aggregate import DemandAggregate, SupplyAggregate
from visibility.study.export import build_aggregates, validate_aggregates, SchemaValidationError
import pytest

def _demand():
    return DemandAggregate(
        total_respostas=3, pct_com_medico_nominal=0.33, pct_marketplace=0.33,
        pct_nenhum=0.34, cfm_risco_pct=0.1, divergencia_motores_pct=0.5,
        por_especialidade={"Dermatologia": {"total": 3, "pct_com_medico_nominal": 0.33,
                            "pct_marketplace": 0.33, "pct_nenhum": 0.34, "cfm_risco_pct": 0.1}},
        top_medicos=[["Dra. Ana Lima", 2]], top_marketplaces=[["doctoralia", 1]])

def _supply():
    return SupplyAggregate(por_especialidade={"Dermatologia": {
        "n": 4, "mediana": 50.0, "p25": 30.0, "p75": 70.0, "pct_abaixo_50": 0.5,
        "media_por_categoria": {"visibilidade_ia": 15.0},
        "top_decil": {"n": 1, "media_por_categoria": {"visibilidade_ia": 25.0}}}})

def test_build_aggregates_estrutura_e_sem_pii():
    data = build_aggregates(_demand(), _supply(), now="2026-06-28T14:00:00Z",
                            pipeline_version="0.1.0")
    assert data["schema_version"] == "1.0"
    assert data["meta"]["gerado_em"] == "2026-06-28T14:00:00Z"
    assert data["demanda"]["total_respostas"] == 3
    assert data["oferta"]["por_especialidade"]["Dermatologia"]["n"] == 4
    # top_medicos é share-of-voice agregado (aparece), mas NÃO há blocos por-médico nominais na oferta
    assert "medicos" not in data["oferta"]

def test_validate_aggregates_aceita_documento_valido():
    data = build_aggregates(_demand(), _supply(), now="2026-06-28T14:00:00Z",
                            pipeline_version="0.1.0")
    validate_aggregates(data)   # não levanta

def test_validate_aggregates_rejeita_documento_invalido():
    with pytest.raises(SchemaValidationError):
        validate_aggregates({"schema_version": "1.0"})   # faltam campos obrigatórios
```

- [ ] **Step 2: Rodar e confirmar falha**

Run: `.venv/bin/pytest tests/test_study_export.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'visibility.study.export'`

- [ ] **Step 3: Criar o JSON Schema**

```json
// visibility/study/schema/study_aggregates_1_0.json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "MedRank Study Aggregates",
  "type": "object",
  "required": ["schema_version", "meta", "demanda", "oferta"],
  "additionalProperties": false,
  "properties": {
    "schema_version": {"const": "1.0"},
    "meta": {
      "type": "object",
      "required": ["gerado_em", "pipeline_version"],
      "additionalProperties": false,
      "properties": {
        "gerado_em": {"type": "string"},
        "pipeline_version": {"type": "string"},
        "idioma": {"type": "string"}
      }
    },
    "demanda": {
      "type": "object",
      "required": ["total_respostas", "pct_com_medico_nominal", "pct_marketplace",
                   "pct_nenhum", "cfm_risco_pct", "divergencia_motores_pct",
                   "por_especialidade", "top_medicos", "top_marketplaces"],
      "additionalProperties": false,
      "properties": {
        "total_respostas": {"type": "integer", "minimum": 0},
        "pct_com_medico_nominal": {"type": "number"},
        "pct_marketplace": {"type": "number"},
        "pct_nenhum": {"type": "number"},
        "cfm_risco_pct": {"type": "number"},
        "divergencia_motores_pct": {"type": "number"},
        "por_especialidade": {"type": "object"},
        "top_medicos": {"type": "array", "items": {"type": "array"}},
        "top_marketplaces": {"type": "array", "items": {"type": "array"}}
      }
    },
    "oferta": {
      "type": "object",
      "required": ["por_especialidade"],
      "additionalProperties": false,
      "properties": {
        "por_especialidade": {"type": "object"}
      }
    }
  }
}
```

- [ ] **Step 4: Implementar `export.py`**

```python
# visibility/study/export.py
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
```

- [ ] **Step 5: Rodar e confirmar passagem**

Run: `.venv/bin/pytest tests/test_study_export.py -q`
Expected: PASS (3 passed)

- [ ] **Step 6: Commit**

```bash
git add visibility/study/export.py visibility/study/schema/study_aggregates_1_0.json tests/test_study_export.py
git commit -m "feat(study): export + JSON Schema do aggregates.json (sem PII)"
```

---

## Task 11: CLI `medrank-study` (`study/cli.py`)

**Files:**
- Create: `visibility/study/cli.py`
- Test: `tests/test_study_cli.py`

- [ ] **Step 1: Escrever o teste que falha**

```python
# tests/test_study_cli.py
import json
from visibility.study.cli import run

def _study_cfg(tmp_path, roster_path):
    cfg = {
        "demand": {"especialidades": ["Dermatologia"], "cidades": ["SP"],
                   "procedimentos": {"Dermatologia": ["botox"]},
                   "prompt_tipos": ["melhor_especialista", "procedimento"],
                   "engines": ["chatgpt"], "repeticoes": 1},
        "rosters": [{"especialidade": "Dermatologia", "arquivo": roster_path}],
    }
    p = tmp_path / "study.json"
    p.write_text(json.dumps(cfg), encoding="utf-8")
    return str(p)

def test_plan_imprime_estimativa(tmp_path, capsys):
    cfg = _study_cfg(tmp_path, "rosters/x.json")
    rc = run(["plan", "--config", cfg, "--roster-size", "50"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "chamadas" in out.lower() and "usd" in out.lower()

def test_demand_escreve_respostas(tmp_path):
    cfg = _study_cfg(tmp_path, "rosters/x.json")
    out = tmp_path / "raw_demand.json"
    # engine factory scriptado: nunca toca a rede
    def fake_engines(settings):
        class L:
            name = "chatgpt"
            def ask(self, p): return "Indico a Dra. Ana Lima."
        return {"chatgpt": L()}
    rc = run(["demand", "--config", cfg, "--out", str(out),
              "--now", "2026-06-28T14:00:00Z"], engines_factory=fake_engines)
    assert rc == 0
    data = json.loads(out.read_text(encoding="utf-8"))
    # 1 melhor + 1 procedimento = 2 prompts × 1 engine × 1 rep
    assert len(data) == 2
    assert data[0]["engine"] == "chatgpt"

def test_aggregate_gera_aggregates_valido(tmp_path):
    # respostas de demanda mínimas
    demand = [{"especialidade": "Dermatologia", "cidade": "SP",
               "tipo": "melhor_especialista", "procedimento": None,
               "engine": "chatgpt", "rep": 1, "capturado_em": "t",
               "texto": "Indico a Dra. Ana Lima."}]
    dpath = tmp_path / "raw_demand.json"
    dpath.write_text(json.dumps(demand), encoding="utf-8")
    # supply vazio é válido (sem rosters rodados)
    spath = tmp_path / "raw_supply.json"
    spath.write_text(json.dumps({}), encoding="utf-8")
    out = tmp_path / "aggregates.json"
    rc = run(["aggregate", "--demand", str(dpath), "--supply", str(spath),
              "--out", str(out), "--now", "2026-06-28T14:00:00Z"])
    assert rc == 0
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema_version"] == "1.0"
    assert data["demanda"]["total_respostas"] == 1
```

- [ ] **Step 2: Rodar e confirmar falha**

Run: `.venv/bin/pytest tests/test_study_cli.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'visibility.study.cli'`

- [ ] **Step 3: Implementar `cli.py`**

```python
# visibility/study/cli.py
from __future__ import annotations
import argparse
import json
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from typing import Callable
from visibility.config import Settings, build_engines, build_collectors
from visibility.models import VisibilityReport
from visibility.study.config import StudyConfig
from visibility.study.demand import build_demand_prompts, DemandRunner, DemandResponse
from visibility.study.supply import run_supply
from visibility.study.aggregate import aggregate_demand, aggregate_supply
from visibility.study.cost import (estimate_demand_calls, estimate_supply_calls,
                                   estimate_cost)
from visibility.study.export import build_aggregates, validate_aggregates

def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def _write(path: str | None, text: str) -> None:
    if path:
        open(path, "w", encoding="utf-8").write(text)
    else:
        sys.stdout.write(text + "\n")

def _cmd_plan(args) -> int:
    cfg = StudyConfig.from_file(args.config)
    n_demand = estimate_demand_calls(cfg.demand)
    supply = estimate_supply_calls(
        n_medicos=args.roster_size * max(len(cfg.rosters), 1),
        media_procedimentos=args.media_procedimentos, n_motores=len(cfg.demand.engines))
    custo = estimate_cost(llm=n_demand + supply["llm"],
                          serpapi=supply["serpapi"], places=supply["places"])
    print(f"Demanda: {n_demand} chamadas LLM")
    print(f"Oferta:  {supply['llm']} LLM + {supply['serpapi']} SerpApi + "
          f"{supply['places']} Places")
    print(f"Custo estimado: USD {custo:.2f}")
    return 0

def _cmd_demand(args, engines_factory) -> int:
    cfg = StudyConfig.from_file(args.config)
    now = args.now or _utc_now()
    engines = engines_factory(Settings.from_env())
    # respeita o subconjunto declarado na matriz
    engines = {k: v for k, v in engines.items() if k in cfg.demand.engines}
    prompts = build_demand_prompts(cfg.demand)
    responses = DemandRunner(engines=engines, repeticoes=cfg.demand.repeticoes).run(prompts, now)
    _write(args.out, json.dumps([asdict(r) for r in responses], ensure_ascii=False, indent=2))
    return 0

def _cmd_supply(args, collector_factory) -> int:
    cfg = StudyConfig.from_file(args.config)
    now = args.now or _utc_now()
    reports = run_supply(cfg.rosters, collector_factory=collector_factory,
                         settings=Settings.from_env(), now=now,
                         pipeline_version=args.pipeline_version)
    serial = {esp: [r.model_dump(mode="json", exclude_none=True) for r in rs]
              for esp, rs in reports.items()}
    _write(args.out, json.dumps(serial, ensure_ascii=False, indent=2))
    return 0

def _cmd_aggregate(args) -> int:
    now = args.now or _utc_now()
    demand_raw = json.loads(open(args.demand, encoding="utf-8").read())
    responses = [DemandResponse(**d) for d in demand_raw]
    supply_raw = json.loads(open(args.supply, encoding="utf-8").read())
    reports = {esp: [VisibilityReport.model_validate(r) for r in rs]
               for esp, rs in supply_raw.items()}
    demand_agg = aggregate_demand(responses)
    supply_agg = aggregate_supply(reports)
    data = build_aggregates(demand_agg, supply_agg, now=now,
                            pipeline_version=args.pipeline_version)
    validate_aggregates(data)
    _write(args.out, json.dumps(data, ensure_ascii=False, indent=2))
    return 0

def run(argv: list[str],
        engines_factory: Callable[[Settings], dict] = build_engines,
        collector_factory: Callable[[Settings], list] = build_collectors) -> int:
    parser = argparse.ArgumentParser(prog="medrank-study")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_plan = sub.add_parser("plan", help="estima chamadas e custo de API")
    p_plan.add_argument("--config", required=True)
    p_plan.add_argument("--roster-size", type=int, default=0,
                        help="médicos por roster (para estimar a oferta)")
    p_plan.add_argument("--media-procedimentos", type=int, default=4)

    p_dem = sub.add_parser("demand", help="roda os prompts de demanda")
    p_dem.add_argument("--config", required=True)
    p_dem.add_argument("--out")
    p_dem.add_argument("--now", default=None)

    p_sup = sub.add_parser("supply", help="roda o Visibility Score nos rosters")
    p_sup.add_argument("--config", required=True)
    p_sup.add_argument("--out")
    p_sup.add_argument("--now", default=None)
    p_sup.add_argument("--pipeline-version", default="0.1.0")

    p_agg = sub.add_parser("aggregate", help="agrega + valida o aggregates.json")
    p_agg.add_argument("--demand", required=True)
    p_agg.add_argument("--supply", required=True)
    p_agg.add_argument("--out")
    p_agg.add_argument("--now", default=None)
    p_agg.add_argument("--pipeline-version", default="0.1.0")

    args = parser.parse_args(argv)
    if args.cmd == "plan":
        return _cmd_plan(args)
    if args.cmd == "demand":
        return _cmd_demand(args, engines_factory)
    if args.cmd == "supply":
        return _cmd_supply(args, collector_factory)
    if args.cmd == "aggregate":
        return _cmd_aggregate(args)
    return 2

def main() -> None:
    raise SystemExit(run(sys.argv[1:]))


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Rodar e confirmar passagem**

Run: `.venv/bin/pytest tests/test_study_cli.py -q`
Expected: PASS (3 passed)

- [ ] **Step 5: Rodar a suíte inteira (não quebrar nada existente)**

Run: `.venv/bin/pytest -q`
Expected: PASS — todos os testes (existentes + novos `test_study_*`)

- [ ] **Step 6: Commit**

```bash
git add visibility/study/cli.py tests/test_study_cli.py
git commit -m "feat(study): CLI medrank-study (plan/demand/supply/aggregate)"
```

---

## Task 12: Smoke end-to-end + README do estudo

**Files:**
- Create: `tests/test_study_smoke.py`
- Create: `visibility/study/README.md`

- [ ] **Step 1: Escrever o smoke test que falha**

```python
# tests/test_study_smoke.py
import json
from visibility.study.cli import run

def test_pipeline_demand_para_aggregate(tmp_path):
    cfg = {"demand": {"especialidades": ["Dermatologia"], "cidades": ["SP"],
                      "procedimentos": {"Dermatologia": ["botox"]},
                      "prompt_tipos": ["melhor_especialista"],
                      "engines": ["chatgpt"], "repeticoes": 1},
           "rosters": []}
    cfgp = tmp_path / "study.json"; cfgp.write_text(json.dumps(cfg), encoding="utf-8")

    def fake_engines(settings):
        class L:
            name = "chatgpt"
            def ask(self, p): return "Indico a Dra. Ana Lima; veja no Doctoralia."
        return {"chatgpt": L()}

    dem = tmp_path / "demand.json"
    assert run(["demand", "--config", str(cfgp), "--out", str(dem),
                "--now", "2026-06-28T14:00:00Z"], engines_factory=fake_engines) == 0

    sup = tmp_path / "supply.json"; sup.write_text("{}", encoding="utf-8")
    agg = tmp_path / "aggregates.json"
    assert run(["aggregate", "--demand", str(dem), "--supply", str(sup),
                "--out", str(agg), "--now", "2026-06-28T14:00:00Z"]) == 0

    data = json.loads(agg.read_text(encoding="utf-8"))
    assert data["demanda"]["pct_com_medico_nominal"] == 1.0
    assert ["doctoralia", 1] in data["demanda"]["top_marketplaces"]
```

- [ ] **Step 2: Rodar e confirmar falha (ou passar, se tudo já integra)**

Run: `.venv/bin/pytest tests/test_study_smoke.py -q`
Expected: PASS (1 passed) — se falhar, corrigir a integração antes de seguir.

- [ ] **Step 3: Escrever o README do estudo**

```markdown
<!-- visibility/study/README.md -->
# medrank-study — engine de dados do Índice MedRank 2026

Gera o `aggregates.json` (lado da demanda + lado da oferta) que alimenta o microsite e o PDF.
Reaproveita a CLI `medrank-visibility`. **Sem rede nos testes** (clientes scriptados).

## Fluxo

```bash
# 1. estimar custo antes de gastar API
medrank-study plan --config study.json --roster-size 50

# 2. lado da demanda (prompts de paciente nos motores de IA)
SERPAPI_KEY=... OPENAI_API_KEY=... medrank-study demand --config study.json \
  --out raw_demand.json

# 3. lado da oferta (Visibility Score sobre rosters reais)
medrank-study supply --config study.json --out raw_supply.json

# 4. agregar + validar contra o schema -> aggregates.json (sem PII)
medrank-study aggregate --demand raw_demand.json --supply raw_supply.json \
  --out aggregates.json
```

## `study.json`

```json
{
  "demand": {
    "especialidades": ["Dermatologia", "Cirurgia Plástica"],
    "cidades": ["São Paulo", "Rio de Janeiro"],
    "procedimentos": {"Dermatologia": ["botox", "preenchimento"],
                      "Cirurgia Plástica": ["rinoplastia"]},
    "prompt_tipos": ["melhor_especialista", "procedimento", "confianca"],
    "engines": ["chatgpt", "gemini", "perplexity"],
    "repeticoes": 3
  },
  "rosters": [
    {"especialidade": "Dermatologia", "arquivo": "rosters/derm.json"}
  ]
}
```

`rosters/derm.json` é uma lista de `DoctorMeta` (ver `visibility/models.py`).

## Limitações / metodologia
- Os motores de IA são acessados via **API** (gpt-4o, sonar, gemini) — proxy do que o
  consumidor vê, não réplica exata. Declarar isso na metodologia do relatório.
- Risco-CFM é **heurístico** (lista de frases); confirmação por LLM é etapa futura.
- O `aggregates.json` é **anonimizado**: só estatísticas agregadas e share-of-voice.
```

- [ ] **Step 4: Rodar a suíte inteira**

Run: `.venv/bin/pytest -q`
Expected: PASS — tudo verde.

- [ ] **Step 5: Commit**

```bash
git add tests/test_study_smoke.py visibility/study/README.md
git commit -m "test(study): smoke end-to-end + README da engine de dados"
```

---

## Self-Review (do autor do plano)

**1. Cobertura do spec (Frente 1 do §3):**
- §3a Runner de demanda → Tasks 2–3. ✅
- §3b Classificador (tipo de entidade + share of voice + risco-CFM) → Tasks 4–5; share of voice agregado na Task 6. ✅
- §3c Batch do Visibility Score sobre roster → Task 7; agregação Task 8. ✅
- §3d Export de agregados (schema versionado, sem PII) → Task 10. ✅
- Modelo de custo (§7) → Task 9. ✅
- Orquestração / CLI nova `medrank-study` → Task 11; smoke + README Task 12. ✅
- *Sourcing do roster* permanece input externo (item aberto do spec, intencional). ✅

**2. Placeholders:** nenhum TODO/TBD; todo step de código traz o código completo e executável.

**3. Consistência de tipos/assinaturas:**
- `DemandResponse(especialidade, cidade, tipo, procedimento, engine, rep, capturado_em, texto)` — mesma ordem em `demand.py`, nos testes de aggregate e no `DemandResponse(**d)` da CLI. ✅
- `classify_response(texto) -> ResponseClassification(tipo_resposta, medicos, marketplaces, tem_clinica, tem_hospital, cfm_risco)` — consistente entre Tasks 4/5/6. ✅
- `run_supply(rosters, collector_factory, settings, *, now, pipeline_version)` — mesma assinatura no teste (Task 7) e na chamada da CLI (Task 11). ✅
- `build_aggregates(demand, supply, *, now, pipeline_version)` e chaves `demanda`/`oferta` — schema (Task 10) e CLI/smoke (Tasks 11–12) batem. ✅
- `estimate_cost(llm, serpapi, places)` — consistente Task 9 e CLI. ✅

Sem ajustes pendentes.

---

## Notas de execução

- **Pré-requisito:** venv com `pip install -e ".[dev]"` (já documentado em `visibility/README.md`).
- **Ordem:** Tasks 0→12 em sequência; cada uma deixa a suíte verde.
- **Rede:** nenhum teste toca a internet — sempre injete fakes (`engines_factory`/`collector_factory`).
- **Próximas frentes** (planos próprios): Frente 2 (microsite consumindo `aggregates.json`), Frente 3 (PDF + captura → Google Sheet), Frente 4 (distribuição).
