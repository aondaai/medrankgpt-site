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
