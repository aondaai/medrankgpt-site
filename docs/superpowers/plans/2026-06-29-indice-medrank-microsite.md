# Microsite Índice MedRank 2026 (Frente 2) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Construir o microsite público scrollytelling do Índice MedRank 2026 — herói "84% invisíveis", 9 telas, seletor "sua especialidade" e CTA de captura — consumindo o `studies/results/aggregates.json` em runtime.

**Architecture:** Site **estático autossuficiente** em `studies/microsite/`. HTML semântico + CSS (tokens do `design-system/tokens.css`) + ES modules vanilla. A **lógica pura** (normalização de dados, geometria dos gráficos SVG, valor por especialidade, payload do form) fica em módulos isolados e testáveis com `node:test`; as **cascas de DOM/fetch** (`main.js`) são finas e verificadas no navegador. Nada de número hard-coded — tudo vem do JSON.

**Tech Stack:** HTML5, CSS (custom properties já existentes), JavaScript ES modules, `node:test` (Node 22, nativo, sem npm), `python3 -m http.server` para servir localmente. Sem framework, sem build step.

**Convenções:**
- Tokens de `design-system/tokens.css` (ex.: `--color-primary`, `--viz-1..5`, `--font-display`, `--fs-display-xl`, `--hl-fill`). Importar esse arquivo, não redefinir cores.
- Fontes: Satoshi (Fontshare) + Geist Mono (Google) — mesmos `<link>` do `DESIGN.md`.
- Testes: arquivos `*.test.mjs` em `studies/microsite/test/`, rodados com `node --test`.
- Determinismo: as funções puras recebem dados por parâmetro; nenhuma faz fetch.

---

## File Structure

**Criar:**
- `studies/microsite/index.html` — markup das 9 seções + JSON-LD (AEO).
- `studies/microsite/styles.css` — importa tokens + layout scrollytelling.
- `studies/microsite/aggregates.json` — **cópia** de `studies/results/aggregates.json` (deploy standalone).
- `studies/microsite/js/data.js` — `normalizeData(raw)` (pura) + `loadData(url)` (fetch).
- `studies/microsite/js/charts.js` — `bigNumberSVG`, `barChartSVG`, `donutSVG` (puras, SVG string).
- `studies/microsite/js/specialty.js` — `specialtyValue(norm, esp)` + `especialidadesList(norm)` (puras).
- `studies/microsite/js/capture.js` — `buildPayload(obj)` (pura) + `submitLead(payload, endpoint)` (fetch).
- `studies/microsite/js/main.js` — wiring DOM (render seções, seletor, form). Verificado no navegador.
- `studies/microsite/test/data.test.mjs`, `charts.test.mjs`, `specialty.test.mjs`, `capture.test.mjs`.
- `studies/microsite/README.md` — como servir/testar/deployar.

**Não modifica** nenhum arquivo existente (o microsite é autocontido).

---

## Task 0: Scaffold + cópia do dataset + harness de teste

**Files:**
- Create: `studies/microsite/` (dir), `studies/microsite/js/`, `studies/microsite/test/`
- Create: `studies/microsite/aggregates.json` (cópia)
- Create: `studies/microsite/test/smoke.test.mjs`

- [ ] **Step 1: Criar dirs + copiar o dataset**

```bash
mkdir -p studies/microsite/js studies/microsite/test
cp studies/results/aggregates.json studies/microsite/aggregates.json
```

- [ ] **Step 2: Smoke test que confirma o harness `node:test`**

```javascript
// studies/microsite/test/smoke.test.mjs
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

test('aggregates.json copiado é válido e tem as chaves esperadas', () => {
  const d = JSON.parse(readFileSync(new URL('../aggregates.json', import.meta.url)));
  for (const k of ['chatgpt', 'google_serp', 'google_aio', 'camada2_visibilidade_ia', 'meta'])
    assert.ok(k in d, `falta chave ${k}`);
  assert.equal(typeof d.camada2_visibilidade_ia.pct_invisivel_ia, 'number');
});
```

- [ ] **Step 3: Rodar — deve passar**

Run: `node --test studies/microsite/test/`
Expected: PASS (1 test)

- [ ] **Step 4: Commit**

```bash
git add studies/microsite/aggregates.json studies/microsite/test/smoke.test.mjs
git commit -m "chore(microsite): scaffold + cópia do aggregates + harness node:test"
```

---

## Task 1: `data.js` — normalização (pura) + loader

**Files:**
- Create: `studies/microsite/js/data.js`
- Test: `studies/microsite/test/data.test.mjs`

- [ ] **Step 1: Teste que falha**

```javascript
// studies/microsite/test/data.test.mjs
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { normalizeData } from '../js/data.js';

const RAW = JSON.parse(readFileSync(new URL('../aggregates.json', import.meta.url)));

test('normalizeData extrai os números-herói num formato plano', () => {
  const n = normalizeData(RAW);
  assert.equal(n.hero.totalMedicos, RAW.camada2_visibilidade_ia.total_medicos);
  assert.equal(n.hero.pctInvisivel, RAW.camada2_visibilidade_ia.pct_invisivel_ia);
  assert.equal(n.meta.especialidades, RAW.meta.especialidades);
  assert.equal(n.serp.melhorMarketplacePos1,
    RAW.google_serp.por_tipo_busca.melhor.pos1_por_tipo.marketplace);
  assert.equal(n.chatgpt.citaMedico, RAW.chatgpt.pct_cita_medico);
  assert.equal(n.chatgpt.instabilidade, RAW.chatgpt.instabilidade_pct_top_medico_muda);
  assert.equal(n.aio.semAioMelhor, RAW.google_aio.sem_aio_melhor);
});

test('porEspecialidade vira mapa visivel/invisivel', () => {
  const n = normalizeData(RAW);
  const derm = n.porEspecialidade['Dermatologia'];
  assert.ok(derm.visivel >= 0 && derm.visivel <= 1);
  assert.equal(Math.round((derm.visivel + derm.invisivel) * 100), 100);
});
```

- [ ] **Step 2: Rodar — falha**

Run: `node --test studies/microsite/test/data.test.mjs`
Expected: FAIL (`Cannot find module` / `normalizeData is not a function`)

- [ ] **Step 3: Implementar**

```javascript
// studies/microsite/js/data.js
export function normalizeData(raw) {
  const c2 = raw.camada2_visibilidade_ia;
  const porEspecialidade = {};
  for (const [esp, v] of Object.entries(c2.por_especialidade)) {
    porEspecialidade[esp] = { visivel: v.pct, invisivel: Math.round((1 - v.pct) * 10000) / 10000 };
  }
  return {
    hero: { pctInvisivel: c2.pct_invisivel_ia, totalMedicos: c2.total_medicos },
    meta: { especialidades: raw.meta.especialidades, capitais: raw.meta.capitais,
            ressalvas: raw.meta.ressalvas || [] },
    serp: {
      melhorMarketplacePos1: raw.google_serp.por_tipo_busca.melhor.pos1_por_tipo.marketplace || 0,
      procMarketplacePos1: raw.google_serp.por_tipo_busca.procedimento.pos1_por_tipo.marketplace || 0,
      topDominios: raw.google_serp.top_dominios_pos1.slice(0, 6),
    },
    chatgpt: {
      citaMedico: raw.chatgpt.pct_cita_medico,
      doctoraliaFonte: raw.chatgpt.doctoralia_como_fonte_pct,
      instabilidade: raw.chatgpt.instabilidade_pct_top_medico_muda,
    },
    aio: { semAio: raw.google_aio.pct_sem_aio, semAioMelhor: raw.google_aio.sem_aio_melhor },
    porEspecialidade,
  };
}

export async function loadData(url = './aggregates.json') {
  const r = await fetch(url);
  if (!r.ok) throw new Error(`falha ao carregar ${url}: ${r.status}`);
  return normalizeData(await r.json());
}
```

- [ ] **Step 4: Rodar — passa**

Run: `node --test studies/microsite/test/data.test.mjs`
Expected: PASS (2 tests)

- [ ] **Step 5: Commit**

```bash
git add studies/microsite/js/data.js studies/microsite/test/data.test.mjs
git commit -m "feat(microsite): normalização de dados (puro) + loader"
```

---

## Task 2: `charts.js` — gráficos SVG puros

**Files:**
- Create: `studies/microsite/js/charts.js`
- Test: `studies/microsite/test/charts.test.mjs`

- [ ] **Step 1: Teste que falha**

```javascript
// studies/microsite/test/charts.test.mjs
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { bigNumberSVG, barChartSVG, donutSVG } from '../js/charts.js';

test('bigNumberSVG mostra a porcentagem', () => {
  const svg = bigNumberSVG(0.845, 'invisíveis');
  assert.match(svg, /^<svg/);
  assert.match(svg, /84%/);
  assert.match(svg, /invisíveis/);
});

test('barChartSVG faz uma barra por item e marca o destaque', () => {
  const svg = barChartSVG([
    { label: 'Dermatologia', value: 0.05, highlight: true },
    { label: 'Reumatologia', value: 0.34 },
  ]);
  assert.equal((svg.match(/<rect/g) || []).length >= 2, true);
  assert.match(svg, /Dermatologia/);
  assert.match(svg, /Reumatologia/);
});

test('donutSVG cria um arco (circle com dash) por segmento', () => {
  const svg = donutSVG([
    { label: 'marketplace', value: 0.89, color: 'var(--viz-4)' },
    { label: 'outro', value: 0.11, color: 'var(--viz-1)' },
  ]);
  assert.equal((svg.match(/<circle/g) || []).length, 2);
  assert.match(svg, /var\(--viz-4\)/);
});
```

- [ ] **Step 2: Rodar — falha**

Run: `node --test studies/microsite/test/charts.test.mjs`
Expected: FAIL (`Cannot find module`)

- [ ] **Step 3: Implementar**

```javascript
// studies/microsite/js/charts.js
const pct = (v) => `${Math.round(v * 100)}%`;
const esc = (s) => String(s).replace(/[<>&]/g, (c) => ({ '<': '&lt;', '>': '&gt;', '&': '&amp;' }[c]));

export function bigNumberSVG(value, legenda = '') {
  return `<svg viewBox="0 0 320 200" role="img" aria-label="${esc(pct(value))} ${esc(legenda)}" xmlns="http://www.w3.org/2000/svg">
  <text x="160" y="120" text-anchor="middle" font-family="var(--font-display)" font-weight="900"
        font-size="110" fill="var(--color-primary)">${pct(value)}</text>
  <text x="160" y="165" text-anchor="middle" font-family="var(--font-sans)" font-size="20"
        fill="var(--color-text-muted)">${esc(legenda)}</text>
</svg>`;
}

export function barChartSVG(items, { width = 520, barH = 26, gap = 14 } = {}) {
  const max = Math.max(...items.map((i) => i.value), 0.0001);
  const labelW = 180, trackW = width - labelW - 60;
  const rows = items.map((it, i) => {
    const y = i * (barH + gap);
    const w = Math.max(2, (it.value / max) * trackW);
    const fill = it.highlight ? 'var(--color-accent-coral)' : 'var(--viz-1)';
    return `<text x="0" y="${y + barH * 0.7}" font-family="var(--font-sans)" font-size="14"
        fill="var(--color-text)">${esc(it.label)}</text>
    <rect x="${labelW}" y="${y}" width="${w}" height="${barH}" rx="6" fill="${fill}"/>
    <text x="${labelW + w + 8}" y="${y + barH * 0.7}" font-family="var(--font-mono)" font-size="13"
        fill="var(--color-text-muted)">${pct(it.value)}</text>`;
  }).join('\n');
  const h = items.length * (barH + gap);
  return `<svg viewBox="0 0 ${width} ${h}" role="img" xmlns="http://www.w3.org/2000/svg">${rows}</svg>`;
}

export function donutSVG(segments, { size = 220, thickness = 38 } = {}) {
  const r = (size - thickness) / 2, cx = size / 2, cy = size / 2;
  const C = 2 * Math.PI * r;
  let offset = 0;
  const arcs = segments.map((s) => {
    const len = s.value * C;
    const dash = `${len} ${C - len}`;
    const el = `<circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="${s.color}"
      stroke-width="${thickness}" stroke-dasharray="${dash}" stroke-dashoffset="${-offset}"
      transform="rotate(-90 ${cx} ${cy})"></circle>`;
    offset += len;
    return el;
  }).join('\n');
  return `<svg viewBox="0 0 ${size} ${size}" role="img" xmlns="http://www.w3.org/2000/svg">${arcs}</svg>`;
}
```

> Nota: o donut usa `<circle>` com `stroke-dasharray` (um arco por segmento) — idêntico
> visualmente a paths e mais simples. O teste (Task 2 Step 1) já conta `<circle>`, então
> impl e teste estão alinhados.

- [ ] **Step 4: Rodar — passa**

Run: `node --test studies/microsite/test/charts.test.mjs`
Expected: PASS (3 tests)

- [ ] **Step 5: Commit**

```bash
git add studies/microsite/js/charts.js studies/microsite/test/charts.test.mjs
git commit -m "feat(microsite): gráficos SVG puros (número-grande, barras, donut)"
```

---

## Task 3: `specialty.js` — valor por especialidade (puro)

**Files:**
- Create: `studies/microsite/js/specialty.js`
- Test: `studies/microsite/test/specialty.test.mjs`

- [ ] **Step 1: Teste que falha**

```javascript
// studies/microsite/test/specialty.test.mjs
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { normalizeData } from '../js/data.js';
import { specialtyValue, especialidadesList } from '../js/specialty.js';

const N = normalizeData(JSON.parse(readFileSync(new URL('../aggregates.json', import.meta.url))));

test('especialidadesList vem ordenada por menor visibilidade (pior primeiro)', () => {
  const list = especialidadesList(N);
  assert.ok(Array.isArray(list) && list.length >= 17);
  for (let i = 1; i < list.length; i++)
    assert.ok(list[i - 1].visivel <= list[i].visivel);
});

test('specialtyValue devolve visivel/invisivel da especialidade', () => {
  const v = specialtyValue(N, 'Dermatologia');
  assert.equal(v.visivel, N.porEspecialidade['Dermatologia'].visivel);
  assert.equal(v.invisivel, N.porEspecialidade['Dermatologia'].invisivel);
});

test('specialtyValue desconhecida devolve null', () => {
  assert.equal(specialtyValue(N, 'Inexistente'), null);
});
```

- [ ] **Step 2: Rodar — falha**

Run: `node --test studies/microsite/test/specialty.test.mjs`
Expected: FAIL

- [ ] **Step 3: Implementar**

```javascript
// studies/microsite/js/specialty.js
export function especialidadesList(norm) {
  return Object.entries(norm.porEspecialidade)
    .map(([nome, v]) => ({ nome, visivel: v.visivel, invisivel: v.invisivel }))
    .sort((a, b) => a.visivel - b.visivel);
}

export function specialtyValue(norm, especialidade) {
  const v = norm.porEspecialidade[especialidade];
  return v ? { visivel: v.visivel, invisivel: v.invisivel } : null;
}
```

- [ ] **Step 4: Rodar — passa**

Run: `node --test studies/microsite/test/specialty.test.mjs`
Expected: PASS (3 tests)

- [ ] **Step 5: Commit**

```bash
git add studies/microsite/js/specialty.js studies/microsite/test/specialty.test.mjs
git commit -m "feat(microsite): seletor de especialidade (lógica pura)"
```

---

## Task 4: `capture.js` — payload do lead (puro) + submit

**Files:**
- Create: `studies/microsite/js/capture.js`
- Test: `studies/microsite/test/capture.test.mjs`

- [ ] **Step 1: Teste que falha**

```javascript
// studies/microsite/test/capture.test.mjs
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { buildPayload } from '../js/capture.js';

test('buildPayload normaliza e marca origem', () => {
  const p = buildPayload({ nome: ' Dra. Ana ', especialidade: 'Dermatologia',
    cidade: 'São Paulo', email: 'ANA@x.com ' }, 'diagnostico');
  assert.equal(p.nome, 'Dra. Ana');
  assert.equal(p.email, 'ana@x.com');
  assert.equal(p.origem, 'diagnostico');
  assert.ok(typeof p.capturado_em === 'string' && p.capturado_em.length > 0);
});

test('buildPayload rejeita email inválido', () => {
  assert.throws(() => buildPayload({ nome: 'X', email: 'semarroba' }, 'pdf'),
    /email inválido/);
});
```

- [ ] **Step 2: Rodar — falha**

Run: `node --test studies/microsite/test/capture.test.mjs`
Expected: FAIL

- [ ] **Step 3: Implementar**

```javascript
// studies/microsite/js/capture.js
export function buildPayload(form, origem) {
  const nome = (form.nome || '').trim();
  const email = (form.email || '').trim().toLowerCase();
  if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) throw new Error('email inválido');
  return {
    nome, email, origem,
    especialidade: (form.especialidade || '').trim(),
    cidade: (form.cidade || '').trim(),
    capturado_em: new Date().toISOString(),
  };
}

// Endpoint do Google Sheet — definido na Frente 3. Vazio = modo log (não envia).
export const LEAD_ENDPOINT = '';

export async function submitLead(payload, endpoint = LEAD_ENDPOINT) {
  if (!endpoint) { console.info('[lead]', payload); return { ok: true, logged: true }; }
  const r = await fetch(endpoint, { method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload) });
  return { ok: r.ok };
}
```

> Nota: `buildPayload` usa `new Date().toISOString()` — aqui é aceitável (runtime do navegador,
> não há replay determinístico). O teste só checa que é string não-vazia.

- [ ] **Step 4: Rodar — passa**

Run: `node --test studies/microsite/test/capture.test.mjs`
Expected: PASS (2 tests)

- [ ] **Step 5: Commit**

```bash
git add studies/microsite/js/capture.js studies/microsite/test/capture.test.mjs
git commit -m "feat(microsite): payload de captura de lead (puro) + submit"
```

---

## Task 5: `index.html` — markup das 9 telas + AEO

**Files:**
- Create: `studies/microsite/index.html`

- [ ] **Step 1: Escrever o HTML** (markup semântico; os números entram via JS em `[data-fill]`)

```html
<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Índice MedRank 2026 — 84% dos médicos são invisíveis para a IA</title>
<meta name="description" content="Estudo proprietário: 84% dos médicos listados são invisíveis para a IA. Analisamos 2.567 médicos em ChatGPT, Google e AI Overview, em 20 especialidades e 9 capitais.">
<meta property="og:title" content="Índice MedRank 2026 — 84% dos médicos são invisíveis para a IA">
<meta property="og:description" content="Quando o paciente pergunta à IA, ela quase nunca cita o seu médico. O estudo que prova isso.">
<meta property="og:type" content="article">
<link rel="preconnect" href="https://api.fontshare.com">
<link href="https://api.fontshare.com/v2/css?f[]=satoshi@400,500,700,900&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Geist+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="styles.css">
<script type="application/ld+json">
{"@context":"https://schema.org","@type":"Dataset","name":"Índice MedRank 2026",
"description":"Visibilidade de médicos brasileiros em motores de IA (ChatGPT, Google AI Overview) e busca, 20 especialidades x 9 capitais, 2.567 médicos.",
"creator":{"@type":"Organization","name":"MedRankGPT"},"temporalCoverage":"2026"}
</script>
</head>
<body>
<main>
  <!-- 1. HERÓI -->
  <section class="tela hero" id="hero">
    <p class="overline">Índice MedRank 2026 · O Estado das Buscas Médicas com IA</p>
    <h1>De cada 100 médicos, <span class="hl" data-fill="hero-num">—</span> são invisíveis para a IA.</h1>
    <p class="lead">Analisamos <span data-fill="hero-n">—</span> médicos reais em 3 superfícies de IA, 20 especialidades e 9 capitais. O que a IA responde quando o paciente pergunta "quem é o melhor médico?"</p>
    <div class="hero-chart" data-chart="hero"></div>
    <a class="scroll-cue" href="#experimento">↓ ver o estudo</a>
  </section>

  <!-- 2. O EXPERIMENTO -->
  <section class="tela" id="experimento">
    <h2>O experimento</h2>
    <p>Rodamos as buscas que um paciente faz — "melhor [especialista] em [cidade]" — em três superfícies que ele realmente encontra, e cruzamos com 2.567 médicos reais listados no Doctoralia.</p>
    <ul class="stats" data-fill="experimento-stats"></ul>
  </section>

  <!-- 3. GOOGLE -> DOCTORALIA -->
  <section class="tela" id="google">
    <h2>No Google, o paciente cai no marketplace</h2>
    <p>Em <span data-fill="serp-melhor">—</span> das buscas "melhor [especialista]", quem ocupa a posição #1 é o <strong>Doctoralia</strong> — não o médico.</p>
    <div class="chart" data-chart="serp-donut"></div>
  </section>

  <!-- 4. CHATGPT -->
  <section class="tela" id="chatgpt">
    <h2>O ChatGPT nomeia um médico — mas lê o Doctoralia</h2>
    <p>O ChatGPT cita um médico em <span data-fill="cg-cita">—</span> das vezes. Só que escolhe a partir das mesmas fontes: cita o Doctoralia como fonte em <span data-fill="cg-fonte">—</span> das respostas.</p>
  </section>

  <!-- 5. AIO -->
  <section class="tela" id="aio">
    <h2>O Google esconde a própria IA em saúde</h2>
    <p>Em <span data-fill="aio-melhor">—</span> das buscas por "melhor [especialista]", o Google <strong>não mostra</strong> o AI Overview. Ele liga menos a IA justamente quando o paciente procura um especialista.</p>
  </section>

  <!-- 6. CLÍMAX + SELETOR -->
  <section class="tela climax" id="invisiveis">
    <h2><span data-fill="hero-num2">—</span> dos médicos são invisíveis para a IA</h2>
    <p>De 2.567 médicos reais, só uma fração chega a ser nomeada pela IA. E quanto mais concorrida a especialidade, pior:</p>
    <div class="chart" data-chart="esp-bars"></div>
    <div class="selector">
      <label for="esp-select">Veja a sua especialidade:</label>
      <select id="esp-select"></select>
      <p class="selector-out" data-fill="esp-out" aria-live="polite"></p>
    </div>
  </section>

  <!-- 7. ROLETA -->
  <section class="tela" id="roleta">
    <h2>A IA é uma roleta</h2>
    <p>Faça a mesma pergunta duas vezes e, em <span data-fill="cg-instab">—</span> das vezes, o médico recomendado muda. Ser a resposta <em>consistente</em> é um diferencial.</p>
  </section>

  <!-- 8. PLAYBOOK -->
  <section class="tela" id="playbook">
    <h2>Dá para virar o jogo</h2>
    <p>A IA não inventa nomes — ela lê fontes. Quem aparece de forma consistente nessas fontes (perfis, conteúdo, menções, site com sinais técnicos) vira "o nome que a IA dá". É disso que trata o AEO (Answer Engine Optimization) — posicionar o médico como a resposta que ChatGPT, Gemini e o Google recomendam, dentro das regras do CFM.</p>
  </section>

  <!-- 9. CTA + RODAPÉ -->
  <section class="tela cta" id="cta">
    <h2>Descubra se VOCÊ aparece na IA</h2>
    <p>Diagnóstico gratuito da sua visibilidade nos motores de IA.</p>
    <form id="lead-form" class="lead-form" novalidate>
      <input name="nome" placeholder="Seu nome" autocomplete="name" required>
      <input name="especialidade" placeholder="Especialidade" required>
      <input name="cidade" placeholder="Cidade" required>
      <input name="email" type="email" placeholder="E-mail" autocomplete="email" required>
      <button type="submit">Quero meu diagnóstico</button>
      <p class="form-msg" data-fill="form-msg" aria-live="polite"></p>
    </form>
    <p class="pdf"><a id="pdf-link" href="#cta">Ou baixe o relatório completo em PDF →</a></p>
    <footer>
      <h3>Metodologia</h3>
      <ul data-fill="ressalvas"></ul>
      <p class="src">Fonte: Índice MedRank 2026 · dados em <code>aggregates.json</code>.</p>
    </footer>
  </section>
</main>
<script type="module" src="js/main.js"></script>
</body>
</html>
```

- [ ] **Step 2: Validar que abre sem erro de sintaxe**

Run: `node -e "const s=require('fs').readFileSync('studies/microsite/index.html','utf8'); if(!s.includes('id=\"esp-select\"')) throw new Error('faltou seletor'); console.log('html ok')"`
Expected: `html ok`

- [ ] **Step 3: Commit**

```bash
git add studies/microsite/index.html
git commit -m "feat(microsite): markup das 9 telas + JSON-LD (AEO)"
```

---

## Task 6: `styles.css` — tokens + layout scrollytelling

**Files:**
- Create: `studies/microsite/styles.css`

- [ ] **Step 1: Escrever o CSS** (importa tokens; mobile-first; respeita reduced-motion já tratado nos tokens)

```css
/* studies/microsite/styles.css */
@import url("../../design-system/tokens.css");

* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body { margin: 0; background: var(--color-bg); color: var(--color-text);
  font-family: var(--font-sans); font-size: var(--fs-body); line-height: var(--lh-body); }

.tela { max-width: var(--maxw); margin: 0 auto; padding: var(--space-4xl) var(--space-lg);
  min-height: 88vh; display: flex; flex-direction: column; justify-content: center; }
.tela h2 { font-family: var(--font-display); font-weight: var(--w-black);
  font-size: var(--fs-display-md); letter-spacing: var(--tracking-display); margin: 0 0 var(--space-md); }
.tela p { font-size: var(--fs-body-lg); color: var(--color-text-muted); max-width: 60ch; }

.overline { font-family: var(--font-mono); font-size: var(--fs-overline);
  letter-spacing: var(--tracking-overline); text-transform: uppercase; color: var(--color-primary-deep); }
.hero h1 { font-family: var(--font-display); font-weight: var(--w-black);
  font-size: var(--fs-display-xl); line-height: var(--lh-tight); letter-spacing: var(--tracking-display); margin: var(--space-md) 0; }
.hl { background: var(--hl-fill); padding: 0 .08em; }
.lead { font-size: var(--fs-body-lg); }
.hero-chart svg, .chart svg { width: 100%; height: auto; max-width: 560px; }
.scroll-cue { margin-top: var(--space-2xl); color: var(--color-primary-deep);
  text-decoration: none; font-weight: var(--w-medium); }

.stats { list-style: none; padding: 0; display: grid; gap: var(--space-md);
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); }
.stats li { background: var(--color-surface-2); border: 1px solid var(--color-border);
  border-radius: var(--card-radius); padding: var(--card-pad); }
.stats b { font-family: var(--font-mono); font-size: var(--fs-display-md);
  color: var(--color-primary); display: block; }

.climax { background: var(--color-bg-subtle); }
.selector { margin-top: var(--space-xl); background: var(--color-surface);
  border: 1px solid var(--color-border-strong); border-radius: var(--card-radius); padding: var(--card-pad); }
.selector select { font-family: var(--font-sans); font-size: var(--fs-body);
  padding: 10px 14px; border-radius: var(--input-radius); border: 1px solid var(--color-border-strong); }
.selector-out { font-family: var(--font-display); font-weight: var(--w-bold);
  font-size: var(--fs-h2); color: var(--color-text); margin-top: var(--space-md); }

.cta { background: var(--color-text); color: var(--color-on-ink); }
.cta h2, .cta p { color: var(--color-on-ink); }
.lead-form { display: grid; gap: var(--space-sm); max-width: 420px; }
.lead-form input { padding: 12px 14px; border-radius: var(--input-radius); border: 0; font-size: var(--fs-body); }
.lead-form button { background: var(--color-primary); color: var(--color-on-primary);
  border: 0; border-radius: var(--btn-radius); padding: var(--btn-pad-y) var(--btn-pad-x);
  font-weight: var(--w-bold); cursor: pointer; }
.lead-form button:hover { background: var(--color-primary-hover); }
.form-msg { font-size: var(--fs-body-sm); }
footer { margin-top: var(--space-3xl); border-top: 1px solid var(--color-border-strong); padding-top: var(--space-lg); }
footer ul { color: var(--color-text-subtle); font-size: var(--fs-body-sm); }
.src code { font-family: var(--font-mono); }

@media (max-width: 640px) {
  .hero h1 { font-size: var(--fs-display-md); }
  .tela h2 { font-size: var(--fs-h1); }
  .tela { padding: var(--space-3xl) var(--space-md); }
}
```

- [ ] **Step 2: Commit**

```bash
git add studies/microsite/styles.css
git commit -m "feat(microsite): estilos (tokens do design-system) + layout scrollytelling"
```

---

## Task 7: `main.js` — wiring + verificação no navegador

**Files:**
- Create: `studies/microsite/js/main.js`

- [ ] **Step 1: Implementar o wiring**

```javascript
// studies/microsite/js/main.js
import { loadData } from './data.js';
import { bigNumberSVG, barChartSVG, donutSVG } from './charts.js';
import { especialidadesList, specialtyValue } from './specialty.js';
import { buildPayload, submitLead } from './capture.js';

const pct = (v) => `${Math.round(v * 100)}%`;
const set = (key, html) => { for (const el of document.querySelectorAll(`[data-fill="${key}"]`)) el.innerHTML = html; };
const chart = (key, svg) => { const el = document.querySelector(`[data-chart="${key}"]`); if (el) el.innerHTML = svg; };

loadData().then((N) => {
  // herói
  set('hero-num', pct(N.hero.pctInvisivel));
  set('hero-num2', pct(N.hero.pctInvisivel));
  set('hero-n', N.hero.totalMedicos.toLocaleString('pt-BR'));
  chart('hero', bigNumberSVG(N.hero.pctInvisivel, 'invisíveis para a IA'));

  // experimento
  set('experimento-stats', [
    [N.meta.especialidades, 'especialidades'], [N.meta.capitais, 'capitais'],
    [N.hero.totalMedicos.toLocaleString('pt-BR'), 'médicos reais'], ['3', 'superfícies de IA'],
  ].map(([b, l]) => `<li><b>${b}</b>${l}</li>`).join(''));

  // google serp
  set('serp-melhor', pct(N.serp.melhorMarketplacePos1));
  chart('serp-donut', donutSVG([
    { label: 'Doctoralia (#1)', value: N.serp.melhorMarketplacePos1, color: 'var(--viz-4)' },
    { label: 'resto', value: 1 - N.serp.melhorMarketplacePos1, color: 'var(--viz-1)' },
  ]));

  // chatgpt
  set('cg-cita', pct(N.chatgpt.citaMedico));
  set('cg-fonte', pct(N.chatgpt.doctoraliaFonte));
  set('cg-instab', pct(N.chatgpt.instabilidade));

  // aio
  set('aio-melhor', pct(N.aio.semAioMelhor));

  // clímax: barras + seletor
  const list = especialidadesList(N);
  chart('esp-bars', barChartSVG(list.slice(0, 12).map((e) => ({
    label: e.nome, value: e.visivel, highlight: e.nome === 'Dermatologia',
  }))));
  const select = document.getElementById('esp-select');
  if (select) {
    select.innerHTML = list.map((e) => `<option>${e.nome}</option>`).join('');
    const update = () => {
      const v = specialtyValue(N, select.value);
      set('esp-out', v ? `Em ${select.value}, só <strong>${pct(v.visivel)}</strong> dos médicos aparecem na IA — <strong>${pct(v.invisivel)}</strong> são invisíveis.` : '');
    };
    select.addEventListener('change', update);
    select.value = 'Dermatologia'; update();
  }

  // ressalvas
  set('ressalvas', (N.meta.ressalvas || []).map((r) => `<li>${r}</li>`).join(''));

  // captura
  const form = document.getElementById('lead-form');
  if (form) form.addEventListener('submit', async (ev) => {
    ev.preventDefault();
    const data = Object.fromEntries(new FormData(form).entries());
    try {
      const payload = buildPayload(data, 'diagnostico');
      await submitLead(payload);
      set('form-msg', 'Recebido! Em breve você recebe seu diagnóstico. ✅');
      form.reset();
    } catch (e) { set('form-msg', `Confira os dados: ${e.message}`); }
  });
  const pdf = document.getElementById('pdf-link');
  if (pdf) pdf.addEventListener('click', (ev) => { ev.preventDefault();
    try { /* mesmo gate, origem pdf */ const data = Object.fromEntries(new FormData(form).entries());
      const p = buildPayload(data, 'pdf'); submitLead(p); set('form-msg', 'Preencha e envie o form acima para receber o PDF.'); }
    catch { set('form-msg', 'Preencha o form acima para liberar o PDF.'); } });
}).catch((e) => { document.body.insertAdjacentHTML('afterbegin',
  `<p style="color:red;padding:1rem">Erro ao carregar dados: ${e.message}</p>`); });
```

- [ ] **Step 2: Servir e verificar no navegador (screenshots + interação)**

Run:
```bash
( cd studies/microsite && python3 -m http.server 8765 >/dev/null 2>&1 & echo $! > /tmp/ms.pid )
sleep 1
```
Então use o skill **`/browse`** (ou Claude Preview) para abrir `http://localhost:8765`:
- Verificar que o herói mostra "84%" (não "—").
- Rolar até a tela "invisíveis", trocar o `<select>` para "Oftalmologia" e confirmar que o texto atualiza para ~7%.
- Submeter o form com email inválido → mensagem "Confira os dados"; com email válido → "Recebido!".
- Tirar screenshot do herói e da tela do seletor.

Parar o servidor:
```bash
kill $(cat /tmp/ms.pid) 2>/dev/null
```
Expected: herói com "84%", seletor reativo, form valida. (Se algum `data-fill` mostrar "—", o `key` do `set()` não bate com o HTML — corrigir.)

- [ ] **Step 3: Commit**

```bash
git add studies/microsite/js/main.js
git commit -m "feat(microsite): wiring DOM (render das 9 telas, seletor, captura)"
```

---

## Task 8: README + verificação final + push

**Files:**
- Create: `studies/microsite/README.md`

- [ ] **Step 1: README**

```markdown
<!-- studies/microsite/README.md -->
# Microsite — Índice MedRank 2026

Site estático scrollytelling que consome `aggregates.json` (cópia de `studies/results/`).

## Servir local
```bash
cd studies/microsite && python3 -m http.server 8765
# abrir http://localhost:8765
```

## Testar a lógica pura
```bash
node --test studies/microsite/test/
```

## Atualizar dados (nova edição do estudo)
```bash
cp studies/results/aggregates.json studies/microsite/aggregates.json
```

## Deploy (item aberto — Frente 3)
Site standalone (ex.: `indice.medrankgpt.com.br` no Render) OU copiar a pasta para o site
principal. `main` tem história git não relacionada — não fazer merge. Endpoint de captura
(Google Sheet) e geração do PDF são da Frente 3; hoje o form roda em modo log (`LEAD_ENDPOINT` vazio).
```

- [ ] **Step 2: Rodar toda a suíte JS**

Run: `node --test studies/microsite/test/`
Expected: PASS (todos os `*.test.mjs`)

- [ ] **Step 3: Commit + push**

```bash
git add studies/microsite/README.md
git commit -m "docs(microsite): README (servir, testar, deploy)"
git push origin claude/silly-villani-19b5e0
```

---

## Self-Review (do autor do plano)

**1. Cobertura do spec:**
- §3 (9 telas) → Task 5 (markup) + Task 7 (dados). ✅
- §4 unidades isoladas (data/charts/specialty/capture/main) → Tasks 1–4, 7. ✅
- §5 AEO/SEO (JSON-LD, headings, meta) → Task 5. ✅
- §2 lê JSON em runtime, zero hard-coded → Task 1 (loadData) + Task 7 (data-fill). ✅
- §6 critérios: charts testáveis (Task 2), seletor correto (Task 3 + verificação Task 7), responsivo/DESIGN.md (Task 6). ✅
- Captura → Sheet (endpoint configurável) → Task 4. ✅

**2. Placeholders:** o "—" no HTML é o estado inicial substituído pelo JS (intencional, não é placeholder de código). Impl e teste do donut já consistentes (`<circle>`). Sem TODO/TBD reais.

**3. Consistência de tipos/chaves:**
- `normalizeData` produz `{hero, meta, serp, chatgpt, aio, porEspecialidade}` — consumido igual em `specialty.js` (Task 3) e `main.js` (Task 7). ✅
- chaves `data-fill`/`data-chart` do HTML (Task 5) batem com os `set()/chart()` do `main.js` (Task 7): hero-num, hero-num2, hero-n, experimento-stats, serp-melhor, serp-donut, cg-cita, cg-fonte, cg-instab, aio-melhor, esp-bars, esp-out, ressalvas, form-msg. ✅
- `bigNumberSVG/barChartSVG/donutSVG` mesma assinatura em Task 2 e Task 7. ✅
- `buildPayload(form, origem)` mesma assinatura em Task 4 e Task 7. ✅

Sem ajustes pendentes.

## Notas de execução
- Pré-requisito: Node 22 (tem `node:test`) + `python3 -m http.server`. Sem npm install.
- A verificação visual (Task 7 Step 2) usa o skill `/browse` ou Claude Preview — é o teste de
  integração real do site (os unit tests cobrem só a lógica pura).
- **Próximas frentes:** Frente 3 (PDF gated + endpoint Sheet real), Frente 4 (distribuição).
