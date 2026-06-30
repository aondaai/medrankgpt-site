import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { normalizeData } from '../js/data.js';
import { specialtyValue, especialidadesList } from '../js/specialty.js';

const N = normalizeData(JSON.parse(readFileSync(new URL('../aggregates.json', import.meta.url))));

test('especialidadesList vem ordenada por menor visibilidade (pior primeiro)', () => {
  const list = especialidadesList(N);
  assert.ok(Array.isArray(list) && list.length >= 17);
  for (let i = 1; i < list.length; i++)
    assert.ok(list[i - 1].visivel <= list[i].visivel);
});

test('specialtyValue devolve visivel/invisivel da especialidade', () => {
  const v = specialtyValue(N, 'Dermatologia');
  assert.equal(v.visivel, N.porEspecialidade['Dermatologia'].visivel);
  assert.equal(v.invisivel, N.porEspecialidade['Dermatologia'].invisivel);
});

test('specialtyValue desconhecida devolve null', () => {
  assert.equal(specialtyValue(N, 'Inexistente'), null);
});
