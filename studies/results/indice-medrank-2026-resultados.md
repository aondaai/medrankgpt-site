# Índice MedRank 2026 — Resultados (snapshot)

> **O Estado das Buscas Médicas na Era da IA.** Dados proprietários coletados pela engine
> `visibility/study/`. Amostra: **20 especialidades × 9 capitais** (SP, RJ, BH, Curitiba,
> Porto Alegre, Brasília, Recife, Salvador, Fortaleza — 4 regiões).
> Coleta: 2026-06-28. Números agregados/anonimizados em [`aggregates.json`](aggregates.json).

## As manchetes

1. **No Google, o paciente cai no marketplace.** Em **89%** das buscas "melhor [especialista]",
   quem ocupa a **posição #1** da 1ª página é o **Doctoralia** — não o médico.
2. **No ChatGPT, a IA nomeia um médico — em 93% das vezes.** Mas escolhe lendo as mesmas
   fontes que dominam o Google: **cita o Doctoralia como fonte em 35%** das respostas.
3. **A vaga está aberta.** Nenhum médico domina as recomendações da IA (o mais citado
   aparece em só 9 de 720 respostas). Quem se posiciona vira "o nome que a IA dá".

---

## Pilar A — ChatGPT (a IA que o paciente *pergunta*)

Modelo: `gpt-4o-search-preview` (navega na web, como o ChatGPT de consumo). 720 buscas.

| Métrica | Valor |
|---|---|
| **Cita um médico nominalmente** | **93%** |
| — "melhor [especialista]" | 98% |
| — "[especialista] de confiança" | 100% |
| — "quem faz [procedimento]" | 87% |
| **Cita Doctoralia como fonte** | **35%** |
| Alegação com risco-CFM | 0% |
| Concentração (top médico) | 9 / 720 — **pulverizado** |

> Nota metodológica decisiva: o modelo **sem busca** (`gpt-4o`) se esquiva e cita médico em
> só ~6%; o modelo **com busca** cita em 93%. O ChatGPT de consumo navega — então o número
> fiel é o do `search-preview`.

## Pilar B — Google SERP (o que de fato *ranqueia*)

Composição da 1ª página orgânica via Serper. 540 buscas.

| Tipo de busca | #1 = marketplace | Quem lidera o #1 |
|---|---|---|
| **"melhor [especialista]"** (180) | **89%** | **Doctoralia (160/180)** |
| **"[procedimento]"** (360) | **16%** | sites próprios (36%), **Instagram (22%)**, clínica/hospital |

**Domínios mais frequentes na posição #1 (540 buscas):** Doctoralia (216) · Instagram (81) ·
Rede D'Or (9) · Santa Casa (8) · Hospital Moinhos (7).

**Insight acionável:** no genérico ("melhor X") o Doctoralia engole; no específico
("procedimento Y") o **próprio médico compete e vence** (Instagram + site pessoal). É aí
que o posicionamento individual paga.

## Pilar C — Google AI Overview (a IA do Google)

Via SerpApi. Amostra: **460/540 (85%)** — taxa de supressão estável desde os 280 primeiros.

| Tipo de busca | Sem AIO (suprimido) | Quando aparece, cita médico |
|---|---|---|
| **Geral** | **37%** | 56% |
| **"melhor [especialista]"** | **43%** | **92%** |
| **"[procedimento]"** | 34% | 40% |

**Achados:**
- O Google **não mostra IA em 37% das buscas médicas** — e em **43%** quando o paciente
  procura "o melhor [especialista]". Confirma a postura conservadora do Google em saúde (YMYL).
- Mas quando **mostra** AIO no "melhor", ele **nomeia um médico em 92%** das vezes — ou seja,
  onde há IA do Google, ela também aponta nomes (e lê as mesmas fontes).

---

## A tese do Índice (com 2 superfícies fechadas)

> **O Google te manda pro Doctoralia. O ChatGPT lê o Doctoralia e nomeia um médico — mas
> qualquer um, porque o jogo está aberto. Garanta que o nome seja o seu.**

Isso é, literalmente, o argumento do AEO/posicionamento que o MedRankGPT vende — agora
provado com dado proprietário nacional.

## Metodologia e ressalvas

- **Superfícies:** ChatGPT (`gpt-4o-search-preview`, navegando), Google SERP (Serper),
  Google AIO (SerpApi). 3 das fontes que o paciente brasileiro realmente encontra.
- **Proxy de API:** os motores são acessados via API — aproximam, não replicam byte-a-byte,
  o produto de consumo. Declarado.
- **Momento:** SERP e AIO refletem o estado da busca no dia da coleta.
- **Risco-CFM:** heurístico (lista de frases); confirmação por LLM é etapa futura.
- **Anonimização:** só agregados e share-of-voice; sem blocos por-médico identificáveis.
- **Classificador de SERP:** o bucket "outro" é residual (sites próprios + agregadores ainda
  não rotulados, ex.: Rede D'Or) — refinável; o sinal "marketplace = #1" é inequívoco.

## Próximos passos

1. ✅ Pilar C (AIO) fechado (37% supressão). _Opcional: completar os ~80 do tail lento._
2. **2ª repetição** dos prompts de IA (medir instabilidade da recomendação).
3. **Camada 2 — AI Visibility Score** sobre rosters reais (distribuição de notas; depende de
   sourcing de médicos).
4. Microsite + PDF consumindo o `aggregates.json`.
