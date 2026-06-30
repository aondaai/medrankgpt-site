# Índice MedRank 2026 — Microsite (Frente 2) — Design

> Microsite público scrollytelling que transforma o `aggregates.json` (resultados do estudo)
> no ativo de captação de leads do MedRankGPT. Data: 2026-06-29.

## 1. Objetivo

Publicar os resultados do Índice MedRank 2026 num **microsite público, scrollytelling**, que
(a) seja altamente link­ável e citável por IA (AEO/SEO — a própria competência da empresa),
e (b) **capture leads** de médicos/clínicas via um diagnóstico personalizado + PDF gated.

**Decisões do brainstorming:**

| Decisão | Escolha |
|--------|---------|
| Herói | "**84% dos médicos são invisíveis para a IA**" |
| Formato | Scrollytelling de uma página + **seletor "sua especialidade"** |
| Captura | Diagnóstico grátis (CTA-herói) + PDF completo gated; ambos → Google Sheet |
| Tech | Estático autossuficiente (HTML/CSS/JS vanilla) consumindo `aggregates.json` |
| Identidade | `DESIGN.md` (Satoshi/Geist Mono, paleta "Crescimento", data-viz colorida) |

## 2. Fonte de dados

Consome [`studies/results/aggregates.json`](../../../studies/results/aggregates.json) (já no
repo). Chaves usadas: `chatgpt` (pct_cita_medico, doctoralia_como_fonte_pct, instabilidade,
por_tipo_prompt), `google_serp` (por_tipo_busca, top_dominios_pos1), `google_aio`
(pct_sem_aio, sem_aio_melhor), `camada2_visibilidade_ia` (pct_invisivel_ia, por_especialidade),
`meta` (especialidades, capitais, ressalvas).

O site **lê o JSON em runtime** (fetch) — nada de números hard-coded no HTML. Trocar o estudo
(ex.: edição 2027) = trocar o JSON.

## 3. Estrutura (9 telas scrollytelling)

| # | Tela | Dado / gráfico |
|---|------|----------------|
| 1 | **Herói** | "84%" gigante animado + subtítulo + seta de scroll |
| 2 | **O experimento** | metodologia: 20 esp × 9 capitais × 3 superfícies, 2.567 médicos |
| 3 | **Google → Doctoralia** | 89% #1 = marketplace; composição do #1 (donut/barra) |
| 4 | **ChatGPT nomeia, lê o Doctoralia** | 93% cita médico; 35% cita Doctoralia como fonte |
| 5 | **Google esconde a IA** | 35% sem AIO (42% no "melhor") |
| 6 | **Clímax: 84% invisíveis + seletor** | barra por especialidade + `<select>` "sua especialidade" → número do médico |
| 7 | **A IA é uma roleta** | 42% muda o top médico entre 2 reps |
| 8 | **A virada (playbook)** | o que fazer — pitch AEO suave (texto) |
| 9 | **CTA + rodapé** | diagnóstico grátis (form) + PDF gated + metodologia/ressalvas |

## 4. Componentes (unidades isoladas)

- **`index.html`** — markup semântico das 9 seções (headings hierárquicos p/ AEO, FAQ/JSON-LD).
- **`styles.css`** — usa tokens do `design-system/` (importa `tokens.css` se possível).
- **`data.js`** — carrega `aggregates.json`, expõe um objeto normalizado p/ os componentes.
- **`charts.js`** — funções puras que recebem dados e devolvem SVG (barra, donut, número-grande).
  Cada tipo de gráfico é uma função isolada e testável (dado → string SVG).
- **`specialty-selector.js`** — o widget interativo da tela 6 (lê `por_especialidade`, atualiza o número/barra ao trocar a opção).
- **`capture.js`** — submit do form do diagnóstico + gate do PDF → endpoint do Sheet (endpoint configurável numa constante; integração real é da Frente 3).

**Interface de cada unidade:** recebe dados via parâmetro, sem estado global escondido; `charts.js`
é pura (testável headless); `data.js` é o único que faz fetch.

## 5. AEO/SEO (requisito, não enfeite)

- Headings semânticos (`h1` = herói, `h2` por seção), texto real (não só imagem).
- **JSON-LD** (`Dataset` + `FAQPage`) com as manchetes — pra ser citável por IA.
- `<title>`, meta description, OpenGraph, `sitemap`/`robots` da página.
- Cada manchete escrita como uma afirmação extraível (frase-resposta).

## 6. Critérios de sucesso (verificáveis)

- Todas as 9 telas renderizam a partir do `aggregates.json` (zero número hard-coded).
- O seletor de especialidade mostra o valor correto de `por_especialidade` ao trocar a opção.
- `charts.js` testável: cada função, dado um input fixo, produz SVG determinístico (snapshot).
- Responsivo (mobile-first) e fiel ao `DESIGN.md`.
- Marcação AEO presente (JSON-LD valida).
- Form de captura coleta nome/especialidade/cidade/email e chama o endpoint (mockável).

## 7. Itens abertos (não bloqueiam a construção)

1. **Hospedagem/deploy:** `main` (site ao vivo) tem história git não relacionada — o microsite
   provavelmente vira **site estático standalone** (ex.: `indice.medrankgpt.com.br` no Render) ou
   é **copiado** para o site principal. Decidir na hora do deploy. Ver [[medrankgpt-repo-unrelated-histories]].
2. **Endpoint do Google Sheet** (Frente 3): Apps Script webhook vs serverless.
3. **Geração do PDF** (Frente 3): a partir do mesmo conteúdo.
4. **Nome final** confirmado: "Índice MedRank 2026" (alternativas no doc de resultados).

## 8. Fora de escopo (outras Frentes)

- PDF gated + integração real do Sheet → **Frente 3**.
- PR/distribuição/e-mail → **Frente 4**.
- Visibility Score 0-100 por médico → v2 do estudo.

Este é o spec da **Frente 2 (microsite)**. Deriva do spec guarda-chuva
[`2026-06-28-indice-medrank-2026-design.md`](2026-06-28-indice-medrank-2026-design.md).
