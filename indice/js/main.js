import { loadData } from './data.js';
import { bigNumberSVG, barChartSVG, donutSVG } from './charts.js';
import { especialidadesList, specialtyValue } from './specialty.js';
import { buildBridgePayload, submitLead } from './capture.js';

const pct = (v) => `${Math.round(v * 100 - 1e-9)}%`;
const set = (key, html) => { for (const el of document.querySelectorAll(`[data-fill="${key}"]`)) el.innerHTML = html; };
const chart = (key, svg) => { const el = document.querySelector(`[data-chart="${key}"]`); if (el) el.innerHTML = svg; };

loadData().then((N) => {
  // herói
  set('hero-num', pct(N.hero.pctInvisivel));
  set('hero-num2', pct(N.hero.pctInvisivel));
  set('hero-n', N.hero.totalMedicos.toLocaleString('pt-BR'));
  chart('hero', bigNumberSVG(N.hero.pctInvisivel, 'invisíveis para a IA'));

  // experimento
  set('experimento-stats', [
    [N.meta.especialidades, 'especialidades'], [N.meta.capitais, 'capitais'],
    [N.hero.totalMedicos.toLocaleString('pt-BR'), 'médicos reais'], ['3', 'superfícies de IA'],
  ].map(([b, l]) => `<li><b>${b}</b>${l}</li>`).join(''));

  // google serp
  set('serp-melhor', pct(N.serp.melhorMarketplacePos1));
  chart('serp-donut', donutSVG([
    { label: 'Doctoralia (#1)', value: N.serp.melhorMarketplacePos1, color: 'var(--viz-4)' },
    { label: 'resto', value: 1 - N.serp.melhorMarketplacePos1, color: 'var(--viz-1)' },
  ]));

  // chatgpt
  set('cg-cita', pct(N.chatgpt.citaMedico));
  set('cg-fonte', pct(N.chatgpt.doctoraliaFonte));
  set('cg-instab', pct(N.chatgpt.instabilidade));

  // aio
  set('aio-melhor', pct(N.aio.semAioMelhor));

  // virada: melhor vs procedimento — mesmos 3 segmentos, cores fixas p/ comparar
  const dom = ([host, n]) => `${host} lidera o #1 (${n}×)`;
  const viradaDonut = (mkt, social) => donutSVG([
    { label: 'marketplace', value: mkt, color: 'var(--viz-4)' },
    { label: 'Instagram', value: social, color: 'var(--viz-2)' },
    { label: 'resto', value: Math.max(0, 1 - mkt - social), color: 'var(--viz-1)' },
  ]);
  set('virada-proc', pct(N.virada.procMarketplace));
  chart('virada-melhor', viradaDonut(N.virada.melhorMarketplace, N.virada.melhorSocial));
  chart('virada-proc-donut', viradaDonut(N.virada.procMarketplace, N.virada.procSocial));
  set('virada-top-melhor', dom(N.virada.melhorTop));
  set('virada-top-proc', dom(N.virada.procTop));

  // regional: Google espreme desigual; ChatGPT uniforme
  const reg = N.regional;
  set('regional-melhor-cidade', reg[0].cidade);
  set('regional-melhor-pct', pct(reg[0].marketplaceGoogle));
  set('regional-pior-cidade', reg[reg.length - 1].cidade);
  set('regional-pior-pct', pct(reg[reg.length - 1].marketplaceGoogle));
  chart('regional-bars', barChartSVG(reg.map((r, i) => ({
    label: r.cidade, value: r.marketplaceGoogle, highlight: i === 0,
  }))));

  // clímax: barras + seletor
  const list = especialidadesList(N);
  chart('esp-bars', barChartSVG(list.slice(0, 12).map((e) => ({
    label: e.nome, value: e.visivel, highlight: e.nome === 'Dermatologia',
  }))));
  const select = document.getElementById('esp-select');
  if (select) {
    select.innerHTML = list.map((e) => `<option>${e.nome}</option>`).join('');
    const update = () => {
      const v = specialtyValue(N, select.value);
      set('esp-out', v ? `Em ${select.value}, só <strong>${pct(v.visivel)}</strong> dos médicos aparecem na IA — <strong>${pct(v.invisivel)}</strong> são invisíveis.` : '');
    };
    select.addEventListener('change', update);
    select.value = 'Dermatologia'; update();
  }

  // oportunidade: índice de dor por especialidade
  set('oport-top', N.oportunidade[0].especialidade);
  chart('oport-bars', barChartSVG(N.oportunidade.slice(0, 12).map((o, i) => ({
    label: o.especialidade, value: o.scoreDor, highlight: i === 0,
  }))));

  // ressalvas
  set('ressalvas', (N.meta.ressalvas || []).map((r) => `<li>${r}</li>`).join(''));

  // captura -> bridge da mainpage (Slack)
  const form = document.getElementById('lead-form');
  const pdfWrap = document.getElementById('pdf-wrap');
  if (form) form.addEventListener('submit', async (ev) => {
    ev.preventDefault();
    const data = Object.fromEntries(new FormData(form).entries());
    let payload;
    try {
      payload = buildBridgePayload(data);
    } catch {
      set('form-msg', 'Esse e-mail parece incompleto — confere pra gente?');
      return;
    }
    set('form-msg', 'Enviando…');
    const res = await submitLead(payload);
    if (res.ok) {
      set('form-msg', 'Pronto! Seu diagnóstico está a caminho. O relatório completo está liberado aqui embaixo ⬇');
      if (pdfWrap) pdfWrap.hidden = false;
      form.reset();
    } else {
      set('form-msg', 'Algo falhou no envio. Tenta de novo em instantes?');
    }
  });
}).catch((e) => { document.body.insertAdjacentHTML('afterbegin',
  `<p style="color:red;padding:1rem">Erro ao carregar dados: ${e.message}</p>`); });
