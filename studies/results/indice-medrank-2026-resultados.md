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
4. **84% dos médicos são invisíveis pra IA.** De **2.567** médicos reais listados no Doctoralia,
   só **15,5%** chegam a ser nomeados pelo ChatGPT — e nas especialidades mais concorridas
   (Dermatologia) é só **5%**.
5. **A IA é instável: pergunte 2x, mude o médico em 42%.** O top recomendado muda entre duas
   perguntas idênticas em 42% das buscas — ser a resposta *consistente* é um diferencial.

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
| **Instabilidade** (top muda entre 2 reps) | **42%** |

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

Via SerpApi. Amostra: **531/540 (98%)**.

| Tipo de busca | Sem AIO (suprimido) | Quando aparece, cita médico |
|---|---|---|
| **Geral** | **35%** | 56% |
| **"melhor [especialista]"** | **42%** | **92%** |
| **"[procedimento]"** | 32% | 40% |

**Achados:**
- O Google **não mostra IA em 35% das buscas médicas** — e em **42%** quando o paciente
  procura "o melhor [especialista]". Confirma a postura conservadora do Google em saúde (YMYL).
- Mas quando **mostra** AIO no "melhor", ele **nomeia um médico em 92%** das vezes — ou seja,
  onde há IA do Google, ela também aponta nomes (e lê as mesmas fontes).

---

## Camada 2 — Visibilidade na IA (denominador real: 2.567 médicos do Doctoralia)

Roster construído a partir das listagens do Doctoralia (top ~15 por especialidade×capital,
**20 especialidades**). Cruzamos cada médico real com os nomes que a IA de fato citou na
Camada 1 (2 repetições).

> **Só 15,5% dos médicos listados chegam a ser nomeados pela IA. → 84% são invisíveis pro ChatGPT.**

| Recorte | % visível na IA |
|---|---|
| **Geral** (2.567 médicos) | **15,5%** |
| Reumatologia (maior) | 34,4% |
| **Dermatologia (menor)** | **5,2%** |
| Oftalmologia | 7,4% |
| Cirurgia Plástica | 9,7% |

**Insight de venda:** as especialidades **mais concorridas têm a MENOR visibilidade** — quanto
mais médico disputando, mais invisível cada um. É exatamente onde a dor (e a disposição a
pagar) é maior.

> Nota: o roster já é de médicos prominentes (top Doctoralia), então no universo total a
> invisibilidade é ainda **maior** — 84% é piso conservador. "Visível" = nomeado nas buscas
> da Camada 1 (mesma especialidade/cidade).

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

1. ✅ Pilar C (AIO) fechado (35% supressão, 531/540).
2. ✅ **2ª repetição** dos prompts de IA → instabilidade de 42%.
3. ✅ **Camada 2** — visibilidade na IA de 2.567 médicos reais, 20 especialidades (84% invisíveis).
   _Pendente opcional: Visibility Score completo 0-100 por médico (Google + site)._
4. Microsite + PDF consumindo o `aggregates.json`.
