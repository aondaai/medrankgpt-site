# Plano de expansão — SEO local + backlinks (offsite)

> Documento interno. Não é linkado, não está no sitemap, não é indexado. Os dois itens abaixo
> **não** foram gerados à mão nesta sessão de propósito: páginas locais precisam da profundidade
> (~2.000 palavras) do pipeline de conteúdo, e backlinks são execução de outreach, não código.
> Gerá-los como páginas rasas/duplicadas prejudicaria o SEO que estamos otimizando.

---

## 1. Matriz local — completar o grid 6 × 10

**Situação atual:** 30 páginas em `/local/`, mas cada especialidade cobre apenas **um** conjunto
disjunto de 5 cidades. Resultado: lacunas óbvias como "ginecologista em São Paulo" (não existe) e
"dermatologista no Rio de Janeiro" (não existe).

| Especialidade | Cidades cobertas hoje | Cidades faltando (criar) |
|---|---|---|
| Cirurgião plástico | SP, BH, Curitiba, Fortaleza, Salvador | Rio, Brasília, Goiânia, Porto Alegre, Recife |
| Dermatologista | SP, BH, Curitiba, Fortaleza, Salvador | Rio, Brasília, Goiânia, Porto Alegre, Recife |
| Ortopedista | SP, BH, Curitiba, Fortaleza, Salvador | Rio, Brasília, Goiânia, Porto Alegre, Recife |
| Ginecologista | Rio, Brasília, Goiânia, Porto Alegre, Recife | SP, BH, Curitiba, Fortaleza, Salvador |
| Oftalmologista | Rio, Brasília, Goiânia, Porto Alegre, Recife | SP, BH, Curitiba, Fortaleza, Salvador |
| Psiquiatra | Rio, Brasília, Goiânia, Porto Alegre, Recife | SP, BH, Curitiba, Fortaleza, Salvador |

**Fase 1 — fechar o grid (30 páginas novas).** Padrão de slug já em uso:
`/local/melhor-{especialidade}-em-{cidade}-como-a-ia-escolhe-e-como-aparecer/`

City slugs: `sao-paulo`, `belo-horizonte`, `curitiba`, `fortaleza`, `salvador`,
`rio-de-janeiro`, `brasilia`, `goiania`, `porto-alegre`, `recife`.

Lista exata a gerar:
- cirurgiao-plastico × {rio-de-janeiro, brasilia, goiania, porto-alegre, recife}
- dermatologista × {rio-de-janeiro, brasilia, goiania, porto-alegre, recife}
- ortopedista × {rio-de-janeiro, brasilia, goiania, porto-alegre, recife}
- ginecologista × {sao-paulo, belo-horizonte, curitiba, fortaleza, salvador}
- oftalmologista × {sao-paulo, belo-horizonte, curitiba, fortaleza, salvador}
- psiquiatra × {sao-paulo, belo-horizonte, curitiba, fortaleza, salvador}

**Fase 2 — novas especialidades já existentes em `/especialidades/` mas não em `/local/`:**
cardiologista, pediatra, endocrinologista, urologista, gastroenterologista — cada uma × top 10 capitais.
Priorizar especialidades de alto ticket e busca local forte (cardiologista, urologista).

**Regras anti-canibalização / anti-thin-content (obrigatórias no pipeline):**
- Cada página com conteúdo **único** por cidade (panorama da concorrência local, bairros, portais
  citados pela IA naquela praça) — não trocar só o nome da cidade num template.
- Reaproveitar o template já validado em `/local/melhor-dermatologista-em-sao-paulo-.../` (schema
  Article + FAQPage + BreadcrumbList, ~2.000 palavras, 28 links internos).
- Após gerar: adicionar cada URL ao `sitemap.xml` e ao `llms.txt`, e garantir card no hub `/local/`.
- Interligar cidades irmãs ("outras cidades") e especialidades irmãs na mesma cidade.

**Impacto esperado:** alto. Duplica a superfície de busca local (a categoria que mais migrou
para resposta por IA) usando um template já comprovado.

---

## 2. Programa de backlinks / menções offsite

> Esta é literalmente a entrega "offsite" do produto MedRankGPT — vale dogfood. A IA tira a maior
> parte do que diz sobre uma marca de **fontes externas**, então o site precisa ser citado fora dele.

**Alvos prioritários (todos CFM-safe — informativos, sem promessa de resultado):**
1. **Perfil da Empresa no Google** de cada cliente — base do AEO local (ver novo guia
   `/guia/google-meu-negocio-para-medicos-e-a-busca-por-ia/`).
2. **Diretórios médicos** (Doctoralia, BoaConsulta, iMedicina) — perfis completos e consistentes (NAP).
3. **Artigos-convidado** em portais de saúde e veículos regionais — conteúdo informativo assinado.
4. **Perfis em sociedades/associações** (SBD, SBC, CBC etc.) — alta autoridade temática.
5. **Imprensa local / pautas** — comentário de especialista (modelo HARO/“fonte de jornalista”).
6. **Citações cruzadas** entre as próprias páginas-pilar e parceiros não concorrentes.

**Cadência sugerida:** 4–6 menções/mês por cliente, priorizando fontes que a IA comprovadamente
cruza (diretórios + portais + associações). Medir com o monitoramento de menções já oferecido.

**KPI:** nº de fontes externas citando o cliente → correlação com aparição em ChatGPT/Gemini/AI Overviews.

---

## 3. Itens fora do escopo de código (precisam de você)
- **Conectar Ahrefs/Semrush via MCP** → habilita volume real, KD e rank tracking no próximo audit.
- **Cadência de freshness** → revisar `lastmod` + conteúdo trimestralmente.
