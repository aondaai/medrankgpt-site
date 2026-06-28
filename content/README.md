# content/ — Conteúdo das 100 páginas (MedRankGPT)

Cada página do plano (aba **Plano 100 Páginas**) vira **um arquivo `.md`** aqui.
A planilha continua sendo o painel de controle (status, metadados, schema); este
diretório guarda o corpo escrito. O caminho de cada arquivo está na coluna
**"Arquivo (content/)"** da planilha.

## Estrutura de silos (ramificação do domínio)

| Pasta | Cluster | Prefixo de URL |
|---|---|---|
| `guia/` | 1. Pilares & Educação | `/guia/` |
| `especialidades/` | 2. Especialidade × IA | `/especialidades/` |
| `local/` | 3. Local (Especialidade × Cidade) | `/local/` (refinar p/ `/cidade/especialidade`) |
| `condicoes/` | 4. Condições & Sintomas | `/condicoes/` |
| `procedimentos/` | 5. Procedimentos | `/procedimentos/` |
| `comparativos/` | 6. Comparativos | `/comparativos/` |
| `estudos/` | 7. Dados & Autoridade | `/estudos/` |
| `cfm/` | 8. Conformidade CFM | `/cfm/` |
| `listas/` | 9. Listicles | `/listas/` |
| `casos/` | 10. Casos & Prova | `/casos/` |
| `processo/` | 11. Processo & Transparência | `/processo/` |

Cada silo tem uma **hub page** (índice da pasta) que linka para as páginas-filhas,
e cada filha linka de volta para a hub. É isso que concentra autoridade e ajuda
IA e Google a indexar o tema.

## Convenção de front-matter

Todo arquivo começa com YAML espelhando a linha da planilha + os campos de
renderização (meta title/description, FAQ, relacionadas). Modelo:

```yaml
---
id: 1                              # ID da planilha
cluster: "1. Pilares & Educação"
tipo: "Pilar / Definição"
title: "..."                       # H1 da página
slug: "/guia/..."                  # slug siloado (coluna R)
meta_title: "..."                  # <title>, ~55-60 caracteres
meta_description: "..."            # meta description, ~150-155 caracteres
prompt_alvo: "..."                 # a pergunta real que a página responde
keyword: "..."
intencao: "Informacional"
funil: "Topo (ToFu)"
formato_aeo: "Glossário/Definição"
schema: [Article, FAQPage, DefinedTerm]
cta: "Diagnóstico grátis"
onda: 1
status: "Rascunho"                 # Rascunho | Revisão | Pronto | Publicado
hub: "/guia/"
relacionadas:                      # links internos (silo + cross-silo)
  - /guia/...
faq:                               # vira FAQPage schema + bloco visível
  - q: "..."
    a: "..."
---
```

## Princípio AEO de cada página (não negociável)

1. **Resposta direta no topo** — logo abaixo do H1, 2–4 frases que respondem o
   `prompt_alvo` de forma autossuficiente e citável (o trecho que a IA extrai).
2. **Escaneável** — H2/H3 claros, listas, tabelas, definições em destaque.
3. **FAQ** — 3–6 perguntas reais, respostas curtas (espelham o `faq` do front-matter).
4. **Dados estruturados** — os schemas listados em `schema`.
5. **CTA** — sempre o "Diagnóstico grátis" ao fim (e idealmente no meio).
6. **Sem estatística inventada** — números só vêm das páginas do cluster `/estudos/`.
