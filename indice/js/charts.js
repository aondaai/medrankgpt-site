// round-half-down via épsilon: o dado já vem pré-arredondado; mantém 84,5%→"84%" (herói),
// sem afetar 92,78%→"93%", 89%→"89%", 42,2%→"42%".
const pct = (v) => `${Math.round(v * 100 - 1e-9)}%`;
const esc = (s) => String(s).replace(/[<>&]/g, (c) => ({ '<': '&lt;', '>': '&gt;', '&': '&amp;' }[c]));

export function bigNumberSVG(value, legenda = '') {
  return `<svg viewBox="0 0 320 200" role="img" aria-label="${esc(pct(value))} ${esc(legenda)}" xmlns="http://www.w3.org/2000/svg">
  <text x="160" y="120" text-anchor="middle" font-family="var(--font-display)" font-weight="900"
        font-size="110" fill="var(--color-primary)">${pct(value)}</text>
  <text x="160" y="165" text-anchor="middle" font-family="var(--font-sans)" font-size="20"
        fill="var(--color-text-muted)">${esc(legenda)}</text>
</svg>`;
}

export function barChartSVG(items, { width = 520, barH = 26, gap = 14 } = {}) {
  const max = Math.max(...items.map((i) => i.value), 0.0001);
  const labelW = 180, trackW = width - labelW - 60;
  const rows = items.map((it, i) => {
    const y = i * (barH + gap);
    const w = Math.max(2, (it.value / max) * trackW);
    const fill = it.highlight ? 'var(--color-accent-coral)' : 'var(--viz-1)';
    return `<text x="0" y="${y + barH * 0.7}" font-family="var(--font-sans)" font-size="14"
        fill="var(--color-text)">${esc(it.label)}</text>
    <rect x="${labelW}" y="${y}" width="${w}" height="${barH}" rx="6" fill="${fill}"/>
    <text x="${labelW + w + 8}" y="${y + barH * 0.7}" font-family="var(--font-mono)" font-size="13"
        fill="var(--color-text-muted)">${pct(it.value)}</text>`;
  }).join('\n');
  const h = items.length * (barH + gap);
  return `<svg viewBox="0 0 ${width} ${h}" role="img" xmlns="http://www.w3.org/2000/svg">${rows}</svg>`;
}

export function donutSVG(segments, { size = 220, thickness = 38 } = {}) {
  const r = (size - thickness) / 2, cx = size / 2, cy = size / 2;
  const C = 2 * Math.PI * r;
  let offset = 0;
  const arcs = segments.map((s) => {
    const len = s.value * C;
    const dash = `${len} ${C - len}`;
    const el = `<circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="${s.color}"
      stroke-width="${thickness}" stroke-dasharray="${dash}" stroke-dashoffset="${-offset}"
      transform="rotate(-90 ${cx} ${cy})"></circle>`;
    offset += len;
    return el;
  }).join('\n');
  return `<svg viewBox="0 0 ${size} ${size}" role="img" xmlns="http://www.w3.org/2000/svg">${arcs}</svg>`;
}

// Barras com formatador de valor custom (p/ %, ×, casas decimais). Mesma estética do barChartSVG.
export function groupedBarSVG(items, { width = 520, barH = 26, gap = 14, fmt = pct } = {}) {
  const max = Math.max(...items.map((i) => i.value), 0.0001);
  const labelW = 180, trackW = width - labelW - 70;
  const rows = items.map((it, i) => {
    const y = i * (barH + gap);
    const w = Math.max(2, (it.value / max) * trackW);
    const fill = it.highlight ? 'var(--color-accent-coral)' : 'var(--viz-1)';
    return `<text x="0" y="${y + barH * 0.7}" font-family="var(--font-sans)" font-size="14"
        fill="var(--color-text)">${esc(it.label)}</text>
    <rect x="${labelW}" y="${y}" width="${w}" height="${barH}" rx="6" fill="${fill}"/>
    <text x="${labelW + w + 8}" y="${y + barH * 0.7}" font-family="var(--font-mono)" font-size="13"
        fill="var(--color-text-muted)">${esc(fmt(it.value, it))}</text>`;
  }).join('\n');
  const h = items.length * (barH + gap);
  return `<svg viewBox="0 0 ${width} ${h}" role="img" xmlns="http://www.w3.org/2000/svg">${rows}</svg>`;
}

// Tabela de dados semântica. headers: string[]; rows: (string|number)[][]; highlightCol opcional.
export function tableHTML(headers, rows, { caption = '' } = {}) {
  const head = `<tr>${headers.map((h) => `<th scope="col">${esc(h)}</th>`).join('')}</tr>`;
  const body = rows.map((r) =>
    `<tr>${r.map((c, i) => i === 0
      ? `<th scope="row">${esc(c)}</th>`
      : `<td>${esc(c)}</td>`).join('')}</tr>`).join('\n');
  const cap = caption ? `<caption>${esc(caption)}</caption>` : '';
  return `<table class="data-table">${cap}<thead>${head}</thead><tbody>${body}</tbody></table>`;
}
