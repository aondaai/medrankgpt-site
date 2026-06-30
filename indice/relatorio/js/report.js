import { loadData } from '../../js/data.js';
import { barChartSVG, donutSVG, groupedBarSVG, tableHTML } from '../../js/charts.js';
import { especialidadesList } from '../../js/specialty.js';

const pct = (v) => `${Math.round(v * 100 - 1e-9)}%`;
const set = (key, html) => { for (const el of document.querySelectorAll(`[data-fill="${key}"]`)) el.innerHTML = html; };
const chart = (key, svg) => { const el = document.querySelector(`[data-chart="${key}"]`); if (el) el.innerHTML = svg; };
const kpisHTML = (pairs) => pairs.map(([b, l]) => `<li><b>${b}</b><span>${l}</span></li>`).join('');

loadData('../aggregates.json').then((N) => {
  const R = N.reporte;
  const totalMed = N.hero.totalMedicos.toLocaleString('pt-BR');
  const pctInvisivel = pct(N.hero.pctInvisivel); // 0.8446 -> "84%"

  // ---- 1. SUMÁRIO EXECUTIVO ----
  set('n-medicos', totalMed);
  set('n-medicos-2', totalMed);
  set('n-medicos-3', totalMed);
  set('invisivel', pctInvisivel);
  set('kpis', kpisHTML([
    [pctInvisivel, 'médicos invisíveis para a IA'],
    [pct(R.citaMedicoGeral), 'das respostas citam um médico'],
    [pct(N.serp.melhorMarketplacePos1), 'das buscas: Doctoralia no #1'],
    [pct(N.chatgpt.instabilidade), 'das vezes a resposta muda'],
    [pct(R.aio.semAio), 'das buscas sem IA do Google'],
    [totalMed, 'médicos reais analisados'],
  ]));
  set('resumo-conclusoes', [
    `A IA já nomeia um médico em ${pct(R.citaMedicoGeral)} das respostas — o jogo é quem ela cita.`,
    `${pct(N.chatgpt.instabilidade)} das respostas mudam o médico recomendado: consistência é diferencial.`,
    `No Google, o Doctoralia fica no #1 em ${pct(N.serp.melhorMarketplacePos1)} das buscas por especialista.`,
    `Na busca por procedimento, propriedades próprias (site, Instagram) competem pelo #1.`,
    `${pctInvisivel} dos médicos são invisíveis para a IA — e os visíveis são poucos e concentrados.`,
  ].map((t) => `<li>${t}</li>`).join(''));

  // ---- 2. METODOLOGIA ----
  set('metodo-kpis', kpisHTML([
    [N.meta.especialidades, 'especialidades'],
    [N.meta.capitais, 'capitais'],
    ['3', 'superfícies de IA'],
  ]));

  // ---- 3. A IA JÁ NOMEIA E CONFIA ----
  set('cita-geral', pct(R.citaMedicoGeral));
  set('prompt-confianca', pct(R.promptChatgpt.confianca));
  set('cfm-risco', '0,28%');
  chart('prompt-bars', groupedBarSVG([
    { label: '"em quem confiar"', value: R.promptChatgpt.confianca, highlight: true },
    { label: '"melhor especialista"', value: R.promptChatgpt.melhor },
    { label: '"[procedimento]"', value: R.promptChatgpt.procedimento },
  ]));

  // ---- 4. FONTES ----
  set('doctoralia-fonte', pct(N.chatgpt.doctoraliaFonte));

  // ---- 5. GOOGLE: MARKETPLACE ----
  set('serp-melhor', pct(N.serp.melhorMarketplacePos1));
  set('serp-share', pct(R.shareMarketplaceMelhor));
  chart('serp-donut', donutSVG([
    { label: 'Doctoralia (#1)', value: N.serp.melhorMarketplacePos1, color: 'var(--viz-4)' },
    { label: 'resto', value: 1 - N.serp.melhorMarketplacePos1, color: 'var(--viz-1)' },
  ]));
  const reg = N.regional;
  set('regional-melhor-cidade', reg[0].cidade);
  set('regional-melhor-pct', pct(reg[0].marketplaceGoogle));
  set('regional-pior-cidade', reg[reg.length - 1].cidade);
  set('regional-pior-pct', pct(reg[reg.length - 1].marketplaceGoogle));
  chart('regional-bars', barChartSVG(reg.map((r, i) => ({
    label: r.cidade, value: r.marketplaceGoogle, highlight: i === 0,
  }))));

  // ---- 6. VIRADA DO PROCEDIMENTO ----
  set('proc-mkt', pct(R.procMarketplacePos1));
  set('proc-ig', `${R.procInstagram[1]}×`);
  set('proc-doc', `${R.procDoctoralia[1]}×`);
  set('proc-social', pct(R.procSocialPos1));
  const viradaDonut = (mkt, social) => donutSVG([
    { label: 'marketplace', value: mkt, color: 'var(--viz-4)' },
    { label: 'Instagram', value: social, color: 'var(--viz-2)' },
    { label: 'resto', value: Math.max(0, 1 - mkt - social), color: 'var(--viz-1)' },
  ]);
  chart('virada-melhor', viradaDonut(N.virada.melhorMarketplace, N.virada.melhorSocial));
  chart('virada-proc', viradaDonut(R.procMarketplacePos1, R.procSocialPos1));

  // ---- 7. AIO ----
  set('aio-sem', pct(R.aio.semAio));
  set('aio-sem-melhor', pct(R.aio.semAioMelhor));
  set('aio-sem-proc', pct(R.aio.semAioProc));
  set('aio-cita', pct(R.aio.citaMedicoPresente));
  set('aio-mkt', pct(R.aio.marketplacePresente));

  // (seções 8-14 na Task 7)
  window.__N = N; // facilita verificação no console
}).catch((e) => {
  document.body.insertAdjacentHTML('afterbegin',
    `<p style="color:red;padding:1rem">Erro ao carregar dados: ${e.message}</p>`);
});
