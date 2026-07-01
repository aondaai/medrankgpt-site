# Relatório Robusto — Índice MedRank 2026 — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Construir um relatório longo e denso em `/indice/relatorio/` (14 seções, ~16-18 páginas impressas) que aprofunda o estudo Índice MedRank 2026, reusando o sistema visual e os dados existentes, sem inventar nenhum número.

**Architecture:** Página HTML estática com slots `data-fill`/`data-chart`, preenchida por um módulo `report.js` que importa `loadData()` (`indice/js/data.js`) e os geradores de gráfico (`indice/js/charts.js`). Derivações novas dos dados vão num namespace `reporte` adicionado a `normalizeData()` — aditivo, o microsite ignora. Dois geradores novos (`groupedBarSVG`, `tableHTML`) entram em `charts.js`. CSS de impressão deixa o print-to-PDF limpo.

**Tech Stack:** HTML5, CSS (custom properties em `tokens.css`), JavaScript ES Modules (sem build, sem deps). Verificação via `python3 -m http.server` + browser headless (skill `/browse`) ou navegador manual.

**Fonte de dados:** `indice/aggregates.json` (já existe). Regra de arredondamento: `pct(v) = Math.round(v*100 - 1e-9) + '%'` (já em `charts.js`/`main.js`). **Todos os números abaixo já foram conferidos contra `aggregates.json` com essa regra.**

---

## Contexto que o engenheiro precisa saber

- O microsite atual vive em `indice/index.html` + `indice/js/main.js` e **não pode regredir**. Ele consome campos de `normalizeData()` em `indice/js/data.js`. Qualquer mudança em `data.js`/`charts.js` deve ser **estritamente aditiva**.
- `indice/js/charts.js` exporta `bigNumberSVG(value, legenda)`, `barChartSVG(items, opts)`, `donutSVG(segments, opts)`. `items` para barra = `[{label, value, highlight?}]`. `segments` para donut = `[{label, value, color}]`. Cores usam CSS vars (`var(--viz-1)` etc.).
- `indice/js/data.js` exporta `loadData(url='./aggregates.json')` → objeto normalizado. Caminho relativo: a partir de `indice/relatorio/`, os dados estão em `../aggregates.json` e os módulos em `../js/`.
- `indice/js/specialty.js` exporta `especialidadesList(norm)` (ordena por `visivel` asc) e `specialtyValue(norm, esp)`.
- Tokens de cor/tipografia/espaço estão em `indice/tokens.css` (`--color-*`, `--font-*`, `--space-*`, `--fs-*`, `--radius-*`). Reusar, não redefinir.
- Fontes carregadas via Fontshare (Satoshi) e Google (Geist Mono) — copiar os `<link>` do `indice/index.html`.

## Estrutura de arquivos

| Arquivo | Cria/Modifica | Responsabilidade |
|---|---|---|
| `indice/relatorio/index.html` | Cria | Marcação estática das 14 seções com slots |
| `indice/relatorio/report.css` | Cria | Layout longo + tipografia de relatório + `@media print` |
| `indice/relatorio/js/report.js` | Cria | Carrega dados, preenche slots, renderiza gráficos/tabelas |
| `indice/js/charts.js` | Modifica (aditivo) | + `groupedBarSVG`, `tableHTML` |
| `indice/js/data.js` | Modifica (aditivo) | + `deriveReportInsights(raw)` → campo `reporte` |

## Números de referência (conferidos)

| Slot | Valor bruto | Exibido |
|---|---|---|
| invisíveis IA | `camada2.pct_invisivel_ia` 0.8446 | 84% |
| visíveis IA | 0.1554 | 16% |
| ChatGPT cita médico | `chatgpt.pct_cita_medico` 0.9278 | 93% |
| prompt "melhor" | `por_tipo_prompt.melhor_especialista` 0.9778 | 98% |
| prompt "confiança" | `por_tipo_prompt.confianca` 1.0 | 100% |
| prompt "procedimento" | `por_tipo_prompt.procedimento` 0.8667 | 87% |
| risco-CFM | `chatgpt.cfm_risco_pct` 0.0028 | 0,28% |
| Doctoralia como fonte | `chatgpt.doctoralia_como_fonte_pct` 0.3528 | 35% |
| instabilidade | `chatgpt.instabilidade_pct_top_medico_muda` 0.4222 | 42% |
| Doctoralia #1 ("melhor") | `serp...melhor.pos1_por_tipo.marketplace` 0.8944 | 89% |
| share marketplace ("melhor") | `serp...melhor.share_medio_por_tipo.marketplace` 0.1347 | 13% |
| marketplace #1 (procedimento) | `serp...procedimento.pos1_por_tipo.marketplace` 0.1556 | 16% |
| social #1 (procedimento) | `serp...procedimento.pos1_por_tipo.social` 0.2222 | 22% |
| Instagram #1 procedimento | `top_dominios_pos1[0]` = ["instagram.com", 76] | 76× |
| Doctoralia #1 procedimento | `top_dominios_pos1[1]` = ["doctoralia.com.br", 56] | 56× |
| SP marketplace #1 | `serp.por_cidade["São Paulo"]` 0.2667 | 27% |
| Fortaleza marketplace #1 | 0.4833 | 48% |
| sem AIO (geral) | `google_aio.pct_sem_aio` 0.3522 | 35% |
| sem AIO ("melhor") | `google_aio.sem_aio_melhor` 0.4222 | 42% |
| sem AIO (procedimento) | `google_aio.sem_aio_procedimento` 0.3162 | 32% |
| AIO presente cita médico | `google_aio.entre_presentes.pct_cita_medico` 0.5552 | 56% |
| AIO presente marketplace | `google_aio.entre_presentes.pct_marketplace` 0.1337 | 13% |
| Reumatologia visível | `camada2.por_especialidade.Reumatologia.pct` 0.3443 | 34% |
| Dermatologia visível | 0.0519 | 5% |
| ChatGPT Cardiologia | `chatgpt.por_especialidade.Cardiologia` 0.7778 | 78% |
| ChatGPT Gastroenterologia | 0.6944 | 69% |
| top médico citado | `chatgpt.top_medicos[0]` = ["Dr. Gilberto Studart", 9] | 9× |
| total médicos | `camada2.total_medicos` 2567 | 2.567 |

---

## Task 1: Scaffold da página + servidor local + baseline do microsite

**Files:**
- Create: `indice/relatorio/index.html`
- Create: `indice/relatorio/report.css`
- Create: `indice/relatorio/js/report.js`

- [ ] **Step 1: Subir servidor local na raiz do repo**

Run (na raiz `…/stupefied-torvalds-6765db`):
```bash
python3 -m http.server 8000 >/tmp/medrank-http.log 2>&1 &
```
Expected: servidor no ar. `curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/indice/index.html` → `200`.

- [ ] **Step 2: Confirmar baseline do microsite (sem regressão depois)**

Abrir `http://localhost:8000/indice/` (via `/browse` headless ou navegador) e confirmar que carrega sem erro de console e o herói mostra "84%". Anotar como baseline.
Expected: microsite OK.

- [ ] **Step 3: Criar `report.css` mínimo (só para a página abrir)**

```css
@import url("../tokens.css");

* { box-sizing: border-box; }
html { -webkit-text-size-adjust: 100%; }
body {
  margin: 0;
  background: var(--color-bg);
  color: var(--color-text);
  font-family: var(--font-sans);
  font-size: var(--fs-body);
  line-height: var(--lh-body);
}
.report { max-width: 760px; margin: 0 auto; padding: var(--space-3xl) var(--space-xl); }
```

- [ ] **Step 4: Criar `js/report.js` mínimo (carrega dados, loga, sem preencher)**

```javascript
import { loadData } from '../../js/data.js';

loadData('../aggregates.json').then((N) => {
  console.info('[relatorio] dados carregados', N.hero);
}).catch((e) => {
  document.body.insertAdjacentHTML('afterbegin',
    `<p style="color:red;padding:1rem">Erro ao carregar dados: ${e.message}</p>`);
});
```

- [ ] **Step 5: Criar `index.html` esqueleto que carrega o módulo**

```html
<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Índice MedRank 2026 — Relatório completo</title>
<meta name="description" content="Relatório completo do Índice MedRank 2026: o estado das buscas médicas com IA no Brasil. 2.567 médicos, 20 especialidades, 9 capitais, 3 superfícies de IA.">
<link rel="preconnect" href="https://api.fontshare.com">
<link href="https://api.fontshare.com/v2/css?f[]=satoshi@400,500,700,900&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Geist+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="report.css">
</head>
<body>
<main class="report" id="report">
  <p class="overline">carregando…</p>
</main>
<script type="module" src="js/report.js"></script>
</body>
</html>
```

- [ ] **Step 6: Verificar que a página abre sem erro**

Abrir `http://localhost:8000/indice/relatorio/`. Console deve mostrar `[relatorio] dados carregados {pctInvisivel: 0.8446, totalMedicos: 2567}` e **nenhum erro**.
Expected: log presente, sem erro 404/módulo.

- [ ] **Step 7: Commit**

```bash
git add indice/relatorio/
git commit -m "feat(relatorio): scaffold da página de relatório completo do Índice 2026"
```

---

## Task 2: Geradores de gráfico novos em `charts.js` (`groupedBarSVG`, `tableHTML`)

**Files:**
- Modify: `indice/js/charts.js` (append no fim; não tocar nas funções existentes)

> `groupedBarSVG` é igual ao `barChartSVG` em forma de entrada (`[{label,value,highlight}]`) mas aceita rótulo de valor customizado (`fmt`) — para mostrar "100%", "0,28%", "76×" etc. sem depender do `pct()` interno. `tableHTML` gera uma `<table>` semântica.

- [ ] **Step 1: Acrescentar `groupedBarSVG` ao fim de `indice/js/charts.js`**

```javascript
// Barras com formatador de valor custom (p/ %, ×, casas decimais). Mesma estética do barChartSVG.
export function groupedBarSVG(items, { width = 520, barH = 26, gap = 14, fmt = pct } = {}) {
  const max = Math.max(...items.map((i) => i.value), 0.0001);
  const labelW = 180, trackW = width - labelW - 70;
  const rows = items.map((it, i) => {
    const y = i * (barH + gap);
    const w = Math.max(2, (it.value / max) * trackW);
    const fill = it.highlight ? 'var(--color-accent-coral)' : 'var(--viz-1)';
    return `<text x="0" y="${y + barH * 0.7}" font-family="var(--font-sans)" font-size="14"
        fill="var(--color-text)">${esc(it.label)}</text>
    <rect x="${labelW}" y="${y}" width="${w}" height="${barH}" rx="6" fill="${fill}"/>
    <text x="${labelW + w + 8}" y="${y + barH * 0.7}" font-family="var(--font-mono)" font-size="13"
        fill="var(--color-text-muted)">${esc(fmt(it.value, it))}</text>`;
  }).join('\n');
  const h = items.length * (barH + gap);
  return `<svg viewBox="0 0 ${width} ${h}" role="img" xmlns="http://www.w3.org/2000/svg">${rows}</svg>`;
}
```

- [ ] **Step 2: Acrescentar `tableHTML` ao fim de `indice/js/charts.js`**

```javascript
// Tabela de dados semântica. headers: string[]; rows: (string|number)[][]; highlightCol opcional.
export function tableHTML(headers, rows, { caption = '' } = {}) {
  const head = `<tr>${headers.map((h) => `<th scope="col">${esc(h)}</th>`).join('')}</tr>`;
  const body = rows.map((r) =>
    `<tr>${r.map((c, i) => i === 0
      ? `<th scope="row">${esc(c)}</th>`
      : `<td>${esc(c)}</td>`).join('')}</tr>`).join('\n');
  const cap = caption ? `<caption>${esc(caption)}</caption>` : '';
  return `<table class="data-table">${cap}<thead>${head}</thead><tbody>${body}</tbody></table>`;
}
```

- [ ] **Step 3: Verificar microsite sem regressão**

Recarregar `http://localhost:8000/indice/` — herói "84%", gráficos renderizam, console limpo. (As funções novas não são usadas pelo microsite; só confirmamos que o append não quebrou o parse.)
Expected: microsite OK.

- [ ] **Step 4: Verificar as funções novas via eval no browser**

Em `http://localhost:8000/indice/relatorio/`, no console:
```javascript
const m = await import('../../js/charts.js');
m.groupedBarSVG([{label:'a',value:1,highlight:true}]).startsWith('<svg');   // true
m.tableHTML(['x','y'],[['a',1]]).includes('<table');                        // true
```
Expected: ambos `true`.

- [ ] **Step 5: Commit**

```bash
git add indice/js/charts.js
git commit -m "feat(relatorio): adiciona groupedBarSVG e tableHTML em charts.js (aditivo)"
```

---

## Task 3: Derivações de dados do relatório (`reporte` em `data.js`)

**Files:**
- Modify: `indice/js/data.js` (adicionar função + campo; não alterar campos existentes)

- [ ] **Step 1: Adicionar `deriveReportInsights(raw)` em `indice/js/data.js` (antes de `normalizeData`)**

```javascript
// Cortes extras só para o relatório longo. Aditivo: o microsite não lê nada disto.
function deriveReportInsights(raw) {
  const gpt = raw.chatgpt, serp = raw.google_serp, aio = raw.google_aio, cam = raw.camada2_visibilidade_ia;
  const tb = serp.por_tipo_busca;

  const chatgptPorEsp = Object.entries(gpt.por_especialidade)
    .map(([nome, v]) => ({ nome, cita: v.pct_cita_medico }))
    .sort((a, b) => a.cita - b.cita);

  // tabela por especialidade: visível IA · marketplace #1 Google · ChatGPT cita
  const tabelaEsp = Object.entries(cam.por_especialidade).map(([nome, v]) => ({
    nome,
    visivelIa: v.pct,
    marketplace1: serp.por_especialidade[nome]?.pct_pos1_marketplace ?? 0,
    chatgptCita: gpt.por_especialidade[nome]?.pct_cita_medico ?? 0,
  })).sort((a, b) => a.visivelIa - b.visivelIa);

  // tabela por capital: marketplace #1 · ChatGPT cita
  const tabelaCidade = Object.entries(serp.por_cidade).map(([cidade, v]) => ({
    cidade,
    marketplace1: v.pct_pos1_marketplace,
    chatgptCita: gpt.por_cidade[cidade]?.pct_cita_medico ?? 0,
  })).sort((a, b) => a.marketplace1 - b.marketplace1);

  return {
    promptChatgpt: {
      melhor: gpt.por_tipo_prompt.melhor_especialista,
      confianca: gpt.por_tipo_prompt.confianca,
      procedimento: gpt.por_tipo_prompt.procedimento,
    },
    cfmRisco: gpt.cfm_risco_pct,
    citaMedicoGeral: gpt.pct_cita_medico,
    shareMarketplaceMelhor: tb.melhor.share_medio_por_tipo.marketplace ?? 0,
    procInstagram: tb.procedimento.top_dominios_pos1.find(([d]) => d.includes('instagram')) ?? ['instagram.com', 0],
    procDoctoralia: tb.procedimento.top_dominios_pos1.find(([d]) => d.includes('doctoralia')) ?? ['doctoralia.com.br', 0],
    procSocialPos1: tb.procedimento.pos1_por_tipo.social ?? 0,
    procMarketplacePos1: tb.procedimento.pos1_por_tipo.marketplace ?? 0,
    aio: {
      presente: aio.pct_presente,
      semAio: aio.pct_sem_aio,
      semAioMelhor: aio.sem_aio_melhor,
      semAioProc: aio.sem_aio_procedimento,
      citaMedicoPresente: aio.entre_presentes.pct_cita_medico,
      marketplacePresente: aio.entre_presentes.pct_marketplace,
    },
    chatgptPorEsp,
    topMedicos: (gpt.top_medicos || []).slice(0, 8),
    tabelaEsp,
    tabelaCidade,
  };
}
```

- [ ] **Step 2: Plugar `reporte` no retorno de `normalizeData` (linha do `return {`)**

Em `normalizeData`, alterar o objeto retornado para incluir `reporte`. O `return` atual começa com `return {\n    ...deriveInsights(raw),`. Acrescentar logo abaixo:

```javascript
  return {
    ...deriveInsights(raw),
    reporte: deriveReportInsights(raw),
    hero: { pctInvisivel: c2.pct_invisivel_ia, totalMedicos: c2.total_medicos },
```
(resto do objeto permanece idêntico)

- [ ] **Step 3: Verificar microsite sem regressão**

Recarregar `http://localhost:8000/indice/` — herói "84%", console limpo. (main.js ignora `.reporte`.)
Expected: microsite OK.

- [ ] **Step 4: Verificar `reporte` via console em `/indice/relatorio/`**

```javascript
const { loadData } = await import('../../js/data.js');
const N = await loadData('../aggregates.json');
N.reporte.promptChatgpt;          // {melhor:0.9778, confianca:1, procedimento:0.8667}
N.reporte.cfmRisco;               // 0.0028
N.reporte.aio.citaMedicoPresente; // 0.5552...
N.reporte.topMedicos[0];          // ["Dr. Gilberto Studart", 9]
N.reporte.tabelaEsp.length;       // 20
N.reporte.tabelaCidade.length;    // 9
```
Expected: todos os valores conferem com a tabela de referência.

- [ ] **Step 5: Commit**

```bash
git add indice/js/data.js
git commit -m "feat(relatorio): deriva cortes extras (prompt, AIO, ChatGPT/esp, tabelas) em data.js"
```

---

## Task 4: CSS do relatório (layout longo + impressão)

**Files:**
- Modify: `indice/relatorio/report.css` (substituir o mínimo da Task 1 pelo completo)

- [ ] **Step 1: Reescrever `report.css` com o layout de relatório + print**

```css
@import url("../tokens.css");

* { box-sizing: border-box; }
html { -webkit-text-size-adjust: 100%; }
body {
  margin: 0;
  background: var(--color-bg);
  color: var(--color-text);
  font-family: var(--font-sans);
  font-size: var(--fs-body);
  line-height: var(--lh-body);
}
.report { max-width: 760px; margin: 0 auto; padding: var(--space-3xl) var(--space-xl); }

.overline {
  font-family: var(--font-mono); font-size: var(--fs-overline);
  letter-spacing: var(--tracking-overline); text-transform: uppercase;
  color: var(--color-text-muted); margin: 0 0 var(--space-sm);
}
h1 { font-size: var(--fs-display-md); font-weight: var(--w-black);
  letter-spacing: var(--tracking-display); line-height: var(--lh-snug); margin: 0 0 var(--space-md); }
.section h2 { font-size: var(--fs-h1); font-weight: var(--w-bold);
  letter-spacing: var(--tracking-display); line-height: var(--lh-snug); margin: 0 0 var(--space-sm); }
.section h3 { font-size: var(--fs-h3); font-weight: var(--w-bold); margin: var(--space-lg) 0 var(--space-xs); }
p { margin: 0 0 var(--space-md); }
.lead { font-size: var(--fs-body-lg); color: var(--color-text); }
.hl { background: var(--hl-fill); padding: 0 .08em; }
strong { font-weight: var(--w-bold); }

.section { margin: var(--space-4xl) 0; }
.section--tint { background: var(--color-bg-subtle); border-radius: var(--radius-2xl);
  padding: var(--space-2xl); margin-inline: calc(-1 * var(--space-md)); }

/* números-chave */
.kpis { display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--space-md); list-style: none; padding: 0; margin: var(--space-lg) 0; }
.kpis li { background: var(--color-surface-2); border: 1px solid var(--color-border);
  border-radius: var(--card-radius); padding: var(--space-lg); }
.kpis b { display: block; font-family: var(--font-display); font-weight: var(--w-black);
  font-size: var(--fs-display-md); color: var(--color-primary); line-height: 1; }
.kpis span { display: block; margin-top: var(--space-xs); font-size: var(--fs-body-sm); color: var(--color-text-muted); }

/* box de conclusão */
.takeaway { border-left: 4px solid var(--color-primary); background: var(--color-primary-soft);
  border-radius: var(--radius-md); padding: var(--space-md) var(--space-lg); margin: var(--space-lg) 0;
  font-size: var(--fs-body-lg); }
.takeaway::before { content: "Conclusão"; display: block; font-family: var(--font-mono);
  font-size: var(--fs-overline); letter-spacing: var(--tracking-overline); text-transform: uppercase;
  color: var(--color-primary-deep); margin-bottom: var(--space-2xs); }

/* listas e metodologia */
ol.conclusoes { padding-left: 1.2em; }
ol.conclusoes li { margin-bottom: var(--space-sm); }
ul.checklist { list-style: none; padding: 0; }
ul.checklist li { padding-left: 1.6em; position: relative; margin-bottom: var(--space-sm); }
ul.checklist li::before { content: "✓"; position: absolute; left: 0; color: var(--color-primary); font-weight: var(--w-bold); }
.meta-list, .legenda { color: var(--color-text-muted); font-size: var(--fs-body-sm); }

/* gráficos */
.chart { margin: var(--space-lg) 0; }
.chart svg { width: 100%; height: auto; }
figure { margin: 0 0 var(--space-lg); }
figcaption { font-family: var(--font-mono); font-size: var(--fs-mono-sm); color: var(--color-text-muted); margin-bottom: var(--space-xs); }
.legenda { display: flex; gap: var(--space-md); list-style: none; padding: 0; }
.legenda .dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 4px; }

/* tabelas de dados */
.data-table { width: 100%; border-collapse: collapse; font-size: var(--fs-body-sm); margin: var(--space-md) 0; }
.data-table caption { text-align: left; color: var(--color-text-muted); font-size: var(--fs-caption); margin-bottom: var(--space-xs); }
.data-table th, .data-table td { text-align: right; padding: var(--space-sm) var(--space-md); border-bottom: 1px solid var(--color-border); }
.data-table thead th { color: var(--color-text-muted); font-weight: var(--w-medium); }
.data-table th[scope="row"] { text-align: left; font-weight: var(--w-medium); }

/* CTA */
.cta-block { background: var(--color-ink-btn); color: var(--color-on-ink);
  border-radius: var(--radius-2xl); padding: var(--space-2xl); margin-top: var(--space-3xl); }
.cta-block h2 { color: var(--color-on-ink); }

footer { margin-top: var(--space-3xl); padding-top: var(--space-lg);
  border-top: 1px solid var(--color-border); color: var(--color-text-muted); font-size: var(--fs-body-sm); }
.src code { font-family: var(--font-mono); }

/* ---------- IMPRESSÃO ---------- */
@page { size: A4; margin: 16mm 14mm; }
@media print {
  body { background: #fff; }
  .report { max-width: none; padding: 0; }
  .section { margin: 0 0 10mm; }
  .section, figure, .takeaway, .kpis, .data-table, .cta-block { break-inside: avoid; }
  .section h2 { break-after: avoid; }
  .section--tint, .cta-block { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  .no-print { display: none !important; }
}
```

- [ ] **Step 2: Verificar que a página ainda abre (estilo aplicado, sem conteúdo ainda)**

Recarregar `http://localhost:8000/indice/relatorio/`. Fonte Satoshi aplicada, sem erro de console.
Expected: OK.

- [ ] **Step 3: Commit**

```bash
git add indice/relatorio/report.css
git commit -m "feat(relatorio): layout longo + CSS de impressão A4"
```

---

## Task 5: Marcação estática das 14 seções (`index.html`)

**Files:**
- Modify: `indice/relatorio/index.html` (substituir `<main>` pelo conteúdo completo)

> Todo texto fixo (headings, leads, análise) vai no HTML. Slots dinâmicos usam `data-fill="chave"` (texto) e `data-chart="chave"` (gráfico). O JS da Task 6/7 preenche as chaves. As frases de análise abaixo são o conteúdo final — escrevê-las **verbatim**.

- [ ] **Step 1: Substituir o `<main class="report">…</main>` pelo conteúdo completo**

```html
<main class="report" id="report">

  <!-- 1. SUMÁRIO EXECUTIVO -->
  <header class="section">
    <p class="overline">Índice MedRank 2026 · Relatório completo</p>
    <h1>Quando o paciente pergunta à IA "quem é o melhor médico?", ela responde — mas quase nunca cita você.</h1>
    <p class="lead">Analisamos <span data-fill="n-medicos">—</span> médicos reais em 3 superfícies de IA, 20 especialidades e 9 capitais. A IA já recomenda médicos todos os dias; o problema é que <span class="hl"><span data-fill="invisivel">—</span> deles são invisíveis para ela</span> — e os poucos visíveis vêm das mesmas fontes de sempre.</p>
    <ul class="kpis" data-fill="kpis"></ul>
    <div class="takeaway">5 conclusões em 30 segundos:
      <ol class="conclusoes" data-fill="resumo-conclusoes"></ol>
    </div>
  </header>

  <!-- 2. METODOLOGIA -->
  <section class="section">
    <h2>Como medimos</h2>
    <p>Reproduzimos as buscas que um paciente real faz e cruzamos com médicos reais. Três tipos de pergunta ("melhor [especialista] em [cidade]", uma pergunta de confiança, e a busca por um procedimento), em três superfícies, contra um roster de <span data-fill="n-medicos-2">—</span> médicos listados no Doctoralia (os ~15 mais proeminentes por especialidade × capital).</p>
    <ul class="kpis" data-fill="metodo-kpis"></ul>
    <p><strong>Superfícies:</strong> ChatGPT via API <code>gpt-4o-search-preview</code> (navega a web); Google SERP via Serper; Google AI Overview via SerpApi. <strong>"Visível"</strong> = a IA nomeou aquele médico nas buscas da mesma especialidade/cidade.</p>
    <p class="meta-list"><strong>Ressalvas honestas:</strong> IA via API é um proxy do produto de consumo; SERP e AIO refletem o momento da coleta (jun/2026); o risco-CFM é uma classificação heurística. Como o roster já é de médicos prominentes, a invisibilidade no universo total de médicos é ainda maior que a medida aqui.</p>
  </section>

  <!-- 3. A IA JÁ NOMEIA E CONFIA -->
  <section class="section">
    <h2>A IA já nomeia médicos — e confia o suficiente para isso</h2>
    <p>O ChatGPT cita um médico específico em <strong><span data-fill="cita-geral">—</span></strong> das respostas. E ele não trava por receio: quando o paciente faz uma pergunta de <em>confiança</em> ("em quem confiar para…"), a IA nomeia um médico em <strong><span data-fill="prompt-confianca">—</span></strong> das vezes. Só <strong><span data-fill="cfm-risco">—</span></strong> das respostas trazem alguma afirmação com risco perante o CFM.</p>
    <figure>
      <figcaption>ChatGPT cita um médico, por tipo de pergunta</figcaption>
      <div class="chart" data-chart="prompt-bars"></div>
    </figure>
    <div class="takeaway">A pergunta não é <em>se</em> a IA recomenda um médico — ela já recomenda. A pergunta é <strong>quem</strong> ela nomeia.</div>
  </section>

  <!-- 4. MAS LÊ AS MESMAS FONTES -->
  <section class="section">
    <h2>Mas ela lê as mesmas fontes de sempre</h2>
    <p>A IA não inventa nomes — ela lê a web e repete o que encontra. Nas respostas em que cita a origem, o <strong>Doctoralia aparece como fonte em <span data-fill="doctoralia-fonte">—</span></strong> das vezes. Quem domina as fontes que a IA lê, domina a resposta que ela dá.</p>
    <div class="takeaway">Aparecer na IA não é sobre "enganar o algoritmo": é estar, de forma consistente, nas fontes que ela já consulta.</div>
  </section>

  <!-- 5. GOOGLE: MARKETPLACE -->
  <section class="section">
    <h2>No Google, o paciente cai no marketplace</h2>
    <p>Na busca "melhor [especialista]", o <strong>Doctoralia ocupa o #1 em <span data-fill="serp-melhor">—</span></strong> das vezes. Mas há uma nuance que muda a estratégia: apesar de dominar o topo, o marketplace responde por só <strong><span data-fill="serp-share">—</span> do share médio</strong> da primeira página. Os médicos <em>estão</em> lá — só que pulverizados, cada um com uma fatia mínima, enquanto o marketplace ocupa a posição que importa.</p>
    <figure>
      <figcaption>Domínio do #1 nas buscas "melhor [especialista]"</figcaption>
      <div class="chart" data-chart="serp-donut"></div>
    </figure>
    <h3>E ele esconde o médico de forma desigual pelo país</h3>
    <p>Em <strong data-fill="regional-melhor-cidade">—</strong> o marketplace fica no #1 em só <span data-fill="regional-melhor-pct">—</span> das buscas; em <strong data-fill="regional-pior-cidade">—</strong> chega a <span data-fill="regional-pior-pct">—</span>. O Google é um jogo regional.</p>
    <figure>
      <figcaption>Marketplace no #1, por capital</figcaption>
      <div class="chart" data-chart="regional-bars"></div>
    </figure>
  </section>

  <!-- 6. A VIRADA DO PROCEDIMENTO -->
  <section class="section">
    <h2>Mas quando o paciente busca um procedimento, o jogo vira</h2>
    <p>Na busca específica ("rinoplastia", "catarata"), o marketplace despenca para <strong><span data-fill="proc-mkt">—</span></strong> dos #1 — e quem lidera passa a ser o <strong>Instagram</strong> (<span data-fill="proc-ig">—</span> no #1, à frente do próprio Doctoralia com <span data-fill="proc-doc">—</span>). Redes sociais respondem por <span data-fill="proc-social">—</span> dos #1, e sites de hospitais e clínicas aparecem com força.</p>
    <figure>
      <figcaption>"melhor [especialista]" vs "[procedimento]" — quem ocupa o #1</figcaption>
      <div class="virada-grid">
        <figure><figcaption>"melhor [especialista]"</figcaption><div class="chart" data-chart="virada-melhor"></div></figure>
        <figure><figcaption>"[procedimento]"</figcaption><div class="chart" data-chart="virada-proc"></div></figure>
      </div>
      <ul class="legenda">
        <li><span class="dot" style="background:var(--viz-4)"></span>marketplace</li>
        <li><span class="dot" style="background:var(--viz-2)"></span>Instagram</li>
        <li><span class="dot" style="background:var(--viz-1)"></span>resto</li>
      </ul>
    </figure>
    <div class="takeaway">Na busca específica, as <strong>propriedades próprias do médico</strong> — site, Instagram, página da clínica — competem de verdade pelo #1. É o terreno onde dá para vencer.</div>
  </section>

  <!-- 7. GOOGLE ESCONDE A PRÓPRIA IA -->
  <section class="section">
    <h2>O Google esconde a própria IA justamente em saúde</h2>
    <p>O Google não exibe o AI Overview em <strong><span data-fill="aio-sem">—</span></strong> das buscas — e some ainda mais na busca por especialista (<span data-fill="aio-sem-melhor">—</span> sem IA, contra <span data-fill="aio-sem-proc">—</span> em procedimento). Mas o achado que importa é o outro lado: <strong>quando o AIO aparece, ele cita um médico em <span data-fill="aio-cita">—</span></strong> das vezes e o marketplace em só <span data-fill="aio-mkt">—</span>. O AI Overview é a superfície <em>mais</em> amigável ao médico — e é a que o Google mais esconde em saúde.</p>
    <div class="takeaway">Onde a IA do Google aparece, o médico tem a melhor chance de ser nomeado. A oportunidade está em existir nas fontes para quando ela aparecer.</div>
  </section>

  <!-- 8. A CAMADA DA INVISIBILIDADE -->
  <section class="section section--tint">
    <h2><span data-fill="invisivel-2">—</span> dos médicos são invisíveis para a IA</h2>
    <p>De <span data-fill="n-medicos-3">—</span> médicos reais, só uma fração chega a ser nomeada. E a dispersão entre especialidades é enorme: <strong data-fill="esp-top-nome">—</strong> é a mais visível (<span data-fill="esp-top-pct">—</span>), enquanto <strong data-fill="esp-bot-nome">—</strong> é a mais invisível (<span data-fill="esp-bot-pct">—</span>) — uma diferença de várias vezes.</p>
    <figure>
      <figcaption>% de médicos visíveis na IA, por especialidade</figcaption>
      <div class="chart" data-chart="esp-bars"></div>
    </figure>
    <h3>E a visibilidade é concentrada em poucos nomes</h3>
    <p>Entre os que aparecem, poucos absorvem a maior parte das citações. O nome mais citado, <strong data-fill="top-medico-nome">—</strong>, foi nomeado <span data-fill="top-medico-n">—</span> — sinal de que a IA, hoje, repete um conjunto pequeno de médicos.</p>
    <figure>
      <figcaption>Médicos mais nomeados pela IA (nº de citações)</figcaption>
      <div class="chart" data-chart="top-medicos-bars"></div>
    </figure>
    <div class="takeaway">A visibilidade na IA é escassa e concentrada. Isso é uma má notícia para quem está fora — e uma vantagem clara de quem chega primeiro.</div>
  </section>

  <!-- 9. ROLETA -->
  <section class="section">
    <h2>A IA é uma roleta</h2>
    <p>Faça a mesma pergunta duas vezes e, em <strong><span data-fill="instab">—</span></strong> das vezes, o médico recomendado muda. Para o médico, ser a resposta <em>consistente</em> — a que aparece repetida, pergunta após pergunta — é um diferencial defensável.</p>
  </section>

  <!-- 10. MAPA DE OPORTUNIDADE -->
  <section class="section">
    <h2>Onde a vaga está mais aberta</h2>
    <p>Cruzando as duas pontas — invisibilidade na IA e domínio do marketplace no Google — dá para ver onde o médico está mais espremido (e onde posicionar-se vale mais). <strong data-fill="oport-top">—</strong> lidera.</p>
    <figure>
      <figcaption>Índice de oportunidade, por especialidade</figcaption>
      <div class="chart" data-chart="oport-bars"></div>
    </figure>
    <p class="meta-list">Índice de oportunidade = 60% invisibilidade na IA + 40% marketplace no #1 do Google. Composição editorial.</p>
  </section>

  <!-- 11. PLAYBOOK -->
  <section class="section">
    <h2>Dá para virar o jogo: o playbook AEO</h2>
    <p>A IA não inventa nomes — ela lê fontes. Quem aparece de forma consistente nessas fontes vira "o nome que a IA dá". É disso que trata o <strong>AEO (Answer Engine Optimization)</strong>: posicionar o médico como a resposta que ChatGPT, Gemini e o Google recomendam, dentro das regras do CFM. Na prática:</p>
    <ul class="checklist">
      <li>Perfis completos e consistentes nas fontes que a IA lê (Doctoralia e equivalentes), com mesma grafia de nome, especialidade e cidade.</li>
      <li>Site próprio com sinais técnicos que a IA entende (dados estruturados, página por especialidade e por procedimento).</li>
      <li>Conteúdo que responde às perguntas reais do paciente — inclusive por procedimento, onde as propriedades próprias competem pelo #1.</li>
      <li>Menções e presença em fontes de terceiros confiáveis, que reforçam o nome.</li>
      <li>Consistência ao longo do tempo, para virar a resposta repetida — e não a sorte da roleta.</li>
      <li>Tudo dentro da Resolução CFM de publicidade médica.</li>
    </ul>
  </section>

  <!-- 12. CONCLUSÕES -->
  <section class="section section--tint">
    <h2>Conclusões</h2>
    <ol class="conclusoes" data-fill="conclusoes"></ol>
  </section>

  <!-- 13. APÊNDICE DE DADOS -->
  <section class="section">
    <h2>Apêndice: os números por especialidade e por capital</h2>
    <div data-fill="tabela-esp"></div>
    <div data-fill="tabela-cidade"></div>
  </section>

  <!-- 14. CTA + RODAPÉ -->
  <section class="section cta-block no-print">
    <h2>Descubra se VOCÊ aparece na IA</h2>
    <p>Diagnóstico gratuito da sua visibilidade nos motores de IA — ChatGPT, Gemini e o Google.</p>
    <p><a href="../#cta" style="color:var(--color-on-ink);text-decoration:underline">Quero meu diagnóstico →</a></p>
  </section>

  <footer>
    <h3>Metodologia e ressalvas</h3>
    <ul class="meta-list" data-fill="ressalvas"></ul>
    <p class="src">Fonte: Índice MedRank 2026 · dados em <code>aggregates.json</code> · coleta jun/2026.</p>
  </footer>

</main>
```

- [ ] **Step 2: Adicionar grid da virada ao `report.css` (no fim, antes de `@media print`)**

```css
.virada-grid { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-lg); }
```

- [ ] **Step 3: Verificar que a página abre com os textos fixos (slots ainda "—")**

Recarregar `http://localhost:8000/indice/relatorio/`. Headings e parágrafos aparecem; slots mostram "—"; console sem erro.
Expected: estrutura visível, sem erro.

- [ ] **Step 4: Commit**

```bash
git add indice/relatorio/index.html indice/relatorio/report.css
git commit -m "feat(relatorio): marcação das 14 seções com textos finais e slots"
```

---

## Task 6: Preencher seções 1-7 (`report.js`)

**Files:**
- Modify: `indice/relatorio/js/report.js` (substituir o stub da Task 1)

- [ ] **Step 1: Reescrever `report.js` com helpers + fills das seções 1-7**

```javascript
import { loadData } from '../../js/data.js';
import { barChartSVG, donutSVG, groupedBarSVG, tableHTML } from '../../js/charts.js';
import { especialidadesList } from '../../js/specialty.js';

const pct = (v) => `${Math.round(v * 100 - 1e-9)}%`;
const set = (key, html) => { for (const el of document.querySelectorAll(`[data-fill="${key}"]`)) el.innerHTML = html; };
const chart = (key, svg) => { const el = document.querySelector(`[data-chart="${key}"]`); if (el) el.innerHTML = svg; };
const kpisHTML = (pairs) => pairs.map(([b, l]) => `<li><b>${b}</b><span>${l}</span></li>`).join('');

loadData('../aggregates.json').then((N) => {
  const R = N.reporte;
  const totalMed = N.hero.totalMedicos.toLocaleString('pt-BR');
  const pctInvisivel = pct(N.hero.pctInvisivel); // 0.8446 -> "84%"

  // ---- 1. SUMÁRIO EXECUTIVO ----
  set('n-medicos', totalMed);
  set('n-medicos-2', totalMed);
  set('n-medicos-3', totalMed);
  set('invisivel', pctInvisivel);
  set('kpis', kpisHTML([
    [pctInvisivel, 'médicos invisíveis para a IA'],
    [pct(R.citaMedicoGeral), 'das respostas citam um médico'],
    [pct(N.serp.melhorMarketplacePos1), 'das buscas: Doctoralia no #1'],
    [pct(N.chatgpt.instabilidade), 'das vezes a resposta muda'],
    [pct(R.aio.semAio), 'das buscas sem IA do Google'],
    [totalMed, 'médicos reais analisados'],
  ]));
  set('resumo-conclusoes', [
    `A IA já nomeia um médico em ${pct(R.citaMedicoGeral)} das respostas — o jogo é quem ela cita.`,
    `${pct(N.chatgpt.instabilidade)} das respostas mudam o médico recomendado: consistência é diferencial.`,
    `No Google, o Doctoralia fica no #1 em ${pct(N.serp.melhorMarketplacePos1)} das buscas por especialista.`,
    `Na busca por procedimento, propriedades próprias (site, Instagram) competem pelo #1.`,
    `${pctInvisivel} dos médicos são invisíveis para a IA — e os visíveis são poucos e concentrados.`,
  ].map((t) => `<li>${t}</li>`).join(''));

  // ---- 2. METODOLOGIA ----
  set('metodo-kpis', kpisHTML([
    [N.meta.especialidades, 'especialidades'],
    [N.meta.capitais, 'capitais'],
    ['3', 'superfícies de IA'],
  ]));

  // ---- 3. A IA JÁ NOMEIA E CONFIA ----
  set('cita-geral', pct(R.citaMedicoGeral));
  set('prompt-confianca', pct(R.promptChatgpt.confianca));
  set('cfm-risco', '0,28%');
  chart('prompt-bars', groupedBarSVG([
    { label: '"em quem confiar"', value: R.promptChatgpt.confianca, highlight: true },
    { label: '"melhor especialista"', value: R.promptChatgpt.melhor },
    { label: '"[procedimento]"', value: R.promptChatgpt.procedimento },
  ]));

  // ---- 4. FONTES ----
  set('doctoralia-fonte', pct(N.chatgpt.doctoraliaFonte));

  // ---- 5. GOOGLE: MARKETPLACE ----
  set('serp-melhor', pct(N.serp.melhorMarketplacePos1));
  set('serp-share', pct(R.shareMarketplaceMelhor));
  chart('serp-donut', donutSVG([
    { label: 'Doctoralia (#1)', value: N.serp.melhorMarketplacePos1, color: 'var(--viz-4)' },
    { label: 'resto', value: 1 - N.serp.melhorMarketplacePos1, color: 'var(--viz-1)' },
  ]));
  const reg = N.regional;
  set('regional-melhor-cidade', reg[0].cidade);
  set('regional-melhor-pct', pct(reg[0].marketplaceGoogle));
  set('regional-pior-cidade', reg[reg.length - 1].cidade);
  set('regional-pior-pct', pct(reg[reg.length - 1].marketplaceGoogle));
  chart('regional-bars', barChartSVG(reg.map((r, i) => ({
    label: r.cidade, value: r.marketplaceGoogle, highlight: i === 0,
  }))));

  // ---- 6. VIRADA DO PROCEDIMENTO ----
  set('proc-mkt', pct(R.procMarketplacePos1));
  set('proc-ig', `${R.procInstagram[1]}×`);
  set('proc-doc', `${R.procDoctoralia[1]}×`);
  set('proc-social', pct(R.procSocialPos1));
  const viradaDonut = (mkt, social) => donutSVG([
    { label: 'marketplace', value: mkt, color: 'var(--viz-4)' },
    { label: 'Instagram', value: social, color: 'var(--viz-2)' },
    { label: 'resto', value: Math.max(0, 1 - mkt - social), color: 'var(--viz-1)' },
  ]);
  chart('virada-melhor', viradaDonut(N.virada.melhorMarketplace, N.virada.melhorSocial));
  chart('virada-proc', viradaDonut(R.procMarketplacePos1, R.procSocialPos1));

  // ---- 7. AIO ----
  set('aio-sem', pct(R.aio.semAio));
  set('aio-sem-melhor', pct(R.aio.semAioMelhor));
  set('aio-sem-proc', pct(R.aio.semAioProc));
  set('aio-cita', pct(R.aio.citaMedicoPresente));
  set('aio-mkt', pct(R.aio.marketplacePresente));

  // (seções 8-14 na Task 7)
  window.__N = N; // facilita verificação no console
}).catch((e) => {
  document.body.insertAdjacentHTML('afterbegin',
    `<p style="color:red;padding:1rem">Erro ao carregar dados: ${e.message}</p>`);
});
```

- [ ] **Step 2: Verificar fills das seções 1-7 no browser**

Recarregar `http://localhost:8000/indice/relatorio/`. Conferir:
- Sumário: KPIs mostram 84% / 93% / 89% / 42% / 35% / 2.567; "5 conclusões" preenchidas.
- Seção 3: gráfico de prompts com "em quem confiar" 100% (barra coral), "melhor" 98%, "procedimento" 87%; texto "0,28%".
- Seção 5: donut + barras por capital (SP 27% no topo coral, Fortaleza 48% no fim); "13% do share".
- Seção 6: dois donuts; "16%", "76×", "56×", "22%".
- Seção 7: "35%", "42%", "32%", "56%", "13%".
- Console **sem erro**.
Expected: tudo conforme a tabela de referência.

- [ ] **Step 3: Commit**

```bash
git add indice/relatorio/js/report.js
git commit -m "feat(relatorio): preenche seções 1-7 (sumário, metodologia, IA, fontes, Google, virada, AIO)"
```

---

## Task 7: Preencher seções 8-14 (`report.js`)

**Files:**
- Modify: `indice/relatorio/js/report.js` (inserir antes da linha `window.__N = N;`)

- [ ] **Step 1: Inserir os fills das seções 8-14 antes de `window.__N = N;`**

```javascript
  // ---- 8. INVISIBILIDADE ----
  set('invisivel-2', pctInvisivel);
  const espList = especialidadesList(N); // asc por visível
  const espTop = espList[espList.length - 1]; // mais visível
  const espBot = espList[0];                  // mais invisível
  set('esp-top-nome', espTop.nome);
  set('esp-top-pct', pct(espTop.visivel));
  set('esp-bot-nome', espBot.nome);
  set('esp-bot-pct', pct(espBot.visivel));
  chart('esp-bars', barChartSVG(
    espList.slice(0, 12).map((e) => ({ label: e.nome, value: e.visivel, highlight: e.nome === espBot.nome })),
  ));
  const topMed = R.topMedicos[0];
  set('top-medico-nome', topMed[0]);
  set('top-medico-n', `${topMed[1]} vezes`);
  chart('top-medicos-bars', groupedBarSVG(
    R.topMedicos.map((m, i) => ({ label: m[0], value: m[1], highlight: i === 0 })),
    { fmt: (v) => `${v}×` },
  ));

  // ---- 9. ROLETA ----
  set('instab', pct(N.chatgpt.instabilidade));

  // ---- 10. OPORTUNIDADE ----
  set('oport-top', N.oportunidade[0].especialidade);
  chart('oport-bars', barChartSVG(
    N.oportunidade.slice(0, 12).map((o, i) => ({ label: o.especialidade, value: o.scoreDor, highlight: i === 0 })),
  ));

  // ---- 12. CONCLUSÕES ----
  set('conclusoes', [
    `A IA já recomenda médicos: o ChatGPT nomeia um médico em ${pct(R.citaMedicoGeral)} das respostas, e em ${pct(R.promptChatgpt.confianca)} quando a pergunta é de confiança.`,
    `A IA é segura o bastante para isso: só 0,28% das respostas trazem afirmação com risco-CFM.`,
    `A IA repete as fontes existentes: cita o Doctoralia como fonte em ${pct(N.chatgpt.doctoraliaFonte)} das vezes.`,
    `No Google, o marketplace fica no #1 em ${pct(N.serp.melhorMarketplacePos1)} das buscas por especialista — mas com só ${pct(R.shareMarketplaceMelhor)} do share da página.`,
    `O domínio do marketplace é regional: de ${pct(N.regional[0].marketplaceGoogle)} (${N.regional[0].cidade}) a ${pct(N.regional[N.regional.length - 1].marketplaceGoogle)} (${N.regional[N.regional.length - 1].cidade}).`,
    `Na busca por procedimento, o marketplace cai para ${pct(R.procMarketplacePos1)} dos #1 e o Instagram lidera — as propriedades próprias do médico competem.`,
    `O AI Overview é a superfície mais amigável ao médico (cita médico em ${pct(R.aio.citaMedicoPresente)}, marketplace em ${pct(R.aio.marketplacePresente)}) — e o Google a esconde em ${pct(R.aio.semAioMelhor)} das buscas por especialista.`,
    `${pctInvisivel} dos ${N.hero.totalMedicos.toLocaleString('pt-BR')} médicos são invisíveis para a IA.`,
    `A visibilidade é desigual (${espTop.nome} ${pct(espTop.visivel)} vs ${espBot.nome} ${pct(espBot.visivel)}) e concentrada (${topMed[0]} citado ${topMed[1]}×).`,
    `A resposta da IA é instável (${pct(N.chatgpt.instabilidade)} muda): ser a resposta consistente, dentro do CFM, é a vantagem que o AEO constrói.`,
  ].map((t) => `<li>${t}</li>`).join(''));

  // ---- 13. APÊNDICE: TABELAS ----
  set('tabela-esp', tableHTML(
    ['Especialidade', 'Visível na IA', 'Marketplace #1', 'ChatGPT cita'],
    R.tabelaEsp.map((r) => [r.nome, pct(r.visivelIa), pct(r.marketplace1), pct(r.chatgptCita)]),
    { caption: 'Por especialidade (ordenado por visibilidade na IA)' },
  ));
  set('tabela-cidade', tableHTML(
    ['Capital', 'Marketplace #1', 'ChatGPT cita'],
    R.tabelaCidade.map((r) => [r.cidade, pct(r.marketplace1), pct(r.chatgptCita)]),
    { caption: 'Por capital (ordenado por domínio do marketplace)' },
  ));

  // ---- 14. RESSALVAS ----
  set('ressalvas', (N.meta.ressalvas || []).map((r) => `<li>${r}</li>`).join(''));
```

- [ ] **Step 2: Verificar fills das seções 8-14 no browser**

Recarregar `http://localhost:8000/indice/relatorio/`. Conferir:
- Seção 8: título "84%"; barras por especialidade (Dermatologia 5% coral no topo da lista invertida — atenção: `slice(0,12)` da lista asc mostra as 12 menos visíveis, Dermatologia primeiro); "Dr. Gilberto Studart … 9 vezes"; barras de top médicos com "9×", "6×"…
- Seção 10: barras de oportunidade (Psiquiatria no topo).
- Seção 12: 10 conclusões numeradas, cada uma com número.
- Seção 13: tabela por especialidade com 20 linhas (4 colunas) + tabela por capital com 9 linhas (3 colunas).
- Rodapé: 3 ressalvas.
- **Nenhum "—" remanescente** em toda a página; console sem erro.
Expected: relatório completo preenchido.

- [ ] **Step 3: Commit**

```bash
git add indice/relatorio/js/report.js
git commit -m "feat(relatorio): preenche seções 8-14 (invisibilidade, roleta, oportunidade, conclusões, tabelas)"
```

---

## Task 8: Verificação de impressão + regressão final

**Files:** nenhum (verificação)

- [ ] **Step 1: Varredura de slots vazios**

No console de `http://localhost:8000/indice/relatorio/`:
```javascript
[...document.querySelectorAll('[data-fill],[data-chart]')].filter(el => el.innerHTML.trim() === '—' || el.innerHTML.trim() === '').map(el => el.dataset.fill || el.dataset.chart);
```
Expected: `[]` (array vazio).

- [ ] **Step 2: Verificar impressão (print-to-PDF)**

Abrir a página no navegador, Imprimir → Salvar como PDF (A4). Conferir: seções e figuras não quebram no meio; tabelas inteiras; fundos das seções tint e do CTA aparecem; nenhuma barra de rolagem/elemento cortado. (Alternativa headless, se disponível: `chrome --headless --print-to-pdf`.)
Expected: PDF limpo de ~16-18 páginas.

- [ ] **Step 3: Regressão do microsite**

Recarregar `http://localhost:8000/indice/` — herói "84%", todos os gráficos, formulário e link de PDF presentes; console sem erro.
Expected: microsite idêntico ao baseline da Task 1.

- [ ] **Step 4: Encerrar o servidor local**

```bash
kill %1 2>/dev/null || pkill -f "http.server 8000"
```

- [ ] **Step 5: Commit final (se houver ajuste) e fim**

Se algum ajuste foi feito nos passos acima, commitar. Caso contrário, plano concluído.

```bash
git add -A && git commit -m "chore(relatorio): ajustes finais de impressão/regressão" --allow-empty
```

---

## Notas de verificação por seção (referência rápida)

- Seção 3 gráfico: a barra de "confiança" é 100% (`highlight` coral) e é a mais longa.
- Seção 5: o donut mostra ~89% coral; barras por capital usam `N.regional` (asc), SP primeiro (coral), Fortaleza por último.
- Seção 6 donut "melhor": usa `N.virada.melhorMarketplace`/`N.virada.melhorSocial` (já derivados em `data.js`), sem números inline.
- Seção 8 barras: `especialidadesList` ordena asc por visível; `slice(0,12)` mostra as 12 menos visíveis (Dermatologia 5% primeiro, destaque coral). Isso é intencional — a seção é sobre invisibilidade.
- Apêndice: `pct()` arredonda; valores batem com a tabela de referência.
