import { test } from 'node:test';
import assert from 'node:assert/strict';
import { buildPayload } from '../js/capture.js';

test('buildPayload normaliza e marca origem', () => {
  const p = buildPayload({ nome: ' Dra. Ana ', especialidade: 'Dermatologia',
    cidade: 'São Paulo', email: 'ANA@x.com ' }, 'diagnostico');
  assert.equal(p.nome, 'Dra. Ana');
  assert.equal(p.email, 'ana@x.com');
  assert.equal(p.origem, 'diagnostico');
  assert.ok(typeof p.capturado_em === 'string' && p.capturado_em.length > 0);
});

test('buildPayload rejeita email inválido', () => {
  assert.throws(() => buildPayload({ nome: 'X', email: 'semarroba' }, 'pdf'),
    /email inválido/);
});
