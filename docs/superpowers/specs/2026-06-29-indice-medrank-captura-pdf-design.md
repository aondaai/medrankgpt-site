# Índice MedRank 2026 — Captura (Slack) + PDF gated (Frente 3) — Design

> Torna a captura de lead do microsite real (form → Slack #medrankgpt, reusando o bridge da
> mainpage) e adiciona o PDF gated (impressão do próprio microsite). Data: 2026-06-29.

## 1. Objetivo

Fechar o ciclo de captação do microsite: o lead preenchido vira aviso no Slack (mesmo canal
e bridge do form da mainpage), e quem se cadastra libera o **relatório completo em PDF**.

**Decisões do brainstorming:**

| Decisão | Escolha |
|--------|---------|
| Destino do lead | Slack #medrankgpt via o **bridge existente** da mainpage |
| Endpoint | `https://mainline-finance.onrender.com/api/medrank-lead` |
| PDF | Impressão do próprio microsite (headless), gated após o submit |

## 2. Contexto reusado (não recriar)

A mainpage (`origin/main:index.html`) já posta leads assim:
- `POST` JSON pra `https://mainline-finance.onrender.com/api/medrank-lead`.
- Payload: `{nome, email, telefone, perfil, especialidade}`.
- O bridge (`app/api/medrank-lead/route.ts` no repo `mainline.finance`) valida CORS
  (`medrankgpt.com.br`), formata Block Kit e posta no Slack via `SLACK_WEBHOOK_URL` (segredo,
  nunca no front). Ver [[medrankgpt-slack-leads]].

O microsite **reusa esse endpoint**; nada de webhook novo, nada de segredo no front.

## 3. Captura → Slack

**Form do microsite** (`index.html`, seção CTA): campos `nome`, `especialidade`, `cidade`,
**`telefone` (novo, opcional)**, `email`.

**`capture.js`:**
- `LEAD_ENDPOINT = "https://mainline-finance.onrender.com/api/medrank-lead"`.
- `buildBridgePayload(form)` (pura) mapeia pro shape do bridge:
  - `nome` ← nome
  - `email` ← email (lowercase, validado)
  - `telefone` ← telefone (ou `""`)
  - `perfil` ← `"Índice MedRank 2026"` (marca a origem no Slack)
  - `especialidade` ← `"{especialidade} — {cidade}"` (carrega a cidade pro Slack)
  - lança `Error("email inválido")` se o email não casar o regex.
- `submitLead(payload, endpoint)` faz o `POST` JSON (`Content-Type` + `Accept` application/json),
  igual à mainpage. Retorna `{ok}`.
- No `submit` do form (`main.js`): `buildBridgePayload` → `submitLead` → em sucesso mostra
  "Recebido ✅" e **revela o link do PDF**; em erro de validação mostra "Confira os dados".

## 4. PDF gated

- **Print CSS** em `styles.css` (`@media print`): fundo branco, sem CTA dark, cada `.tela`
  com `break-inside: avoid`, gráficos SVG visíveis — a página vira um PDF limpo multi-página.
- **Geração** (passo de build, não runtime): `browse pdf` sobre o microsite servido localmente
  → `studies/microsite/indice-medrank-2026.pdf` (artefato versionado).
- **Gate**: o link `#pdf-link` começa com `hidden`; o handler de sucesso do form remove o
  `hidden` e seta `href` pro PDF. Sem cadastro, sem link.

## 5. Componentes (unidades isoladas)

- `capture.js` — `buildBridgePayload` (pura, testável com `node:test`) + `submitLead` (fetch).
- `index.html` — campo telefone no form; `#pdf-link` inicia `hidden`.
- `styles.css` — bloco `@media print`.
- `indice-medrank-2026.pdf` — artefato gerado (não código).

## 6. Critérios de sucesso (verificáveis)

- `buildBridgePayload` produz exatamente `{nome,email,telefone,perfil,especialidade}` com a
  cidade dobrada na especialidade e perfil "Índice MedRank 2026" (teste node).
- Email inválido lança erro; o handler mostra "Confira os dados".
- Após submit válido (mock de fetch), o `#pdf-link` perde `hidden` e ganha `href`.
- `@media print` produz um PDF legível (verificação visual com `browse pdf`).
- Nenhum segredo no front; o endpoint é o bridge existente.

## 7. Itens abertos (não bloqueiam o build)

1. **CORS / deploy:** o bridge libera CORS só pra `medrankgpt.com.br`. A entrega real do POST
   só passa quando o microsite for servido de um origin permitido → recomendado **deploy sob
   `medrankgpt.com.br/indice/`** (CORS já passa). Subdomínio (`indice.medrankgpt.com.br`)
   exigiria adicionar o origin no bridge (repo `mainline.finance`). Localhost não passa no CORS;
   o teste de payload é em node, a entrega é validada pós-deploy.
2. **Telefone obrigatório vs opcional:** começa opcional (menos atrito); reavaliar pela
   qualidade do lead.

## 8. Fora de escopo

- Mudanças no bridge (`mainline.finance`) — só se optarmos por subdomínio.
- PDF desenhado dedicado (v2).
- Distribuição/e-mail → Frente 4.

Deriva do spec guarda-chuva `2026-06-28-indice-medrank-2026-design.md` (Frente 3).
