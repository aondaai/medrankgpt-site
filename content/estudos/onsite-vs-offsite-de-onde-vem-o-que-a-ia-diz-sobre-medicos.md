---
id: 88
cluster: "7. Dados & Autoridade (PR)"
tipo: "Estudo de dados"
title: "Onsite vs offsite: de onde vem o que a IA diz sobre médicos"
slug: "/estudos/onsite-vs-offsite-de-onde-vem-o-que-a-ia-diz-sobre-medicos"
meta_title: "Onsite vs offsite: de onde a IA tira o que diz sobre médicos"
meta_description: "Site próprio ou fontes externas: o que pesa mais quando a IA fala de um médico? Conheça a metodologia do estudo MedRankGPT sobre origem das citações."
prompt_alvo: "de onde a IA tira informação sobre médicos: site próprio ou fontes externas"
keyword: "onsite offsite IA médicos"
intencao: "Informacional"
funil: "Topo (ToFu)"
formato_aeo: "Estudo/tese"
schema: [Article, FAQPage]
cta: "Diagnóstico grátis"
onda: 1
status: "Rascunho — requer dados reais"
hub: "/estudos/"
relacionadas:
  - /estudos/quantas-mencoes-a-ia-precisa-para-recomendar-um-medico-estudo
  - /estudos/indice-medrankgpt-as-especialidades-mais-citadas-pela-ia-no-brasil
  - /estudos/25-estatisticas-de-ia-na-saude-que-todo-medico-deveria-saber
  - /guia/o-que-e-aeo-answer-engine-optimization-na-medicina
faq:
  - q: "O que é onsite e o que é offsite neste estudo?"
    a: "Onsite é o conteúdo no domínio do próprio médico ou clínica (site, blog, página de especialidade). Offsite é tudo fora dele: diretórios, portais de saúde, imprensa, redes e artigos em terceiros."
  - q: "O estudo já diz se onsite ou offsite pesa mais?"
    a: "Ainda não. A página descreve a metodologia; os resultados serão publicados após a coleta. A hipótese é que os dois se reforçam, mas a proporção exata é o que o estudo vai medir."
  - q: "Se a IA usa muito offsite, não adianta ter site próprio?"
    a: "Adianta. Mesmo quando a IA cita uma fonte externa, o site próprio costuma ser a referência que alimenta e dá consistência às demais. O estudo testa exatamente esse encadeamento."
  - q: "Como o estudo identifica a origem de uma citação?"
    a: "Quando o motor de IA aponta a fonte, ela é classificada como onsite ou offsite. Quando não aponta, o estudo rastreia a informação até a origem mais provável seguindo um protocolo de atribuição."
---

# Onsite vs offsite: de onde vem o que a IA diz sobre médicos

**Este estudo do MedRankGPT investiga a origem das informações que a IA usa ao falar de um médico: o conteúdo do próprio site (onsite) ou fontes externas como diretórios, portais e imprensa (offsite). A tese de trabalho é que os dois se reforçam — o site próprio dá a versão consistente, e as fontes externas a amplificam —, mas a proporção exata é o que a coleta vai medir. A metodologia está definida; os números virão depois.** Esta página explica a pergunta, o desenho do estudo e o que cada cenário significa para o médico.

*A divisão entre onsite e offsite e todos os percentuais serão publicados quando o estudo for concluído. Os valores nesta página são placeholders explícitos — nenhum número foi inventado.*

## A pergunta que o estudo responde

Quando a IA descreve um médico, de onde ela tira aquilo? Se vier sobretudo do site próprio, controlar o próprio conteúdo é decisivo. Se vier de fontes externas, a estratégia muda. O estudo separa:

- **Quanto das citações** tem origem onsite versus offsite — `[DADO A VALIDAR — divisão percentual onsite vs. offsite]`.
- **Quais tipos de fonte offsite** mais alimentam a IA (diretórios, portais de saúde, imprensa, artigos) — `[DADO A VALIDAR — ranking de tipos de fonte]`.
- **Como onsite e offsite interagem**: o site próprio funciona como "fonte da verdade" que as externas repetem? — `[DADO A VALIDAR — grau de encadeamento entre fontes]`.

## Definições

- **Onsite**: conteúdo no domínio do próprio médico ou clínica — site institucional, blog, páginas de especialidade, perfil oficial.
- **Offsite**: tudo fora desse domínio — diretórios médicos, portais de saúde, imprensa, redes sociais, artigos publicados em terceiros.

## Metodologia (em construção)

### O que será medido

- **Origem da citação**: para cada resposta da IA que cita um médico, classificar a fonte como onsite ou offsite — `[DADO A VALIDAR — distribuição de origens]`.
- **Peso por tipo de fonte offsite**: frequência com que cada tipo de fonte externa aparece como base — `[DADO A VALIDAR — peso por tipo]`.
- **Consistência cruzada**: o quanto a informação onsite coincide com a offsite (nome, CRM, especialidade) — `[DADO A VALIDAR — taxa de coincidência]`.
- **Efeito do site próprio**: diferença de citação entre médicos com site próprio robusto e médicos sem — `[DADO A VALIDAR — diferença de probabilidade]`.

### Como será medido

1. **Amostra de médicos** com perfis variados de presença onsite e offsite — `[DADO A VALIDAR — tamanho da amostra]`.
2. **Banco de prompts** padronizado, rodado em ChatGPT, Gemini, Perplexity e Google AI — `[DADO A VALIDAR — número de prompts]`.
3. **Captura de fonte**: quando o motor cita a fonte, ela é registrada; quando não cita, aplica-se um protocolo de atribuição que rastreia a informação até a origem mais provável.
4. **Codificação onsite/offsite** seguindo manual fixo, com checagem de concordância entre avaliadores.
5. **Repetições** para captar variação de resposta — `[DADO A VALIDAR — número de repetições]`.

## O que o resultado vai mostrar

| Origem | Participação nas citações |
|---|---|
| Onsite (site próprio) | `[DADO A VALIDAR]` |
| Offsite — diretórios | `[DADO A VALIDAR]` |
| Offsite — portais de saúde | `[DADO A VALIDAR]` |
| Offsite — imprensa | `[DADO A VALIDAR]` |
| Offsite — outros | `[DADO A VALIDAR]` |

A quebra completa, por motor de IA e por especialidade, entra aqui na publicação.

## Como interpretar (e como não interpretar)

- **Não é onsite OU offsite — é onsite E offsite.** A leitura mais provável é de reforço mútuo: o site próprio dá consistência, as fontes externas amplificam.
- **Site próprio raramente é dispensável.** Mesmo quando a IA cita uma fonte externa, ela costuma ecoar o que o site oficial afirma. Sem onsite consistente, o offsite fica contraditório.
- **Inconsistência prejudica.** Nome, CRM e especialidade divergentes entre fontes confundem a IA — alinhar onsite e offsite é parte do trabalho.
- **É uma fotografia datada.** As fontes que a IA prioriza mudam; por isso o estudo é repetido em ciclos.

Quantas menções, no total, fazem diferença é tema do estudo [quantas menções a IA precisa](/estudos/quantas-mencoes-a-ia-precisa-para-recomendar-um-medico-estudo). Para o mecanismo geral, veja [o que é AEO na medicina](/guia/o-que-e-aeo-answer-engine-optimization-na-medicina).

## Perguntas frequentes

**O que é onsite e o que é offsite neste estudo?**
Onsite é o conteúdo no domínio do próprio médico ou clínica (site, blog, página de especialidade). Offsite é tudo fora dele: diretórios, portais de saúde, imprensa, redes e artigos em terceiros.

**O estudo já diz se onsite ou offsite pesa mais?**
Ainda não. A página descreve a metodologia; os resultados serão publicados após a coleta. A hipótese é que os dois se reforçam, mas a proporção exata é o que o estudo vai medir.

**Se a IA usa muito offsite, não adianta ter site próprio?**
Adianta. Mesmo quando a IA cita uma fonte externa, o site próprio costuma ser a referência que alimenta e dá consistência às demais. O estudo testa exatamente esse encadeamento.

**Como o estudo identifica a origem de uma citação?**
Quando o motor de IA aponta a fonte, ela é classificada como onsite ou offsite. Quando não aponta, o estudo rastreia a informação até a origem mais provável seguindo um protocolo de atribuição.

---

## De onde a IA tira o que diz sobre você?

O MedRankGPT faz um **diagnóstico gratuito** que mostra quais fontes — suas ou de terceiros — a IA usa ao falar do seu nome, e o que ajustar.

[**→ Solicitar diagnóstico grátis**](/#contato)
