# AI Visibility Score — Índice por médico (design)

**Data:** 2026-06-28
**Status:** aprovado (design) → próximo passo: plano de implementação
**Produto:** MedRankGPT · camada de diagnóstico (lead magnet "Diagnóstico de Visibilidade em IA")

---

## 1. Contexto e propósito

Estrutura de dados (índice) que descreve, **por médico**, o quão visível ele é quando
um paciente busca/pergunta — no Google, em plataformas médicas e em mecanismos de
resposta por IA. É a matéria-prima do **diagnóstico gratuito** descrito no GTM
([`inteligencia-competitiva-e-gtm.md`](../../../inteligencia-competitiva-e-gtm.md),
§8.2): mostrar o gap ao vivo na reunião e converter.

Decisões que moldaram o design (respostas do brainstorming):

| Decisão | Escolha |
|---|---|
| Uso primário | **Diagnóstico / lead magnet** (um JSON por médico-prospect) |
| Modelo de score | **0–100 + 4 categorias** com sub-scores |
| Coleta | **Pipeline automatizado** → schema máquina-friável: evidência bruta, confiança, fonte, timestamp, versionamento |
| Formato | **Aninhado por categoria** (abordagem A) — o JSON espelha o scorecard |

**Não-objetivos do v1:** estudo agregado ("Índice MedRankGPT" para PR) e dashboard
recorrente de cliente. O schema é desenhado para **evoluir** para esses usos sem
reestruturação (campos `weight`/`pontos`/`run` já presentes), mas eles ficam fora do
escopo desta spec.

---

## 2. Estrutura de topo

Cinco blocos. Três descrevem *o que foi encontrado* (`meta`, `score`, `categorias`);
dois são *evidências cross-cutting* que o relatório renderiza para impacto
(`concorrentes`, `prompts_ia`).

```jsonc
{
  "schema_version": "1.0",
  "meta":          { /* quem é o médico + dados da execução do pipeline */ },
  "score":         { /* manchete 0–100 + tier + 4 sub-scores */ },
  "categorias":    { /* as 4 categorias, cada uma com seus sinais */ },
  "concorrentes":  { /* sinal #12: quem aparece no lugar dele */ },
  "prompts_ia":    [ /* log bruto de prompts rodados — alimenta a North Star */ ]
}
```

**Camadas / fonte da verdade:** `prompts_ia` é o **log de eventos bruto** (cada prompt
rodado em cada engine). Os sinais `ia_marca` / `ia_procedimento` e o bloco
`concorrentes` são **agregações derivadas** desse log. Isso mantém a execução
auditável enquanto o relatório mostra resumos limpos.

---

## 3. Unidade reutilizável: o **sinal**

Cada um dos 11 sinais pontuados tem exatamente esta forma. É o coração do índice.

```jsonc
{
  "id": "google_marca",                 // estável, snake_case — chave do sinal
  "label": "Aparece no Google ao buscar o nome",
  "status": "fail",                     // pass | partial | fail | unknown
  "valor": false,                       // valor normalizado (bool | número | string)
  "weight": 12.5,                       // pontos que este sinal vale dentro da categoria
  "pontos": 0,                          // pontos obtidos (0..weight)
  "confianca": 0.95,                    // 0–1, confiança do pipeline na checagem
  "metodo": "serp_scrape",              // como foi checado (ver tabela §4)
  "observacao": "Não aparece nos 10 primeiros; Doctoralia de outra médica na posição 1.",
  "evidencia": [                        // 1..N provas; vazio só se status=unknown
    {
      "fonte": "google_search",
      "url": "https://www.google.com/search?q=...",
      "query": "Dra. Fulana de Tal dermatologista",
      "capturado_em": "2026-06-28T14:00:00Z",
      "resumo": "0 resultados próprios no top 10.",
      "raw": "…"                        // bruto opcional (pode ser grande/omitido no relatório)
    }
  ]
}
```

### Campos do sinal

| Campo | Tipo | Obrigatório | Notas |
|---|---|---|---|
| `id` | string | sim | snake_case estável; usado como chave/lookup |
| `label` | string | sim | texto humano para o relatório |
| `status` | enum | sim | `pass` · `partial` · `fail` · `unknown` |
| `valor` | bool/number/string | sim | valor normalizado específico do sinal |
| `weight` | number | sim | pontos máximos dentro da categoria |
| `pontos` | number | sim | derivado de `status` (ver §5) |
| `confianca` | number 0–1 | sim | confiança do pipeline |
| `metodo` | string | sim | identificador da técnica de checagem |
| `observacao` | string | não | nota curta para a reunião |
| `evidencia` | array | sim (≥1, exceto `unknown`) | provas com fonte, url, timestamp, bruto |

### Campo da evidência

| Campo | Tipo | Obrigatório |
|---|---|---|
| `fonte` | string | sim |
| `url` | string | não |
| `query` | string | não |
| `capturado_em` | ISO 8601 | sim |
| `resumo` | string | sim |
| `raw` | string/object | não |

---

## 4. Os 12 sinais → 4 categorias

Cada categoria vale **25 pontos** (v1). O sinal #12 (concorrentes) **não é pontuado** —
é evidência cross-cutting que torna cada "não" mais doloroso.

| Categoria | `id` da categoria | Sinais (`id`) | `weight` por sinal | `metodo` sugerido |
|---|---|---|---|---|
| Busca tradicional | `busca_tradicional` | `google_marca`, `google_maps` | 12.5 | `serp_scrape`, `gmaps_api` |
| Plataformas médicas | `plataformas_medicas` | `doctoralia`, `boaconsulta` | 12.5 | `profile_scrape` |
| Visibilidade em IA | `visibilidade_ia` | `ia_marca`, `ia_procedimento` | 12.5 | `llm_prompt` |
| Site / E-E-A-T técnico | `site_conteudo` | `crm_rqe_visivel`, `schema_medico`, `pagina_especialidade`, `pagina_procedimento`, `conteudo_perguntas` | 5.0 | `site_scrape`, `schema_parse` |

**Mapa para a lista original do briefing:**

1. aparece no Google pela marca → `google_marca`
2. aparece no Google Maps → `google_maps`
3. aparece na Doctoralia → `doctoralia`
4. aparece no BoaConsulta → `boaconsulta`
5. aparece em respostas de IA → `ia_marca`
6. aparece em perguntas de procedimento → `ia_procedimento`
7. tem CRM/RQE visível → `crm_rqe_visivel`
8. tem schema médico → `schema_medico`
9. tem página por especialidade → `pagina_especialidade`
10. tem página por procedimento → `pagina_procedimento`
11. tem conteúdo que responde perguntas reais → `conteudo_perguntas`
12. quais concorrentes aparecem no lugar dele → bloco `concorrentes`

**Extensibilidade:** `plataformas_medicas` pode receber novos sinais (ex.: `imedicina`,
`google_business`) sem mudar a estrutura — re-divide-se o `weight` da categoria.

**Narrativa codificada:** categorias 1–3 são *resultados* (muito offsite — score baixo =
"você está invisível"); a categoria 4 é a *alavanca controlável que se vende* (o onsite
que a consultoria corrige). O scorecard torna o gap óbvio e o conserto óbvio.

### Forma da categoria em `categorias`

```jsonc
"site_conteudo": {
  "label": "Site / E-E-A-T técnico",
  "score": 12.5, "max": 25, "weight": 25,
  "sinais": [ /* os objetos-sinal */ ]
}
```

---

## 5. Lógica de pontuação

1. `status` → `pontos`: **pass** = `weight` cheio · **partial** = `weight / 2` ·
   **fail** = 0 · **unknown** = 0.
2. `categoria.score` = soma exata dos `pontos` dos seus sinais (pode ser fracionário; o
   arredondamento é decisão de exibição/UI, não do dado).
3. `score.total` = soma dos `score` das 4 categorias (0–100).
4. `score.tier` (faixas v1, ajustáveis):
   - `0–39` → **Bronze**
   - `40–69` → **Prata**
   - `70–100` → **Ouro**

`tier` conecta-se à estética "medalha" de [`DESIGN.md`](../../../DESIGN.md). Todos os pesos
vivem nos dados → trocar para "ponderado por impacto" é mudar `weight`, não a estrutura.

---

## 6. Bloco `concorrentes` (sinal #12)

```jsonc
"concorrentes": {
  "resumo": "Em 8 de 10 prompts, a IA cita outros 3 médicos — não a Dra. Fulana.",
  "ofensores_recorrentes": [
    { "nome": "Dr. X", "aparicoes": 6, "especialidade": "Dermatologia",
      "fonte_citada": "doctoralia.com.br/..." }
  ]
}
```

---

## 7. Bloco `prompts_ia` (alimenta a North Star)

Log bruto: cada prompt × engine × região. North Star = nº de prompts/cidades onde o
médico é citado (GTM §8.6).

```jsonc
"prompts_ia": [
  {
    "id": "p1",
    "prompt": "melhor dermatologista para acne em São Paulo",
    "tipo": "procedimento",            // marca | especialidade | procedimento
    "engine": "chatgpt",               // chatgpt | gemini | perplexity | google_ai
    "regiao": "São Paulo, SP",
    "medico_citado": false,
    "posicao": null,
    "concorrentes_citados": ["Dr. X", "Dra. Y"],
    "capturado_em": "2026-06-28T14:00:00Z",
    "raw_resposta": "…"
  }
]
```

---

## 8. Exemplo preenchido (resumido)

```json
{
  "schema_version": "1.0",
  "meta": {
    "doctor": {
      "nome": "Dra. Fulana de Tal",
      "crm": "SP 123456", "rqe": "12345",
      "especialidade_principal": "Dermatologia",
      "especialidades": ["Dermatologia"],
      "procedimentos_foco": ["botox", "preenchimento", "acne"],
      "cidade": "São Paulo", "uf": "SP",
      "site": "https://drafulana.com.br", "perfil_google": "https://g.page/drafulana"
    },
    "run": {
      "gerado_em": "2026-06-28T14:00:00Z",
      "pipeline_version": "0.3.1",
      "idioma": "pt-BR", "regiao_busca": "São Paulo, SP"
    }
  },
  "score": {
    "total": 25, "max": 100, "tier": "Bronze",
    "categorias": {
      "busca_tradicional":   { "score": 6.25, "max": 25 },
      "plataformas_medicas": { "score": 6.25, "max": 25 },
      "visibilidade_ia":     { "score": 0,    "max": 25 },
      "site_conteudo":       { "score": 12.5, "max": 25 }
    }
  },
  "categorias": {
    "busca_tradicional": {
      "label": "Busca tradicional", "score": 6.25, "max": 25, "weight": 25,
      "sinais": [
        {
          "id": "google_marca", "label": "Aparece no Google ao buscar o nome",
          "status": "partial", "valor": true, "weight": 12.5, "pontos": 6.25,
          "confianca": 0.9, "metodo": "serp_scrape",
          "observacao": "Aparece só via Doctoralia de terceiros, não com domínio próprio.",
          "evidencia": [{
            "fonte": "google_search",
            "url": "https://www.google.com/search?q=Dra.+Fulana+de+Tal+dermatologista",
            "query": "Dra. Fulana de Tal dermatologista",
            "capturado_em": "2026-06-28T14:00:00Z",
            "resumo": "Perfil próprio ausente do top 10; só listagens de terceiros."
          }]
        },
        {
          "id": "google_maps", "label": "Aparece no Google Maps / Perfil de Empresa",
          "status": "fail", "valor": false, "weight": 12.5, "pontos": 0,
          "confianca": 0.95, "metodo": "gmaps_api",
          "observacao": "Sem perfil de empresa verificado.",
          "evidencia": [{
            "fonte": "google_maps", "capturado_em": "2026-06-28T14:00:00Z",
            "resumo": "Nenhum resultado de ficha para o nome na região."
          }]
        }
      ]
    },
    "site_conteudo": {
      "label": "Site / E-E-A-T técnico", "score": 12.5, "max": 25, "weight": 25,
      "sinais": [
        { "id": "crm_rqe_visivel", "label": "CRM/RQE visível no site", "status": "pass",
          "valor": true, "weight": 5, "pontos": 5, "confianca": 0.98, "metodo": "site_scrape",
          "evidencia": [{ "fonte": "site", "url": "https://drafulana.com.br/sobre",
            "capturado_em": "2026-06-28T14:00:00Z", "resumo": "CRM e RQE no rodapé." }] },
        { "id": "schema_medico", "label": "Tem schema médico (Physician/MedicalClinic)",
          "status": "fail", "valor": false, "weight": 5, "pontos": 0, "confianca": 0.97,
          "metodo": "schema_parse",
          "evidencia": [{ "fonte": "site", "url": "https://drafulana.com.br",
            "capturado_em": "2026-06-28T14:00:00Z", "resumo": "Nenhum JSON-LD Physician encontrado." }] },
        { "id": "pagina_especialidade", "label": "Tem página por especialidade", "status": "pass",
          "valor": true, "weight": 5, "pontos": 5, "confianca": 0.9, "metodo": "site_scrape",
          "evidencia": [{ "fonte": "site", "url": "https://drafulana.com.br/dermatologia",
            "capturado_em": "2026-06-28T14:00:00Z", "resumo": "Página dedicada a dermatologia." }] },
        { "id": "pagina_procedimento", "label": "Tem página por procedimento", "status": "partial",
          "valor": true, "weight": 5, "pontos": 2.5, "confianca": 0.85, "metodo": "site_scrape",
          "evidencia": [{ "fonte": "site", "url": "https://drafulana.com.br/botox",
            "capturado_em": "2026-06-28T14:00:00Z", "resumo": "Só 1 de 3 procedimentos-foco tem página." }] },
        { "id": "conteudo_perguntas", "label": "Conteúdo que responde perguntas reais (FAQ/citável)",
          "status": "fail", "valor": false, "weight": 5, "pontos": 0, "confianca": 0.8,
          "metodo": "site_scrape",
          "evidencia": [{ "fonte": "site", "capturado_em": "2026-06-28T14:00:00Z",
            "resumo": "Sem FAQ nem conteúdo em formato de pergunta-resposta." }] }
      ]
    }
  },
  "concorrentes": {
    "resumo": "Em 8 de 10 prompts, a IA cita outros 3 médicos — não a Dra. Fulana.",
    "ofensores_recorrentes": [
      { "nome": "Dr. X", "aparicoes": 6, "especialidade": "Dermatologia",
        "fonte_citada": "doctoralia.com.br/dr-x" }
    ]
  },
  "prompts_ia": [
    { "id": "p1", "prompt": "melhor dermatologista para acne em São Paulo",
      "tipo": "procedimento", "engine": "chatgpt", "regiao": "São Paulo, SP",
      "medico_citado": false, "posicao": null,
      "concorrentes_citados": ["Dr. X", "Dra. Y"],
      "capturado_em": "2026-06-28T14:00:00Z", "raw_resposta": "…" }
  ]
}
```

> Exemplo abreviado: `plataformas_medicas` e `visibilidade_ia` seguem a mesma forma de
> categoria/sinal de `busca_tradicional`.

---

## 9. JSON Schema (draft 2020-12, esqueleto)

```jsonc
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://medrankgpt.com.br/schemas/ai-visibility-score/1.0.json",
  "type": "object",
  "required": ["schema_version", "meta", "score", "categorias", "concorrentes", "prompts_ia"],
  "properties": {
    "schema_version": { "type": "string" },
    "meta": {
      "type": "object", "required": ["doctor", "run"],
      "properties": {
        "doctor": {
          "type": "object",
          "required": ["nome", "especialidade_principal", "cidade", "uf"],
          "properties": {
            "nome": { "type": "string" },
            "crm": { "type": "string" }, "rqe": { "type": "string" },
            "especialidade_principal": { "type": "string" },
            "especialidades": { "type": "array", "items": { "type": "string" } },
            "procedimentos_foco": { "type": "array", "items": { "type": "string" } },
            "cidade": { "type": "string" }, "uf": { "type": "string" },
            "site": { "type": "string" }, "perfil_google": { "type": "string" }
          }
        },
        "run": {
          "type": "object", "required": ["gerado_em", "pipeline_version"],
          "properties": {
            "gerado_em": { "type": "string", "format": "date-time" },
            "pipeline_version": { "type": "string" },
            "idioma": { "type": "string" }, "regiao_busca": { "type": "string" }
          }
        }
      }
    },
    "score": {
      "type": "object", "required": ["total", "max", "tier", "categorias"],
      "properties": {
        "total": { "type": "number", "minimum": 0, "maximum": 100 },
        "max": { "type": "number" },
        "tier": { "type": "string", "enum": ["Bronze", "Prata", "Ouro"] },
        "categorias": {
          "type": "object",
          "additionalProperties": {
            "type": "object", "required": ["score", "max"],
            "properties": { "score": { "type": "number" }, "max": { "type": "number" } }
          }
        }
      }
    },
    "categorias": {
      "type": "object",
      "additionalProperties": { "$ref": "#/$defs/categoria" }
    },
    "concorrentes": {
      "type": "object", "required": ["resumo", "ofensores_recorrentes"],
      "properties": {
        "resumo": { "type": "string" },
        "ofensores_recorrentes": {
          "type": "array",
          "items": {
            "type": "object", "required": ["nome", "aparicoes"],
            "properties": {
              "nome": { "type": "string" },
              "aparicoes": { "type": "integer" },
              "especialidade": { "type": "string" },
              "fonte_citada": { "type": "string" }
            }
          }
        }
      }
    },
    "prompts_ia": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "prompt", "tipo", "engine", "medico_citado"],
        "properties": {
          "id": { "type": "string" },
          "prompt": { "type": "string" },
          "tipo": { "type": "string", "enum": ["marca", "especialidade", "procedimento"] },
          "engine": { "type": "string", "enum": ["chatgpt", "gemini", "perplexity", "google_ai"] },
          "regiao": { "type": "string" },
          "medico_citado": { "type": "boolean" },
          "posicao": { "type": ["integer", "null"] },
          "concorrentes_citados": { "type": "array", "items": { "type": "string" } },
          "capturado_em": { "type": "string", "format": "date-time" },
          "raw_resposta": { "type": "string" }
        }
      }
    }
  },
  "$defs": {
    "categoria": {
      "type": "object", "required": ["label", "score", "max", "weight", "sinais"],
      "properties": {
        "label": { "type": "string" },
        "score": { "type": "number" }, "max": { "type": "number" },
        "weight": { "type": "number" },
        "sinais": { "type": "array", "items": { "$ref": "#/$defs/sinal" } }
      }
    },
    "sinal": {
      "type": "object",
      "required": ["id", "label", "status", "valor", "weight", "pontos", "confianca", "metodo", "evidencia"],
      "properties": {
        "id": { "type": "string" },
        "label": { "type": "string" },
        "status": { "type": "string", "enum": ["pass", "partial", "fail", "unknown"] },
        "valor": { "type": ["boolean", "number", "string"] },
        "weight": { "type": "number" },
        "pontos": { "type": "number" },
        "confianca": { "type": "number", "minimum": 0, "maximum": 1 },
        "metodo": { "type": "string" },
        "observacao": { "type": "string" },
        "evidencia": { "type": "array", "items": { "$ref": "#/$defs/evidencia" } }
      }
    },
    "evidencia": {
      "type": "object", "required": ["fonte", "capturado_em", "resumo"],
      "properties": {
        "fonte": { "type": "string" },
        "url": { "type": "string" }, "query": { "type": "string" },
        "capturado_em": { "type": "string", "format": "date-time" },
        "resumo": { "type": "string" },
        "raw": { "type": ["string", "object"] }
      }
    }
  }
}
```

---

## 10. Decisões em aberto / futuro

- **Pesos por impacto:** v1 usa 25/categoria e split igual por sinal. Retunar é só mudar
  `weight` — sem reestruturar.
- **Faixas de tier:** 0–39 / 40–69 / 70–100 são placeholder.
- **Evolução para estudo agregado e dashboard:** o `run.gerado_em` + schema versionado
  permitem empilhar execuções no tempo (dashboard) e agregar por especialidade/cidade
  (Índice MedRankGPT) sem mudar o schema base. Fora do escopo do v1.
- **Tamanho de `raw`:** definir na implementação se o bruto fica inline ou referenciado
  (ex.: ponteiro para blob), para o JSON do relatório não inchar.
