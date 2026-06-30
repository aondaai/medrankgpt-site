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
