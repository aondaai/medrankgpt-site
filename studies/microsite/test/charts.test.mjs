import { test } from 'node:test';
import assert from 'node:assert/strict';
import { bigNumberSVG, barChartSVG, donutSVG } from '../js/charts.js';

test('bigNumberSVG mostra a porcentagem', () => {
  const svg = bigNumberSVG(0.845, 'invisíveis');
  assert.match(svg, /^<svg/);
  assert.match(svg, /84%/);
  assert.match(svg, /invisíveis/);
});

test('barChartSVG faz uma barra por item e marca o destaque', () => {
  const svg = barChartSVG([
    { label: 'Dermatologia', value: 0.05, highlight: true },
    { label: 'Reumatologia', value: 0.34 },
  ]);
  assert.equal((svg.match(/<rect/g) || []).length >= 2, true);
  assert.match(svg, /Dermatologia/);
  assert.match(svg, /Reumatologia/);
});

test('donutSVG cria um arco (circle com dash) por segmento', () => {
  const svg = donutSVG([
    { label: 'marketplace', value: 0.89, color: 'var(--viz-4)' },
    { label: 'outro', value: 0.11, color: 'var(--viz-1)' },
  ]);
  assert.equal((svg.match(/<circle/g) || []).length, 2);
  assert.match(svg, /var\(--viz-4\)/);
});
