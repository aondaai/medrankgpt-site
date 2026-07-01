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

  // ---- 8. INVISIBILIDADE ----
  set('invisivel-2', pctInvisivel);
  const espList = especialidadesList(N); // asc por visível
  const espTop = espList[espList.length - 1]; // mais visível
  const espBot = espList[0];                  // mais invisível
  set('esp-top-nome', espTop.nome);
  set('esp-top-pct', pct(espTop.visivel));
  set('esp-bot-nome', espBot.nome);
  set('esp-bot-pct', pct(espBot.visivel));
  chart('esp-bars', barChartSVG(
    espList.slice(0, 12).map((e) => ({ label: e.nome, value: e.visivel, highlight: e.nome === espBot.nome })),
  ));
  const topMed = R.topMedicos[0];
  set('top-medico-nome', topMed[0]);
  set('top-medico-n', `${topMed[1]} vezes`);
  chart('top-medicos-bars', groupedBarSVG(
    R.topMedicos.map((m, i) => ({ label: m[0], value: m[1], highlight: i === 0 })),
    { fmt: (v) => `${v}×` },
  ));

  // ---- 9. ROLETA ----
  set('instab', pct(N.chatgpt.instabilidade));

  // ---- 10. OPORTUNIDADE ----
  set('oport-top', N.oportunidade[0].especialidade);
  chart('oport-bars', barChartSVG(
    N.oportunidade.slice(0, 12).map((o, i) => ({ label: o.especialidade, value: o.scoreDor, highlight: i === 0 })),
  ));

  // ---- 12. CONCLUSÕES ----
  set('conclusoes', [
    `A IA já recomenda médicos: o ChatGPT nomeia um médico em ${pct(R.citaMedicoGeral)} das respostas, e em ${pct(R.promptChatgpt.confianca)} quando a pergunta é de confiança.`,
    `A IA é segura o bastante para isso: só 0,28% das respostas trazem afirmação com risco-CFM.`,
    `A IA repete as fontes existentes: cita o Doctoralia como fonte em ${pct(N.chatgpt.doctoraliaFonte)} das vezes.`,
    `No Google, o marketplace fica no #1 em ${pct(N.serp.melhorMarketplacePos1)} das buscas por especialista — mas com só ${pct(R.shareMarketplaceMelhor)} do share da página.`,
    `O domínio do marketplace é regional: de ${pct(N.regional[0].marketplaceGoogle)} (${N.regional[0].cidade}) a ${pct(N.regional[N.regional.length - 1].marketplaceGoogle)} (${N.regional[N.regional.length - 1].cidade}).`,
    `Na busca por procedimento, o marketplace cai para ${pct(R.procMarketplacePos1)} dos #1 e o Instagram lidera — as propriedades próprias do médico competem.`,
    `O AI Overview é a superfície mais amigável ao médico (cita médico em ${pct(R.aio.citaMedicoPresente)}, marketplace em ${pct(R.aio.marketplacePresente)}) — e o Google a esconde em ${pct(R.aio.semAioMelhor)} das buscas por especialista.`,
    `${pctInvisivel} dos ${totalMed} médicos são invisíveis para a IA.`,
    `A visibilidade é desigual (${espTop.nome} ${pct(espTop.visivel)} vs ${espBot.nome} ${pct(espBot.visivel)}) e concentrada (${topMed[0]} citado ${topMed[1]}×).`,
    `A resposta da IA é instável (${pct(N.chatgpt.instabilidade)} muda): ser a resposta consistente, dentro do CFM, é a vantagem que o AEO constrói.`,
  ].map((t) => `<li>${t}</li>`).join(''));

  // ---- 13. APÊNDICE: TABELAS ----
  set('tabela-esp', tableHTML(
    ['Especialidade', 'Visível na IA', 'Marketplace #1', 'ChatGPT cita'],
    R.tabelaEsp.map((r) => [r.nome, pct(r.visivelIa), pct(r.marketplace1), pct(r.chatgptCita)]),
    { caption: 'Por especialidade (ordenado por visibilidade na IA)' },
  ));
  set('tabela-cidade', tableHTML(
    ['Capital', 'Marketplace #1', 'ChatGPT cita'],
    R.tabelaCidade.map((r) => [r.cidade, pct(r.marketplace1), pct(r.chatgptCita)]),
    { caption: 'Por capital (ordenado por domínio do marketplace)' },
  ));

  // ---- 14. RESSALVAS ----
  set('ressalvas', (N.meta.ressalvas || []).map((r) => `<li>${r}</li>`).join(''));

  window.__N = N; // facilita verificação no console
}).catch((e) => {
  document.body.insertAdjacentHTML('afterbegin',
    `<p style="color:red;padding:1rem">Erro ao carregar dados: ${e.message}</p>`);
});
