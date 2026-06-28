---
id: 85
cluster: "7. Dados & Autoridade (PR)"
tipo: "Estudo de dados"
title: "Índice MedRankGPT: as especialidades mais citadas pela IA no Brasil"
slug: "/estudos/indice-medrankgpt-as-especialidades-mais-citadas-pela-ia-no-brasil"
meta_title: "Índice MedRankGPT: especialidades mais citadas pela IA | Brasil"
meta_description: "Qual especialidade médica a IA mais cita no Brasil? Conheça a metodologia do Índice MedRankGPT, que mede menções a médicos em ChatGPT, Gemini e Google AI."
prompt_alvo: "quais especialidades médicas a IA mais cita no Brasil"
keyword: "índice IA médicos brasil"
intencao: "Informacional"
funil: "Topo (ToFu)"
formato_aeo: "Estudo proprietário"
schema: [Dataset, Article]
cta: "Diagnóstico grátis"
onda: 1
status: "Rascunho — requer dados reais"
hub: "/estudos/"
relacionadas:
  - /estudos/quantas-mencoes-a-ia-precisa-para-recomendar-um-medico-estudo
  - /estudos/onsite-vs-offsite-de-onde-vem-o-que-a-ia-diz-sobre-medicos
  - /estudos/25-estatisticas-de-ia-na-saude-que-todo-medico-deveria-saber
  - /guia/o-que-e-aeo-answer-engine-optimization-na-medicina
faq:
  - q: "O Índice MedRankGPT já tem resultados publicados?"
    a: "Esta página descreve a metodologia do estudo. Os números serão divulgados quando a primeira rodada de coleta for concluída. Até lá, todos os valores aparecem como dados a validar."
  - q: "Quais IAs entram no Índice MedRankGPT?"
    a: "A medição cobre os principais motores de resposta usados no Brasil: ChatGPT, Google AI Overviews, Gemini e Perplexity. A lista exata e os pesos serão definidos no protocolo da rodada."
  - q: "O Índice diz que uma especialidade é melhor que outra?"
    a: "Não. O Índice mede visibilidade na IA — com que frequência médicos de cada especialidade são citados —, não qualidade clínica nem competência profissional. São coisas distintas."
  - q: "Com que frequência o Índice será atualizado?"
    a: "A intenção é repetir a coleta em ciclos regulares para acompanhar a evolução. A cadência (mensal, trimestral) será fixada no protocolo do estudo."
---

# Índice MedRankGPT: as especialidades mais citadas pela IA no Brasil

**O Índice MedRankGPT mede com que frequência médicos de cada especialidade são citados pelos motores de resposta com IA — ChatGPT, Gemini, Perplexity e Google AI Overviews — quando pacientes brasileiros fazem perguntas de saúde. O objetivo é mostrar onde a visibilidade na IA já está consolidada e onde ainda há espaço aberto, por especialidade.** A primeira edição está em construção; esta página documenta a pergunta, a metodologia e o que será medido.

*Os números do Índice serão publicados quando a primeira rodada de coleta for concluída. Até lá, todos os valores nesta página aparecem como placeholders explícitos.*

## A pergunta que o estudo responde

Quando um paciente pergunta à IA "qual o melhor cardiologista" ou "que médico trata enxaqueca", a resposta cita nomes, clínicas e fontes. Algumas especialidades aparecem muito; outras quase não aparecem. O Índice MedRankGPT responde de forma estruturada:

- **Quais especialidades a IA mais cita** ao responder perguntas de pacientes no Brasil.
- **Qual a distância** entre a especialidade mais citada e a menos citada — `[DADO A VALIDAR — diferença em pontos percentuais ou múltiplo entre topo e base do ranking]`.
- **Onde há espaço aberto**: especialidades com alta demanda de busca e baixa presença na IA.

Por que importa: a especialidade onde a IA cita pouco é também onde um único médico bem otimizado consegue se destacar mais rápido. O Índice transforma essa intuição em número.

## Metodologia (em construção)

O estudo segue um protocolo fixo, documentado antes da coleta para garantir que a próxima edição seja comparável.

### O que será medido

- **Taxa de menção por especialidade**: percentual de respostas da IA que citam ao menos um médico/clínica daquela especialidade, sobre o total de perguntas testadas — `[DADO A VALIDAR — taxa de menção, por especialidade]`.
- **Concentração**: quão concentradas as menções estão em poucos nomes versus distribuídas — `[DADO A VALIDAR — índice de concentração por especialidade]`.
- **Presença de fonte**: com que frequência a IA aponta a fonte da citação (site próprio, diretório, portal) — `[DADO A VALIDAR — percentual de respostas com fonte explícita]`.

### Como será medido

1. **Banco de perguntas (prompts)**: conjunto padronizado de perguntas reais de pacientes por especialidade — `[DADO A VALIDAR — número de prompts por especialidade]`.
2. **Motores testados**: ChatGPT, Google AI Overviews, Gemini e Perplexity, cada prompt rodado de forma idêntica em todos.
3. **Repetições**: cada prompt é repetido para captar variação de resposta da IA — `[DADO A VALIDAR — número de repetições por prompt]`.
4. **Janela de coleta**: período fechado para que a edição seja datada — `[DADO A VALIDAR — datas da coleta]`.
5. **Codificação**: cada resposta é lida e marcada (citou médico? qual especialidade? qual fonte?) seguindo um manual de codificação para reduzir subjetividade.

### Amostra de especialidades

A primeira edição cobre as especialidades de maior demanda de busca em saúde — `[DADO A VALIDAR — número de especialidades incluídas]`. A lista final e os critérios de inclusão serão publicados com o estudo.

## O que o ranking vai mostrar

Quando concluído, o Índice apresentará:

| Posição | Especialidade | Taxa de menção na IA |
|---|---|---|
| 1º | `[DADO A VALIDAR]` | `[DADO A VALIDAR]` |
| 2º | `[DADO A VALIDAR]` | `[DADO A VALIDAR]` |
| 3º | `[DADO A VALIDAR]` | `[DADO A VALIDAR]` |
| … | `[DADO A VALIDAR]` | `[DADO A VALIDAR]` |

A tabela completa, com todas as especialidades e a quebra por motor de IA, entra aqui na publicação.

## Como interpretar o Índice (e como não interpretar)

- **É um termômetro de visibilidade, não de qualidade.** Uma especialidade no topo significa que seus médicos são mais citados pela IA — não que sejam clinicamente superiores.
- **Visibilidade baixa = oportunidade.** Estar embaixo no ranking indica espaço aberto: menos concorrência por presença na IA.
- **É uma fotografia datada.** A IA muda suas fontes com frequência; por isso o Índice é repetido em ciclos.
- **Não substitui escolha clínica.** Nenhum paciente deve escolher médico só porque a IA cita mais — e o estudo deixa isso explícito.

Para entender o mecanismo por trás das citações, veja [o que é AEO na medicina](/guia/o-que-e-aeo-answer-engine-optimization-na-medicina) e [quantas menções a IA precisa para recomendar um médico](/estudos/quantas-mencoes-a-ia-precisa-para-recomendar-um-medico-estudo).

## Perguntas frequentes

**O Índice MedRankGPT já tem resultados publicados?**
Esta página descreve a metodologia do estudo. Os números serão divulgados quando a primeira rodada de coleta for concluída. Até lá, todos os valores aparecem como dados a validar.

**Quais IAs entram no Índice MedRankGPT?**
A medição cobre os principais motores de resposta usados no Brasil: ChatGPT, Google AI Overviews, Gemini e Perplexity. A lista exata e os pesos serão definidos no protocolo da rodada.

**O Índice diz que uma especialidade é melhor que outra?**
Não. O Índice mede visibilidade na IA — com que frequência médicos de cada especialidade são citados —, não qualidade clínica nem competência profissional. São coisas distintas.

**Com que frequência o Índice será atualizado?**
A intenção é repetir a coleta em ciclos regulares para acompanhar a evolução. A cadência (mensal, trimestral) será fixada no protocolo do estudo.

---

## Quer saber onde sua especialidade está no Índice?

O MedRankGPT faz um **diagnóstico gratuito** que mostra se ChatGPT, Gemini e o Google AI já citam você na sua especialidade — e o que falta para subir.

[**→ Solicitar diagnóstico grátis**](/#contato)
