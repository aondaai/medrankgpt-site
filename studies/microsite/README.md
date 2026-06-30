# Microsite — Índice MedRank 2026

Site estático scrollytelling (9 telas) que consome `aggregates.json` — **autossuficiente**
(HTML/CSS/JS vanilla, `tokens.css` e `aggregates.json` copiados pra dentro). Zero número
hard-coded: tudo vem do JSON.

## Servir local
```bash
cd studies/microsite && python3 -m http.server 8765
# abrir http://localhost:8765
```

## Testar a lógica pura
```bash
node --test studies/microsite/test/
```
Cobre normalização de dados, gráficos SVG, seletor de especialidade e payload de captura.

## Atualizar (nova edição do estudo / mudou o design-system)
```bash
cp studies/results/aggregates.json studies/microsite/aggregates.json
cp design-system/tokens.css        studies/microsite/tokens.css
```

## Estrutura
- `index.html` — markup das 9 telas + JSON-LD (AEO).
- `styles.css` — importa `./tokens.css`; layout scrollytelling.
- `js/data.js` — `normalizeData` (puro) + `loadData` (fetch).
- `js/charts.js` — `bigNumberSVG` / `barChartSVG` / `donutSVG` (puros).
- `js/specialty.js` — seletor "sua especialidade" (puro).
- `js/capture.js` — `buildPayload` (puro) + `submitLead`.
- `js/main.js` — wiring DOM.

## Pendências (Frente 3)
- **Endpoint do Google Sheet:** hoje o form roda em **modo log** (`LEAD_ENDPOINT` vazio em
  `js/capture.js`). Definir o webhook (Apps Script) e setar a constante.
- **PDF gated:** gerar o relatório completo e ligar o link "Baixe o PDF".
- **Deploy:** site standalone (ex.: `indice.medrankgpt.com.br` no Render) OU copiar a pasta
  para o site principal. `main` tem história git não relacionada — não fazer merge.
