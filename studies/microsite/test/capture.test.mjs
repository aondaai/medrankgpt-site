import { test } from 'node:test';
import assert from 'node:assert/strict';
import { buildBridgePayload, LEAD_ENDPOINT } from '../js/capture.js';

test('buildBridgePayload mapeia pro shape do bridge', () => {
  const p = buildBridgePayload({ nome: ' Dra. Ana ', especialidade: 'Dermatologia',
    cidade: 'São Paulo', telefone: ' 11 99999 ', email: 'ANA@x.com ' });
  assert.equal(p.nome, 'Dra. Ana');
  assert.equal(p.email, 'ana@x.com');
  assert.equal(p.telefone, '11 99999');
  assert.equal(p.perfil, 'Índice MedRank 2026');
  assert.equal(p.especialidade, 'Dermatologia — São Paulo');
  assert.deepEqual(Object.keys(p).sort(),
    ['email', 'especialidade', 'nome', 'perfil', 'telefone']);
});

test('sem cidade não adiciona separador; telefone vazio vira ""', () => {
  const p = buildBridgePayload({ nome: 'X', especialidade: 'Cardiologia', email: 'x@y.com' });
  assert.equal(p.especialidade, 'Cardiologia');
  assert.equal(p.telefone, '');
});

test('rejeita email inválido', () => {
  assert.throws(() => buildBridgePayload({ nome: 'X', email: 'semarroba' }), /email inválido/);
});

test('LEAD_ENDPOINT aponta pro bridge da mainpage', () => {
  assert.match(LEAD_ENDPOINT, /mainline-finance\.onrender\.com\/api\/medrank-lead/);
});
