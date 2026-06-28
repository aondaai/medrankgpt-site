# Índice MedRank 2026 — Design (spec guarda-chuva)

> **O Estado das Buscas Médicas na Era da IA** — relatório-isca (lead magnet)
> proprietário, primeira edição de um índice anual.
> Data: 2026-06-28 · Status: aprovado para virar plano de implementação (por frente).

## 1. Objetivo e premissas

**Objetivo de negócio:** gerar leads qualificados (médicos/clínicas Tier A e gestores de
marketing em saúde) e autoridade de categoria/PR, a partir de **dados proprietários** que
só o MedRankGPT tem — a CLI `medrank-visibility`.

**Decisões já tomadas no brainstorming:**

| Decisão | Escolha |
|--------|---------|
| Fonte de dados | Estudo proprietário real (CLI rodada em escala) |
| Desenho da amostra | Nacional em camadas (manchete nacional ampla + mergulhos profundos) |
| Lente analítica | **Combinada**: Camada 1 = lado da demanda (visão do paciente); Camada 2 = lado da oferta (Visibility Score) |
| Formato | Microsite público + PDF completo *gated* por e-mail |
| Escopo deste spec | Programa inteiro (4 frentes), decomposto em workstreams |
| Captura de leads | Google Sheet (v1) |
| Orçamento de API | Sem teto definido — dimensionar via modelo de custo (§7) |

**Posicionamento:** "Índice MedRank 2026". Primeira edição de um índice **anual** —
o MedRankGPT vira dono da categoria. Subtítulo: *"Como os pacientes estão usando IA para
escolher médicos — e o que isso significa para o seu posicionamento."*
(Nomes alternativos a decidir: "Raio-X das Buscas Médicas com IA 2026", "O Paciente-IA 2026".)

**Restrições:**
- Tudo dentro das regras do CFM (o relatório, inclusive, *mede* violações de CFM nas
  respostas das IAs — então não pode cometer as mesmas).
- Médicos individuais aparecem **somente anonimizados/agregados** no relatório público
  (privacidade + evitar parecer "lista de bons/maus médicos"). Nomes reais ficam só nos
  dados brutos internos.
- PT-BR, mercado Brasil.

## 2. Visão de arquitetura (4 frentes)

```
[Frente 1: Engine de dados] --aggregates.json--> [Frente 2: Microsite]
        |                                                |
        |                                                +--> [Frente 3: PDF + captura -> Google Sheet]
        +--rosters/prompts (input)                            |
                                                              v
                                              [Frente 4: Distribuição / PR / AEO / e-mail]
```

**Tudo depende da Frente 1.** Ordem de implementação: 1 → (2 ∥ 3) → 4.

---

## 3. Frente 1 — Engine de dados  *(coração do projeto)*

Reaproveita `visibility/` (collectors reais: SerpApi, Google Places, OpenAI/Perplexity/
Gemini, httpx). Três entregas:

### 3a. Runner do lado da demanda (NOVO)

Hoje `collectors/ai_engines.py` é **médico-cêntrico** (recebe um `DoctorMeta` e pergunta
sobre ele). A Camada 1 precisa do inverso: rodar **perguntas de paciente** sem médico
pré-definido e analisar a resposta.

- **Entrada:** matriz de prompts = especialidades × cidades × tipos-de-prompt × motores × repetições.
  - Tipos de prompt (mín.): `melhor_especialista` ("Quem é o melhor [esp] em [cidade]?"),
    `procedimento` ("Quem faz [procedimento] em [cidade]?"), `confianca`
    ("Indique um(a) [esp] de confiança em [cidade]").
  - Repetições (R) por combinação para medir estabilidade da resposta.
- **Saída por resposta:** texto bruto + metadados (especialidade, cidade, tipo, motor, rep, timestamp).
- **Reuso:** o `LLMClient` / `build_engines()` de `config.py` é reaproveitado tal qual.

### 3b. Classificador de respostas (NOVO — componente analítico central)

Para cada resposta da Camada 1, extrair:
1. **Entidades citadas** e seu **tipo**: `medico_nominal` | `marketplace`
   (Doctoralia, BoaConsulta, etc.) | `clinica` | `hospital` | `conteudo_generico` | `nenhum`.
2. **Share of voice**: contagem/posição das entidades por combinação (concentração).
3. **Flag de risco-CFM**: presença de alegações vedadas (promessa de resultado,
   superlativo "o melhor", garantia, etc.) — heurística + confirmação por LLM.

> **Decisão de implementação (no plano):** classificação heurística (listas + regex de
> marketplaces/superlativos) **primeiro**, com passe de LLM só onde a heurística ficar
> ambígua — controla custo. Reaproveita `names.py` (`mentioned_names`, `same_person`).

### 3c. Batch do Visibility Score + agregação (lado da oferta — Camada 2)

- **Entrada:** roster de médicos reais por especialidade (2-3 especialidades eletivas:
  ex. Dermatologia, Cirurgia Plástica + 1 a confirmar).
  - **Sourcing do roster:** listagens públicas de Doctoralia/BoaConsulta por especialidade+
    cidade (nome + cidade/UF bastam de entrada; ver `DoctorMeta`). *Item aberto §8.*
- **Processo:** rodar a CLI atual (`visibility.cli`) por médico → relatório JSON pontuado.
- **Saída:** agregação **anonimizada** — distribuição de scores (mediana, percentis, %<limiar),
  desempenho por categoria das 4, e o perfil do **top 10%** (o que correlaciona com score alto).

### 3d. Export de agregados

- Um único `aggregates.json` (schema versionado, no espírito de
  `schema/ai_visibility_score_1_0.json`) consumido por Frente 2 e Frente 3.
- **Nenhum dado pessoal** no `aggregates.json` — só números agregados e exemplos
  anonimizados.

**Interfaces da Frente 1:** entrada = arquivos de config (matriz de prompts, rosters);
saída = `aggregates.json` + dados brutos internos (não publicados). CLI nova:
`medrank-study` (ou subcomandos da CLI existente) — definir no plano.

---

## 4. Frente 2 — Microsite

- Página interativa pública com os gráficos-manchete (Camadas 1 e 2), consumindo
  `aggregates.json`.
- **Reuso obrigatório:** `DESIGN.md` + `design-system/` (Satoshi/Geist Mono, paleta
  "Crescimento", data-viz colorida). Sem inventar estilo.
- Excelente para **SEO/AEO** (é a própria competência da empresa — a página deve ser
  citável por IA): headings semânticos, FAQ, dados estruturados.
- Seções: sumário/5 manchetes → Camada 1 → Camada 2 → playbook → CTA.
- **Hospedagem:** site já vive em Render (ver memória de infra). Página nova no mesmo deploy.

## 5. Frente 3 — PDF + captura de lead

- **Relatório completo em PDF** desenhado (skill `make-pdf` / `document-generate`),
  marca MedRankGPT, mesma identidade do microsite.
- **Gate:** formulário de e-mail no microsite libera o PDF.
- **Destino do lead:** **Google Sheet** (v1). Form → endpoint → append na planilha.
  (Integração com Apollo/CRM fica para depois.)
- **CTA pós-download:** "Peça seu AI Visibility Score grátis" → captura lead quente;
  a auditoria individual é entregue como follow-up de vendas usando a CLI atual
  (automação por-lead **fora de escopo** v1).

## 6. Frente 4 — Distribuição

- PR/imprensa com a manchete nacional; AEO/SEO da página; sequência de e-mail pós-download.
- Fora do escopo de engenharia; vira playbook + assets. Plano próprio, por último.

## 7. Modelo de custo de API (para dimensionar amostra)

Estimativa de ordem de grandeza (confirmar preços no plano):

- **Camada 1 (demanda):** custo ≈ `S × C × P × E × R` chamadas de LLM.
  Ex.: 10 esp × 6 cidades × 3 tipos × 4 motores × 3 reps = **2.160 chamadas** ≈ US$40–65
  (~US$0,02–0,03/chamada). Classificação: heurística-primeiro mantém o passe de LLM baixo.
- **Camada 2 (oferta):** ≈ US$0,20–0,40 por médico (LLM prompts + 1 SerpApi + 1 Places +
  fetch de site). 3 esp × 50 médicos = 150 → **US$30–60**.
- **Total** de um estudo robusto: **~US$100–250**. Pilotos menores cabem em <US$50.

Saída deste modelo: o usuário escolhe `S, C, P, E, R` e tamanho de roster com o custo à vista.

## 8. Itens abertos (resolver no início de cada plano)

1. **Sourcing do roster** (Frente 1c): scrape de Doctoralia/BoaConsulta vs lista curada —
   verificar ToS e robustez. *Bloqueia a Camada 2.*
2. **3ª especialidade** dos mergulhos (Dermatologia + Cirurgia Plástica + ?).
3. **Endpoint do formulário → Google Sheet** (Frente 3): Apps Script webhook vs serviço
   (ex. Sheety/serverless no Render). Decidir no plano da Frente 3.
4. **Nome final** do índice.
5. **Validade do proxy-API**: declarar claramente na metodologia que as APIs (gpt-4o,
   sonar, gemini) aproximam — não replicam exatamente — o produto de consumo.

## 9. Critérios de sucesso (verificáveis)

- **Frente 1:** `aggregates.json` válido contra schema, gerado de ponta a ponta a partir
  de configs, sem dado pessoal; números reproduzíveis com `--now`/seed fixos.
- **Frente 2:** microsite renderiza todos os gráficos a partir do `aggregates.json`,
  responsivo, fiel ao `DESIGN.md`, com marcação AEO.
- **Frente 3:** download do PDF gated funciona e o e-mail aparece na Google Sheet.
- **Programa:** uma manchete nacional defensável + distribuição de scores por especialidade,
  publicados, com metodologia transparente.

## 10. Plano de execução

Tratar como **programa**. Cada frente vira seu próprio ciclo *spec detalhado → plano →
implementação*, nesta ordem:

1. **Frente 1 (engine de dados)** — primeiro e bloqueante.
2. **Frente 2 (microsite)** e **Frente 3 (PDF+captura)** — em paralelo após os dados existirem.
3. **Frente 4 (distribuição)** — por último.

Este documento é o spec guarda-chuva; os planos por frente derivam dele.
