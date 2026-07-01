# Relatório robusto — Índice MedRank 2026

**Data:** 2026-06-30
**Status:** Design aprovado (estrutura + decisões); pendente revisão da spec escrita.

## Problema

O PDF gated atual (`/indice/indice-medrank-2026.pdf`) é uma impressão do microsite `/indice/`:
7 páginas, mesmas manchetes do site, parágrafos curtos. É raso. Queremos um material
mais robusto, com mais conclusões e mais números — sem inventar dados.

O `aggregates.json` já contém muito mais sinal do que o site/PDF expõem hoje. Quase todo
o "mais números" vem de cortes que existem nos dados e nunca foram mostrados.

## Decisões (fixadas no brainstorming)

1. **Genérico, porém mais robusto** — um único relatório para todos os leads, muito mais
   denso. "Personalizado" = mais autoral/aprofundado, **não** por-médico nem por-lead.
2. **Estudo que vende (equilíbrio)** — corpo é estudo sério e isento; a virada para "o que
   fazer" (AEO/playbook/CTA) ganha uma seção forte, mas não domina.
3. **HTML longo → PDF, reusando o sistema** — nova página em `/indice/relatorio/`
   reaproveitando `tokens.css`, `js/charts.js` e `aggregates.json`. Números 100%
   sincronizados com os dados (sem hardcode). O microsite curto `/indice/` continua como
   teaser; o link do gated passa a apontar para o novo relatório.
4. **Eu entrego só o HTML** com CSS de impressão pronto. O usuário gera o PDF no navegador
   (print-to-PDF) quando quiser revisar visualmente. Não rodo headless nesta entrega.

## Arquitetura

```
indice/
  relatorio/
    index.html        # relatório longo (14 seções)
    report.css        # estende tokens.css; estilos de seção + @media print
    js/
      report.js       # importa loadData() + charts.js; preenche o relatório
```

- **Reuso direto:** `js/report.js` importa `loadData()` de `../js/data.js` e os geradores de
  `../js/charts.js` (`bigNumberSVG`, `barChartSVG`, `donutSVG`). Mesma fonte de dados
  (`../aggregates.json`).
- **Adições mínimas em `js/charts.js`:**
  - `groupedBarSVG(rows)` — barras rotuladas para comparar os 3 tipos de prompt e cortes
    lado a lado. (Pode ser implementado reusando `barChartSVG` se a forma bater.)
  - `tableHTML(headers, rows, opts)` — tabela de dados simples para os apêndices.
  - Helper de derivação extra em `data.js` para cortes ainda não derivados (por_tipo_prompt
    do ChatGPT, AIO entre-presentes, ChatGPT por especialidade, top_medicos). Acrescenta a
    `normalizeData()` sem alterar os campos existentes que o microsite consome.
- **Impressão:** `@page { size: A4; margin: ... }`, `break-inside: avoid` nas seções/figuras,
  `break-before` onde fizer sentido, esconder elementos só-tela (ex.: âncoras de rolagem).
- **Não reescrever** nada do microsite. O wiring do gated (qual PDF o formulário libera)
  fica **deferido** — decidido em um passo seguinte, fora desta entrega.

## Estrutura do relatório (14 seções)

Arco narrativo: **a IA já recomenda → mas lê poucas fontes → o médico está invisível → dá
pra virar.** Cada seção = número-manchete + gráfico + 2-3 parágrafos de análise + um *box de
conclusão* (uma frase amarrada a um número).

Números abaixo conferidos contra `indice/aggregates.json` (arredondamento do site: `pct()`).

1. **Sumário executivo** — tese em 1 parágrafo + 6 números-chave (84% invisíveis · 93% cita
   médico · 89% Doctoralia #1 · 42% instabilidade · 35% sem AIO · 2.567 médicos) + caixa
   "5 conclusões em 30 segundos".

2. **Metodologia (à frente, para credibilidade)** — 2.567 médicos reais (roster top Doctoralia),
   20 especialidades × 9 capitais, 3 superfícies (ChatGPT `gpt-4o-search-preview`, Google SERP
   via Serper, Google AIO via SerpApi). Os 3 tipos de prompt (melhor / confiança / procedimento).
   Definição de "visível" = a IA nomeou o médico. Ressalvas honestas (IA via API = proxy do
   produto de consumo; SERP/AIO refletem o momento; risco-CFM heurístico).

3. **A IA já nomeia médicos — e confia** — ChatGPT cita médico em **93%**. Por tipo de prompt:
   melhor **98%**, confiança **100%**, procedimento **87%**. Risco-CFM em só **0,28%** das
   respostas. *Conclusão:* não é *se* a IA recomenda — é *quem*.

4. **Mas lê as mesmas fontes** — ChatGPT cita o Doctoralia como fonte em **35%** das respostas.
   A IA não inventa nomes; ela lê o marketplace. *Conclusão:* quem domina as fontes domina a
   resposta.

5. **No Google, o paciente cai no marketplace** — Doctoralia no #1 em **89%** das buscas
   "melhor [especialista]". Nuance nova: apesar do #1, o marketplace tem só **~13%** do share
   médio da página — os médicos estão lá, mas fragmentados. Desigualdade regional: São Paulo
   **27%** → Fortaleza **48%** de #1 marketplace. Gráfico de barras por capital + por
   especialidade (Psiquiatria 67% no topo).

6. **A virada do procedimento** — na busca específica ("rinoplastia", "catarata"), marketplace
   cai para **16%** dos #1 e o **Instagram lidera** (76× no #1, à frente do Doctoralia 56×);
   social = **22%** dos #1. Hospitais/clínicas aparecem. *Conclusão:* em busca específica, as
   propriedades próprias do médico (site, Instagram, clínica) competem de verdade.

7. **O Google esconde a própria IA** — Google não mostra AIO em **35%** das buscas (e **42%**
   no "melhor [especialista]", vs 32% em procedimento). **Mas quando o AIO aparece**, ele cita
   médico em **56%** e marketplace em só **13%** — é a superfície mais amigável ao médico, e o
   Google a liga menos justamente na busca por especialista.

8. **A camada da invisibilidade** — de 2.567 médicos, **84%** são invisíveis para a IA.
   Dispersão por especialidade: Reumatologia **34%** visível (melhor) vs Dermatologia **5%**
   (pior) — ~7× de diferença. Concentração: **Dr. Gilberto Studart citado 9×**; poucos nomes
   absorvem a maior parte das citações. *Conclusão:* a visibilidade é escassa e concentrada —
   vantagem de quem chega primeiro.

9. **A IA é uma roleta** — repita a mesma pergunta e em **42%** das vezes o médico recomendado
   muda. *Conclusão:* ser a resposta *consistente* é um diferencial defensável.

10. **Mapa de oportunidade** — índice de dor por especialidade = 60% invisibilidade na IA +
    40% marketplace no #1 (composição editorial, já em `data.js`). Psiquiatria lidera. Onde
    posicionar-se vale mais.

11. **Playbook AEO (o que fazer)** — como virar a resposta da IA: presença consistente nas
    fontes que a IA lê (perfis, conteúdo, menções, site com sinais técnicos), dentro das regras
    do CFM. Checklist acionável de 5-7 itens. Seção forte, mas sem dominar o relatório.

12. **Conclusões** — lista numerada de ~10 conclusões, cada uma amarrada a um número do estudo.
    É a entrega explícita de "mais conclusões".

13. **Apêndice de dados** — densidade pura de números:
    - **Tabela por especialidade** (20 linhas): visível na IA · marketplace #1 no Google ·
      ChatGPT cita médico.
    - **Tabela por capital** (9 linhas): marketplace #1 · ChatGPT cita médico.

14. **CTA + rodapé** — diagnóstico gratuito; metodologia/ressalvas; fonte (`aggregates.json`).

Resultado: ~16-18 páginas impressas, ~6 gráficos novos + 2 tabelas, tudo derivado dos dados
existentes.

## Componentes e responsabilidades

| Unidade | O que faz | Depende de |
|---|---|---|
| `relatorio/index.html` | Marcação das 14 seções com slots `data-fill`/`data-chart` | `report.css`, `report.js` |
| `relatorio/report.css` | Layout longo + tipografia + `@media print` | `../tokens.css` |
| `relatorio/js/report.js` | Carrega dados, preenche slots, renderiza gráficos/tabelas | `../js/data.js`, `../js/charts.js` |
| `js/charts.js` (+`groupedBarSVG`,`tableHTML`) | Geradores SVG/HTML reutilizáveis | — |
| `js/data.js` (derivações extra) | Novos cortes (prompt, AIO, ChatGPT/esp, top médicos) | `aggregates.json` |

Cada unidade é compreensível e testável isoladamente: o HTML é estático com slots; o JS lê
dados e preenche; os geradores de gráfico são funções puras (entrada → string SVG/HTML).

## Verificação (critérios de sucesso)

- [ ] `/indice/relatorio/` abre sem erro de console e todos os slots `data-fill`/`data-chart`
      são preenchidos (nenhum "—" remanescente).
- [ ] Todo número exibido bate com `aggregates.json` (nenhum valor hardcoded no HTML/JS).
- [ ] O microsite `/indice/` continua funcionando sem regressão (mesmos campos em `data.js`).
- [ ] Em "Imprimir → Salvar como PDF" (A4), seções e figuras não quebram no meio; saída limpa.
- [ ] As 14 seções estão presentes, na ordem, com box de conclusão e a seção de conclusões
      numeradas + apêndice de tabelas.

## Fora de escopo

- Personalização por médico ou por lead (coleta nova de dados).
- Geração headless do PDF nesta entrega (o usuário imprime).
- Reescrever o microsite ou o sistema de captura de leads.
- **Wiring do gated** (apontar o formulário/link de download para o novo PDF) — deferido.
- Qualquer dado novo/externo além do `aggregates.json` atual.
