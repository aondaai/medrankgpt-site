import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { normalizeData } from '../js/data.js';

const RAW = JSON.parse(readFileSync(new URL('../aggregates.json', import.meta.url)));

test('normalizeData extrai os números-herói num formato plano', () => {
  const n = normalizeData(RAW);
  assert.equal(n.hero.totalMedicos, RAW.camada2_visibilidade_ia.total_medicos);
  assert.equal(n.hero.pctInvisivel, RAW.camada2_visibilidade_ia.pct_invisivel_ia);
  assert.equal(n.meta.especialidades, RAW.meta.especialidades);
  assert.equal(n.serp.melhorMarketplacePos1,
    RAW.google_serp.por_tipo_busca.melhor.pos1_por_tipo.marketplace);
  assert.equal(n.chatgpt.citaMedico, RAW.chatgpt.pct_cita_medico);
  assert.equal(n.chatgpt.instabilidade, RAW.chatgpt.instabilidade_pct_top_medico_muda);
  assert.equal(n.aio.semAioMelhor, RAW.google_aio.sem_aio_melhor);
});

test('porEspecialidade vira mapa visivel/invisivel', () => {
  const n = normalizeData(RAW);
  const derm = n.porEspecialidade['Dermatologia'];
  assert.ok(derm.visivel >= 0 && derm.visivel <= 1);
  assert.equal(Math.round((derm.visivel + derm.invisivel) * 100), 100);
});

test('regional ordena por marketplace asc e resolve chatgpt por cidade', () => {
  const n = normalizeData(RAW);
  const first = n.regional[0], last = n.regional[n.regional.length - 1];
  assert.ok(first.marketplaceGoogle <= last.marketplaceGoogle);     // ordenado asc
  assert.ok(n.regional.every((r) => typeof r.citaChatgpt === 'number')); // float OU objeto resolvido
});

test('oportunidade ordena por score de dor desc (60/40)', () => {
  const n = normalizeData(RAW);
  for (let i = 1; i < n.oportunidade.length; i++) {
    assert.ok(n.oportunidade[i - 1].scoreDor >= n.oportunidade[i].scoreDor);
  }
  const top = n.oportunidade[0];
  assert.ok(Math.abs(top.scoreDor - ((1 - top.visivelIa) * 0.6 + top.marketplaceGoogle * 0.4)) < 1e-9);
});

test('virada captura o flip melhor(marketplace) -> procedimento(social)', () => {
  const n = normalizeData(RAW);
  assert.ok(n.virada.melhorMarketplace > n.virada.procMarketplace); // marketplace cai no procedimento
  assert.equal(Array.isArray(n.virada.melhorTop), true);
  assert.equal(n.virada.melhorTop.length, 2);                       // [host, contagem]
});
