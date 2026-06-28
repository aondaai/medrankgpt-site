---
id: 87
cluster: "7. Dados & Autoridade (PR)"
tipo: "Estudo de dados"
title: "Quantas menções a IA precisa para recomendar um médico (estudo)"
slug: "/estudos/quantas-mencoes-a-ia-precisa-para-recomendar-um-medico-estudo"
meta_title: "Quantas menções a IA precisa para recomendar um médico?"
meta_description: "Quantas menções em fontes confiáveis fazem a IA recomendar um médico? Conheça a metodologia do estudo MedRankGPT que mede o limiar de citação em ChatGPT e Gemini."
prompt_alvo: "quantas menções a IA precisa para recomendar um médico"
keyword: "menções IA recomendação médico"
intencao: "Informacional"
funil: "Topo (ToFu)"
formato_aeo: "Estudo/análise"
schema: [Article, Dataset]
cta: "Diagnóstico grátis"
onda: 1
status: "Rascunho — requer dados reais"
hub: "/estudos/"
relacionadas:
  - /estudos/onsite-vs-offsite-de-onde-vem-o-que-a-ia-diz-sobre-medicos
  - /estudos/indice-medrankgpt-as-especialidades-mais-citadas-pela-ia-no-brasil
  - /estudos/25-estatisticas-de-ia-na-saude-que-todo-medico-deveria-saber
  - /guia/o-que-e-aeo-answer-engine-optimization-na-medicina
faq:
  - q: "Existe um número exato de menções que garante recomendação?"
    a: "Provavelmente não há um número mágico — o estudo busca um limiar prático, a faixa a partir da qual a probabilidade de citação sobe de forma relevante. Os valores serão publicados após a coleta."
  - q: "Só a quantidade de menções importa?"
    a: "Não. O estudo testa quantidade junto com qualidade da fonte e consistência da informação. Dez menções consistentes em fontes confiáveis tendem a pesar mais que muitas menções dispersas ou contraditórias."
  - q: "Como o estudo mede 'recomendação' da IA?"
    a: "Recomendação é definida como a IA citar o médico nominalmente ao responder uma pergunta de paciente. O protocolo distingue ser apenas mencionado de ser apresentado como opção de resposta."
  - q: "Comprar menções faz a IA recomendar mais?"
    a: "O estudo não estimula nem mede compra de menções. Conformidade com o CFM é premissa: menções devem vir de conteúdo legítimo, sem autopromoção indevida nem sensacionalismo."
---

# Quantas menções a IA precisa para recomendar um médico (estudo)

**Este estudo do MedRankGPT investiga o limiar de menções: a partir de quantas citações em fontes confiáveis a probabilidade de a IA recomendar um médico sobe de forma relevante. A hipótese é que não existe um número mágico isolado, mas uma combinação de quantidade, qualidade da fonte e consistência da informação. A metodologia está definida; os números serão preenchidos após a coleta.** Esta página explica a pergunta, o desenho do estudo e como os resultados deverão ser lidos.

*Os limiares e percentuais serão publicados quando o estudo for concluído. Todos os valores nesta página são placeholders explícitos — nenhum número foi inventado.*

## A pergunta que o estudo responde

Médicos perguntam: "quantas vezes preciso aparecer na internet para a IA começar a me indicar?" A resposta intuitiva — "quanto mais, melhor" — é vaga demais para guiar decisões. O estudo busca precisão:

- **A partir de quantas menções** a probabilidade de citação pela IA cresce de forma relevante — `[DADO A VALIDAR — faixa de menções no ponto de inflexão]`.
- **Quanto pesa a qualidade da fonte** versus a quantidade pura de menções — `[DADO A VALIDAR — comparação quantidade vs. qualidade]`.
- **Se há retorno decrescente**: a partir de que ponto novas menções deixam de aumentar a chance de citação — `[DADO A VALIDAR — ponto de saturação]`.

## Metodologia (em construção)

### Definições operacionais

- **Menção**: ocorrência do nome do médico/clínica em uma fonte indexável (site próprio, diretório, portal, imprensa, artigo).
- **Recomendação**: a IA cita o médico nominalmente ao responder uma pergunta de paciente — distinta de apenas listar a especialidade.

### O que será medido

- **Curva menção → citação**: relação entre o número de menções de um médico e a probabilidade de ele ser citado pela IA — `[DADO A VALIDAR — formato e inclinação da curva]`.
- **Limiar prático**: faixa de menções em que a probabilidade cruza um patamar relevante — `[DADO A VALIDAR — valor do limiar]`.
- **Efeito da consistência**: impacto de a informação ser idêntica entre fontes versus contraditória — `[DADO A VALIDAR — diferença de probabilidade]`.

### Como será medido

1. **Amostra de médicos** com diferentes níveis de presença online, do quase invisível ao muito citado — `[DADO A VALIDAR — tamanho da amostra]`.
2. **Contagem de menções** por médico, classificadas por tipo de fonte (onsite, diretório, portal, imprensa).
3. **Teste de citação**: cada médico é "procurado" via banco de prompts em ChatGPT, Gemini, Perplexity e Google AI — `[DADO A VALIDAR — número de prompts por médico]`.
4. **Repetições** para captar variação de resposta — `[DADO A VALIDAR — número de repetições]`.
5. **Modelagem**: relacionar contagem de menções e qualidade de fonte com a probabilidade de citação, controlando por especialidade e região.

## O que o resultado vai mostrar

| Faixa de menções | Probabilidade de a IA citar o médico |
|---|---|
| Poucas | `[DADO A VALIDAR]` |
| Intermediária | `[DADO A VALIDAR]` |
| Alta | `[DADO A VALIDAR]` |
| Muito alta | `[DADO A VALIDAR]` |

A curva completa, com o limiar e o ponto de saturação, entra aqui na publicação.

## Como interpretar (e como não interpretar)

- **Limiar é orientação, não garantia.** Atingir a faixa indicada aumenta a probabilidade — não assegura citação em toda resposta.
- **Qualidade antes de quantidade.** O estudo testa explicitamente se poucas menções fortes superam muitas menções fracas; provável que sim.
- **Consistência conta.** Informação igual entre fontes (mesmo nome, CRM, especialidade) tende a pesar mais que volume disperso.
- **Sem atalhos antiéticos.** O estudo não mede nem incentiva compra de menções; menções devem vir de conteúdo legítimo, em conformidade com o CFM.

De onde essas menções vêm — site próprio ou fontes externas — é tema do estudo [onsite vs offsite](/estudos/onsite-vs-offsite-de-onde-vem-o-que-a-ia-diz-sobre-medicos). Para o mecanismo geral, veja [o que é AEO na medicina](/guia/o-que-e-aeo-answer-engine-optimization-na-medicina).

## Perguntas frequentes

**Existe um número exato de menções que garante recomendação?**
Provavelmente não há um número mágico — o estudo busca um limiar prático, a faixa a partir da qual a probabilidade de citação sobe de forma relevante. Os valores serão publicados após a coleta.

**Só a quantidade de menções importa?**
Não. O estudo testa quantidade junto com qualidade da fonte e consistência da informação. Dez menções consistentes em fontes confiáveis tendem a pesar mais que muitas menções dispersas ou contraditórias.

**Como o estudo mede "recomendação" da IA?**
Recomendação é definida como a IA citar o médico nominalmente ao responder uma pergunta de paciente. O protocolo distingue ser apenas mencionado de ser apresentado como opção de resposta.

**Comprar menções faz a IA recomendar mais?**
O estudo não estimula nem mede compra de menções. Conformidade com o CFM é premissa: menções devem vir de conteúdo legítimo, sem autopromoção indevida nem sensacionalismo.

---

## Quantas menções você já tem?

O MedRankGPT faz um **diagnóstico gratuito** que mapeia suas menções atuais e mostra o quanto falta para a IA começar a citar você.

[**→ Solicitar diagnóstico grátis**](/#contato)
