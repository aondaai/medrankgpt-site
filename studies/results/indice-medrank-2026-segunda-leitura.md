# Índice MedRank 2026 — Segunda Leitura (insights não explorados)

> Re-análise do mesmo `aggregates.json` (coleta 2026-06-28), **sem nova coleta de API**.
> O relatório original ([`indice-medrank-2026-resultados.md`](indice-medrank-2026-resultados.md))
> usou as manchetes principais; este documento garimpa os cortes cruzados que ficaram parados
> no agregado: regional, melhor-vs-procedimento, mapa de oportunidade por especialidade e o
> comportamento do Google AI Overview. Mesma amostra: **20 especialidades × 9 capitais**.

---

## 1. "Melhor X" e "procedimento Y" são jogos opostos — e o médico ganha o segundo

No Google, quem leva a **posição #1** muda completamente conforme a intenção da busca:

| Quem pega o #1 | "melhor [especialista]" (180) | "[procedimento]" (360) |
|---|---|---|
| **Marketplace** (Doctoralia) | **89,4%** | **15,6%** |
| Sites próprios ("outro") | 5,6% | **36,4%** |
| **Social (Instagram)** | 2,8% | **22,2%** |
| Clínica | 0,6% | 11,1% |
| Hospital | 1,7% | 10,6% |

- No genérico, o **Doctoralia** domina o #1 (160 de 180). O Instagram aparece só 5 vezes.
- No procedimento, o **Instagram VENCE o Doctoralia no #1 (76 × 56)** e o marketplace desaba pra 15,6%.

> **Leitura de venda:** a mensagem muda por intenção. No "melhor X" o médico foge do Doctoralia;
> no "procedimento Y" ele já pode **liderar** com Instagram + site próprio. O posicionamento
> individual paga exatamente na busca específica.

---

## 2. O Google espreme o médico de forma desigual por região — o ChatGPT não

| Cidade | Marketplace no #1 (Google) | Cita médico (ChatGPT) |
|---|---|---|
| **São Paulo** | **26,7%** | 92,5% |
| Brasília | 33,3% | 86,2% |
| Curitiba | 38,3% | 96,2% |
| Recife | 38,3% | 93,8% |
| Salvador | 40,0% | 95,0% |
| Porto Alegre | 43,3% | 92,5% |
| Rio de Janeiro | 46,7% | 91,2% |
| Belo Horizonte | 46,7% | 92,5% |
| **Fortaleza** | **48,3%** | 95,0% |

O domínio do marketplace varia **1,8×** entre capitais (27% → 48%). Já o ChatGPT cita médico em
**86–96% em todas** — praticamente plano.

> **Leitura:** "o Google te esconde" é um argumento mais forte **fora do eixo SP**. A IA é um
> jogo nacional uniforme; o Google é regional.

---

## 3. Mapa de oportunidade — onde a dor (e a disposição a pagar) é máxima

Cruzamento de **invisibilidade na IA** (Camada 2) × **domínio de marketplace no Google**.
Score de dor = 60% (1 − visível na IA) + 40% (marketplace no #1). Ordenado da maior dor pra menor.

| # | Especialidade | Visível na IA | Marketplace #1 | nº médicos | Score dor |
|---|---|---|---|---|---|
| 1 | **Psiquiatria** | 8,2% | 66,7% | 135 | 81,8 |
| 2 | Nutrologia | 13,6% | 48,1% | 125 | 71,1 |
| 3 | Ortopedia e Traumatologia | 11,5% | 44,4% | 131 | 70,9 |
| 4 | Endocrinologia | 14,9% | 48,1% | 134 | 70,3 |
| 5 | Otorrinolaringologia | 13,1% | 44,4% | 130 | 69,9 |
| 6 | Ginecologia e Obstetrícia | 12,6% | 40,7% | 135 | 68,7 |
| 7 | **Dermatologia** | **5,2%** | 29,6% | 135 | 68,7 |
| 8 | Pediatria | 13,5% | 40,7% | 133 | 68,2 |
| 9 | Geriatria | 17,6% | 44,4% | 119 | 67,2 |
| 10 | Cardiologia | 16,9% | 40,7% | 130 | 66,1 |
| 11 | Oftalmologia | 7,4% | 25,9% | 135 | 65,9 |
| 12 | Coloproctologia | 26,1% | 51,8% | 115 | 65,1 |
| 13 | Urologia | 18,5% | 37,0% | 135 | 63,7 |
| 14 | Cirurgia Plástica | 9,7% | 22,2% | 134 | 63,1 |
| 15 | Neurologia | 17,6% | 33,3% | 131 | 62,8 |
| 16 | Mastologia | 22,7% | 40,7% | 110 | 62,7 |
| 17 | Cirurgia Vascular | 18,1% | 33,3% | 127 | 62,5 |
| 18 | Gastroenterologia | 13,2% | 25,9% | 129 | 62,5 |
| 19 | Pneumologia | 21,3% | 37,0% | 122 | 62,0 |
| 20 | **Reumatologia** | **34,4%** | 48,1% | 122 | 58,6 |

> **Leitura:** **Psiquiatria** é a mais espremida das duas pontas (quase invisível na IA E o
> Google a manda pro marketplace 2 em cada 3 vezes). **Dermatologia** é a campeã de
> invisibilidade na IA (5,2%). **Reumatologia** é onde a IA já "fechou" — menor dor, venda mais difícil.

---

## 4. Quando a IA do Google aparece, ela age como o ChatGPT — não como o Google orgânico

Google AI Overview (via SerpApi), n=531:

- **Não exibe IA** em 35,2% das buscas médicas — sobe pra **42,2% no "melhor [especialista]"**
  (postura conservadora YMYL), 31,6% no procedimento.
- **Quando exibe** (n=344): nomeia médico em **55,5%**, mas aponta marketplace em só **13,4%**.

> O SERP orgânico faz o oposto (manda pro Doctoralia). São **duas faces do mesmo Google**: o
> link azul empurra pro marketplace, a IA do Google nomeia gente — lendo as mesmas fontes.

---

## 5. O #1 não é a página inteira: sites próprios já dominam o "share"

Mesmo onde o marketplace pega o topo, o bucket **"outro" (sites próprios)** detém o maior
**share médio da 1ª página**: **55,4%** no "melhor" e **52,8%** no procedimento. O marketplace
fica com só 8–13% do share total.

> **Leitura:** há muito mais espaço orgânico do que o "#1 = Doctoralia" sugere. O #1 é a vitrine,
> mas a página inteira já é majoritariamente de sites próprios e clínicas.

---

## 6. A vaga da IA tem dono emergente — e é mapeável

Top médicos citados pelo ChatGPT (de 720 respostas):

| Médico | Citações |
|---|---|
| Dr. Gilberto Studart | 9 |
| Dr. Milton Rocha | 6 |
| Dr. José Lourenço | 6 |
| Dr. Nilo Peçanha | 5 |
| Dr. Reyner Abrantes Stival | 4 |

Nenhum domina (o líder tem 1,25% das respostas), o que confirma a pulverização — **mas** já dá
pra montar o "quem já ganhou a IA" por especialidade e usar como benchmark/prova social.

---

## Como ler estes números (mesmas ressalvas do relatório original)

- Tudo derivado do **mesmo `aggregates.json`** — agregado e anonimizado, coleta 2026-06-28.
- Sem acesso ao nível-resposta (os `raw_demand/raw_supply` não foram versionados), então não há
  intervalo de confiança nem análise de texto aqui — apenas re-corte do que já estava agregado.
- O "score de dor" da seção 3 é uma composição editorial (60/40), não uma métrica do engine.
- SERP/AIO refletem o momento da coleta; risco-CFM é heurístico.
