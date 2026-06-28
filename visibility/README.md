# medrank-visibility

CLI que gera o **AI Visibility Score** de um médico: dado o nome/especialidade/cidade,
roda checagens de visibilidade (Google, Google Maps, Doctoralia/BoaConsulta, motores de
IA e o próprio site) e emite um relatório JSON pontuado de 0–100 em 4 categorias,
validado contra um JSON Schema canônico.

> É uma **ferramenta de linha de comando** (não um serviço web). Não há URL nem login —
> o acesso é quem tem shell na máquina onde está instalada + quem detém as chaves de API.

## Requisitos

- Python **3.11+**
- Instalação editável a partir da raiz do repo:

```bash
python3.11 -m venv .venv
.venv/bin/pip install -e ".[dev]"
```

## Uso

```bash
# escreve o relatório num arquivo
.venv/bin/medrank-visibility --doctor doctor.json --out report.json

# ou imprime no stdout
.venv/bin/medrank-visibility --doctor doctor.json

# equivalente via módulo
.venv/bin/python -m visibility.cli --doctor doctor.json --out report.json
```

Flags:

| Flag | Default | Descrição |
|------|---------|-----------|
| `--doctor` | (obrigatório) | caminho do JSON de entrada do médico |
| `--out` | stdout | caminho do relatório de saída |
| `--now` | UTC agora | timestamp ISO (para execuções determinísticas/testes) |
| `--pipeline-version` | `0.1.0` | carimbado em `meta.run.pipeline_version` |

### Entrada (`doctor.json`)

Campos de `DoctorMeta` (ver [`models.py`](models.py)). Mínimo: `nome`,
`especialidade_principal`, `cidade`, `uf`.

```json
{
  "nome": "Dra. Fulana de Tal",
  "crm": "SP 123456", "rqe": "12345",
  "especialidade_principal": "Dermatologia",
  "especialidades": ["Dermatologia"],
  "procedimentos_foco": ["botox", "acne"],
  "cidade": "São Paulo", "uf": "SP",
  "site": "https://drafulana.com.br"
}
```

### Saída

JSON validado contra [`schema/ai_visibility_score_1_0.json`](schema/ai_visibility_score_1_0.json):
`meta`, `score` (total 0–100 + tier Bronze/Prata/Ouro + sub-scores), `categorias`
(os 12 sinais), `concorrentes` (quem aparece no lugar dele) e `prompts_ia` (log bruto).
Spec completa: [`docs/superpowers/specs/2026-06-28-ai-visibility-score-index-design.md`](../docs/superpowers/specs/2026-06-28-ai-visibility-score-index-design.md).

## Chaves de API (segredos)

Lidas do ambiente por [`config.py`](config.py). Guarde num `.env`/secret store da máquina —
**nunca no git**. Sem chaves, a CLI roda mas cada sinal externo vira `unknown` (score baixo).

| Variável | Usada por |
|----------|-----------|
| `SERPAPI_KEY` | Google search (`google_marca`) |
| `GOOGLE_PLACES_KEY` | Google Maps (`google_maps`) |
| `OPENAI_API_KEY` | motor de IA `chatgpt` |
| `PERPLEXITY_API_KEY` | motor de IA `perplexity` |
| `GEMINI_API_KEY` | motores `gemini` e `google_ai` |

Os collectors de site e plataformas médicas não exigem chave (fazem scrape via HTTP).

## Categorias e pontuação

| Categoria (25 pts) | Sinais |
|--------------------|--------|
| Busca tradicional | `google_marca`, `google_maps` |
| Plataformas médicas | `doctoralia`, `boaconsulta` |
| Visibilidade em IA | `ia_marca`, `ia_procedimento` |
| Site / E-E-A-T técnico | `crm_rqe_visivel`, `schema_medico`, `pagina_especialidade`, `pagina_procedimento`, `conteudo_perguntas` |

`pass` = peso cheio · `partial` = metade · `fail`/`unknown` = 0. Total = soma das 4
categorias. Tier: 0–39 Bronze · 40–69 Prata · 70–100 Ouro.

## Testes

```bash
.venv/bin/pytest -q
```

Todos os collectors são testados contra fixtures (sem rede); o build fica verde sem chaves.

## Limitações conhecidas (v1)

- **Score com dados ausentes:** sem uma chave, a categoria correspondente cai para
  `unknown` (0 pts) mas o total continua sobre 100 — decisão de produto em aberto.
- **Exposição em rede:** se um dia virar serviço web, o fetch de `doctor.site`
  precisa de proteção SSRF (allowlist http/https, bloquear IPs privados) antes de
  aceitar URL de entrada não confiável. Na CLI (entrada confiável) não se aplica.
- `google_ai` é aproximado pelo cliente Gemini (não há API pública do AI Overviews).
