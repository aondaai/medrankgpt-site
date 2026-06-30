import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

test('aggregates.json copiado é válido e tem as chaves esperadas', () => {
  const d = JSON.parse(readFileSync(new URL('../aggregates.json', import.meta.url)));
  for (const k of ['chatgpt', 'google_serp', 'google_aio', 'camada2_visibilidade_ia', 'meta'])
    assert.ok(k in d, `falta chave ${k}`);
  assert.equal(typeof d.camada2_visibilidade_ia.pct_invisivel_ia, 'number');
});
