# Captura (Slack) + PDF gated (Frente 3) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ligar o form do microsite ao bridge de leads da mainpage (→ Slack #medrankgpt) e liberar o relatório em PDF (impresso do próprio microsite) após o cadastro.

**Architecture:** Front estático só. `capture.js` ganha `buildBridgePayload` (puro) que mapeia o form pro shape `{nome,email,telefone,perfil,especialidade}` do bridge existente, e `submitLead` faz o POST. O `index.html` ganha campo telefone e esconde o link do PDF até o submit. O PDF é um artefato estático gerado uma vez via headless (`browse pdf`) com um `@media print`. Nenhum segredo no front.

**Tech Stack:** HTML/CSS/JS ES modules vanilla, `node:test` (Node 22), `browse pdf` (gstack headless) + `python3 -m http.server` para gerar/verificar.

**Contexto reusado:** o bridge da mainpage — `POST https://mainline-finance.onrender.com/api/medrank-lead` com `{nome,email,telefone,perfil,especialidade}` → Slack. CORS restrito a `medrankgpt.com.br` (entrega real só pós-deploy; ver spec §7). Não recriar webhook, não pôr segredo no front.

---

## File Structure

**Modificar:**
- `studies/microsite/js/capture.js` — troca `buildPayload` por `buildBridgePayload` (shape do bridge) + `LEAD_ENDPOINT` real + `submitLead` resiliente.
- `studies/microsite/test/capture.test.mjs` — testes do `buildBridgePayload` + `LEAD_ENDPOINT`.
- `studies/microsite/index.html` — campo `telefone` no form; `#pdf-link` começa escondido.
- `studies/microsite/js/main.js` — usa `buildBridgePayload`, trata `{ok}`, revela o PDF no sucesso.
- `studies/microsite/styles.css` — bloco `@media print` + `[hidden]{display:none}`.

**Criar:**
- `studies/microsite/indice-medrank-2026.pdf` — artefato gerado (não código).

---

## Task 1: `capture.js` — payload do bridge + endpoint

**Files:**
- Modify: `studies/microsite/js/capture.js`
- Modify: `studies/microsite/test/capture.test.mjs`

- [ ] **Step 1: Reescrever o teste (substitui o conteúdo INTEIRO de `capture.test.mjs`)**

```javascript
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { buildBridgePayload, LEAD_ENDPOINT } from '../js/capture.js';

test('buildBridgePayload mapeia pro shape do bridge', () => {
  const p = buildBridgePayload({ nome: ' Dra. Ana ', especialidade: 'Dermatologia',
    cidade: 'São Paulo', telefone: ' 11 99999 ', email: 'ANA@x.com ' });
  assert.equal(p.nome, 'Dra. Ana');
  assert.equal(p.email, 'ana@x.com');
  assert.equal(p.telefone, '11 99999');
  assert.equal(p.perfil, 'Índice MedRank 2026');
  assert.equal(p.especialidade, 'Dermatologia — São Paulo');
  assert.deepEqual(Object.keys(p).sort(),
    ['email', 'especialidade', 'nome', 'perfil', 'telefone']);
});

test('sem cidade não adiciona separador; telefone vazio vira ""', () => {
  const p = buildBridgePayload({ nome: 'X', especialidade: 'Cardiologia', email: 'x@y.com' });
  assert.equal(p.especialidade, 'Cardiologia');
  assert.equal(p.telefone, '');
});

test('rejeita email inválido', () => {
  assert.throws(() => buildBridgePayload({ nome: 'X', email: 'semarroba' }), /email inválido/);
});

test('LEAD_ENDPOINT aponta pro bridge da mainpage', () => {
  assert.match(LEAD_ENDPOINT, /mainline-finance\.onrender\.com\/api\/medrank-lead/);
});
```

- [ ] **Step 2: Rodar — falha**

Run: `node --test studies/microsite/test/capture.test.mjs`
Expected: FAIL (`buildBridgePayload` não existe / `LEAD_ENDPOINT` vazio)

- [ ] **Step 3: Reescrever `capture.js` (conteúdo INTEIRO)**

```javascript
export function buildBridgePayload(form) {
  const nome = (form.nome || '').trim();
  const email = (form.email || '').trim().toLowerCase();
  if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) throw new Error('email inválido');
  const especialidade = (form.especialidade || '').trim();
  const cidade = (form.cidade || '').trim();
  return {
    nome,
    email,
    telefone: (form.telefone || '').trim(),
    perfil: 'Índice MedRank 2026',
    especialidade: cidade ? `${especialidade} — ${cidade}` : especialidade,
  };
}

// Bridge de leads da mainpage (posta no Slack #medrankgpt). Segredo fica no bridge.
export const LEAD_ENDPOINT = 'https://mainline-finance.onrender.com/api/medrank-lead';

export async function submitLead(payload, endpoint = LEAD_ENDPOINT) {
  try {
    const r = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
      body: JSON.stringify(payload),
    });
    return { ok: r.ok };
  } catch {
    return { ok: false };
  }
}
```

- [ ] **Step 4: Rodar — passa**

Run: `node --test studies/microsite/test/capture.test.mjs`
Expected: PASS (4 tests)

- [ ] **Step 5: Commit**

```bash
git add studies/microsite/js/capture.js studies/microsite/test/capture.test.mjs
git commit -m "feat(microsite): captura mapeia pro bridge da mainpage (Slack)"
```

---

## Task 2: `index.html` — campo telefone + PDF escondido

**Files:**
- Modify: `studies/microsite/index.html`

- [ ] **Step 1: Adicionar o campo telefone no form**

Substituir a linha do input de email:
```html
      <input name="email" type="email" placeholder="E-mail" autocomplete="email" required>
```
por (telefone ANTES do email):
```html
      <input name="telefone" placeholder="WhatsApp (opcional)" autocomplete="tel" inputmode="tel">
      <input name="email" type="email" placeholder="E-mail" autocomplete="email" required>
```

- [ ] **Step 2: Esconder o link do PDF até o cadastro**

Substituir:
```html
    <p class="pdf"><a id="pdf-link" href="#cta">Ou baixe o relatório completo em PDF →</a></p>
```
por:
```html
    <p class="pdf" id="pdf-wrap" hidden><a id="pdf-link" href="./indice-medrank-2026.pdf" download>Baixe o relatório completo em PDF →</a></p>
```

- [ ] **Step 3: Verificar**

Run: `node -e "const s=require('fs').readFileSync('studies/microsite/index.html','utf8'); if(!s.includes('name=\"telefone\"')||!s.includes('id=\"pdf-wrap\" hidden')) throw new Error('faltou telefone/pdf-wrap'); console.log('html ok')"`
Expected: `html ok`

- [ ] **Step 4: Commit**

```bash
git add studies/microsite/index.html
git commit -m "feat(microsite): campo telefone no form + link do PDF escondido (gate)"
```

---

## Task 3: `main.js` — usar o payload do bridge + revelar o PDF

**Files:**
- Modify: `studies/microsite/js/main.js`

- [ ] **Step 1: Trocar o import**

Substituir:
```javascript
import { buildPayload, submitLead } from './capture.js';
```
por:
```javascript
import { buildBridgePayload, submitLead } from './capture.js';
```

- [ ] **Step 2: Reescrever o bloco de captura** (o trecho `// captura` até o final do `.then`, ANTES do `.catch`)

Substituir todo o bloco que começa em `// captura` e vai até o handler do `pdf-link` (inclusive) por:
```javascript
  // captura -> bridge da mainpage (Slack)
  const form = document.getElementById('lead-form');
  const pdfWrap = document.getElementById('pdf-wrap');
  if (form) form.addEventListener('submit', async (ev) => {
    ev.preventDefault();
    const data = Object.fromEntries(new FormData(form).entries());
    let payload;
    try {
      payload = buildBridgePayload(data);
    } catch (e) {
      set('form-msg', `Confira os dados: ${e.message}`);
      return;
    }
    set('form-msg', 'Enviando…');
    const res = await submitLead(payload);
    if (res.ok) {
      set('form-msg', 'Recebido! Seu diagnóstico chega em breve. ✅ Relatório liberado abaixo.');
      if (pdfWrap) pdfWrap.hidden = false;
      form.reset();
    } else {
      set('form-msg', 'Não consegui enviar agora — tente de novo em instantes.');
    }
  });
```

> Nota: o `#pdf-link` agora é um link de download normal (revelado no sucesso); não tem mais
> handler de clique. O `.catch(...)` no final do `loadData().then(...)` permanece intacto.

- [ ] **Step 3: Verificar sintaxe + suíte JS**

Run: `node --check studies/microsite/js/main.js && node --test studies/microsite/test/`
Expected: sem erro de sintaxe; todos os `*.test.mjs` passam.

- [ ] **Step 4: Commit**

```bash
git add studies/microsite/js/main.js
git commit -m "feat(microsite): submit posta no bridge e revela o PDF no sucesso"
```

---

## Task 4: `styles.css` — print CSS + [hidden]

**Files:**
- Modify: `studies/microsite/styles.css`

- [ ] **Step 1: Adicionar ao FINAL de `styles.css`**

```css
/* garante que o atributo hidden esconda mesmo com display custom */
[hidden] { display: none !important; }

/* PDF: a página vira um relatório limpo de papel */
@media print {
  body { background: #fff; color: #000; }
  .tela { min-height: auto; page-break-inside: avoid; padding: 24px 0; }
  .cta { background: #fff; color: #000; }
  .cta h2, .cta p { color: #000; }
  .scroll-cue, .lead-form, .pdf, .selector select { display: none !important; }
  .hero h1 { font-size: 32pt; }
  .tela h2 { font-size: 20pt; }
  .chart svg, .hero-chart svg { max-width: 360px; }
  a { color: #000; text-decoration: none; }
}
```

- [ ] **Step 2: Commit**

```bash
git add studies/microsite/styles.css
git commit -m "feat(microsite): print CSS p/ o PDF + [hidden] robusto"
```

---

## Task 5: Gerar o PDF + verificação final

**Files:**
- Create: `studies/microsite/indice-medrank-2026.pdf`

- [ ] **Step 1: Servir o microsite**

```bash
cd studies/microsite && nohup python3 -m http.server 8765 >/dev/null 2>&1 & echo $! > /tmp/ms.pid
cd - >/dev/null; sleep 1
curl -s -o /dev/null -w "up:%{http_code}\n" http://localhost:8765/
```
Expected: `up:200`

- [ ] **Step 2: Gerar o PDF via headless**

Resolver o binário do browse e imprimir a página em PDF:
```bash
B="$HOME/.claude/skills/gstack/browse/dist/browse"
$B goto http://localhost:8765 >/dev/null 2>&1
$B wait --networkidle >/dev/null 2>&1
$B pdf studies/microsite/indice-medrank-2026.pdf --format a4 --print-background
ls -la studies/microsite/indice-medrank-2026.pdf
```
Expected: o arquivo existe e tem tamanho > 0.

- [ ] **Step 3: Verificação visual rápida**

Abrir o PDF (`open studies/microsite/indice-medrank-2026.pdf`) ou screenshot da primeira
página, e confirmar: herói "84%", seções legíveis, sem o CTA escuro/forms. Se o layout
quebrar, ajustar o `@media print` (Task 4) e regerar.

- [ ] **Step 4: Parar o servidor + suíte completa**

```bash
kill $(cat /tmp/ms.pid) 2>/dev/null
node --test studies/microsite/test/
```
Expected: todos os testes JS passam.

- [ ] **Step 5: Commit + push**

```bash
git add studies/microsite/indice-medrank-2026.pdf
git commit -m "feat(microsite): relatório em PDF gerado (gated após cadastro)"
git push origin claude/silly-villani-19b5e0
```

---

## Self-Review (do autor do plano)

**1. Cobertura do spec:**
- §3 Captura → Slack (payload do bridge, telefone, perfil, especialidade+cidade) → Tasks 1–3. ✅
- §4 PDF gated (print CSS, geração, link escondido até submit) → Tasks 2 (hidden), 4 (print), 5 (gerar). ✅
- §6 critérios: `buildBridgePayload` testado (Task 1), revela PDF no sucesso (Task 3), print PDF (Task 5), sem segredo no front (endpoint público do bridge). ✅
- §7 CORS/deploy: declarado; entrega real pós-deploy (não testável em localhost). ✅

**2. Placeholders:** nenhum TODO/TBD; todo passo de código traz o código completo.

**3. Consistência:**
- `buildBridgePayload(form)` (Task 1) usado igual em `main.js` (Task 3). ✅
- `#pdf-wrap`/`#pdf-link` do HTML (Task 2) referenciados no `main.js` (Task 3) e no print CSS (Task 4). ✅
- `LEAD_ENDPOINT` (Task 1) é o default de `submitLead` — `main.js` chama `submitLead(payload)` sem endpoint. ✅
- `indice-medrank-2026.pdf`: href no HTML (Task 2) = arquivo gerado (Task 5). ✅

Sem ajustes pendentes.

## Notas de execução
- Node 22 + `browse` (gstack) + `python3 -m http.server`. Sem npm.
- A entrega real do lead ao Slack só ocorre quando o microsite estiver num origin permitido
  pelo CORS do bridge (`medrankgpt.com.br`) — ver spec §7. Localhost cai no ramo `{ok:false}`.
- **Próxima frente:** Frente 4 (distribuição: PR/imprensa, AEO, e-mail) + deploy.
