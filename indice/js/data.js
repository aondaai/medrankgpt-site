// derivados da "segunda leitura" — mesmos cortes de studies/derive_insights.py.
// score de dor = 0.6*(1-visível na IA) + 0.4*(marketplace no #1); composição editorial.
function deriveInsights(raw) {
  const serp = raw.google_serp, gpt = raw.chatgpt, cam = raw.camada2_visibilidade_ia;
  const gptCidade = (v) => typeof v === 'number' ? v : (v.pct_com_medico_nominal ?? v.pct_cita_medico ?? 0);
  const regional = Object.entries(serp.por_cidade)
    .map(([cidade, sv]) => ({ cidade, marketplaceGoogle: sv.pct_pos1_marketplace,
      citaChatgpt: gptCidade(gpt.por_cidade[cidade] ?? 0) }))
    .sort((a, b) => a.marketplaceGoogle - b.marketplaceGoogle);
  const oportunidade = Object.entries(cam.por_especialidade)
    .map(([especialidade, v]) => {
      const mkt = serp.por_especialidade[especialidade]?.pct_pos1_marketplace ?? 0;
      return { especialidade, visivelIa: v.pct, marketplaceGoogle: mkt,
        scoreDor: (1 - v.pct) * 0.6 + mkt * 0.4 };
    })
    .sort((a, b) => b.scoreDor - a.scoreDor);
  const tb = serp.por_tipo_busca;
  const virada = {
    melhorMarketplace: tb.melhor.pos1_por_tipo.marketplace ?? 0,
    melhorSocial: tb.melhor.pos1_por_tipo.social ?? 0,
    procMarketplace: tb.procedimento.pos1_por_tipo.marketplace ?? 0,
    procSocial: tb.procedimento.pos1_por_tipo.social ?? 0,
    melhorTop: tb.melhor.top_dominios_pos1[0],        // ['doctoralia.com.br', 160]
    procTop: tb.procedimento.top_dominios_pos1[0],    // ['instagram.com', 76]
  };
  return { regional, oportunidade, virada };
}

// Cortes extras só para o relatório longo. Aditivo: o microsite não lê nada disto.
function deriveReportInsights(raw) {
  const gpt = raw.chatgpt, serp = raw.google_serp, aio = raw.google_aio, cam = raw.camada2_visibilidade_ia;
  const tb = serp.por_tipo_busca;

  const chatgptPorEsp = Object.entries(gpt.por_especialidade)
    .map(([nome, v]) => ({ nome, cita: v.pct_cita_medico }))
    .sort((a, b) => a.cita - b.cita);

  // tabela por especialidade: visível IA · marketplace #1 Google · ChatGPT cita
  const tabelaEsp = Object.entries(cam.por_especialidade).map(([nome, v]) => ({
    nome,
    visivelIa: v.pct,
    marketplace1: serp.por_especialidade[nome]?.pct_pos1_marketplace ?? 0,
    chatgptCita: gpt.por_especialidade[nome]?.pct_cita_medico ?? 0,
  })).sort((a, b) => a.visivelIa - b.visivelIa);

  // tabela por capital: marketplace #1 · ChatGPT cita
  const tabelaCidade = Object.entries(serp.por_cidade).map(([cidade, v]) => ({
    cidade,
    marketplace1: v.pct_pos1_marketplace,
    chatgptCita: gpt.por_cidade[cidade]?.pct_cita_medico ?? 0,
  })).sort((a, b) => a.marketplace1 - b.marketplace1);

  return {
    promptChatgpt: {
      melhor: gpt.por_tipo_prompt.melhor_especialista,
      confianca: gpt.por_tipo_prompt.confianca,
      procedimento: gpt.por_tipo_prompt.procedimento,
    },
    cfmRisco: gpt.cfm_risco_pct,
    citaMedicoGeral: gpt.pct_cita_medico,
    shareMarketplaceMelhor: tb.melhor.share_medio_por_tipo.marketplace ?? 0,
    procInstagram: tb.procedimento.top_dominios_pos1.find(([d]) => d.includes('instagram')) ?? ['instagram.com', 0],
    procDoctoralia: tb.procedimento.top_dominios_pos1.find(([d]) => d.includes('doctoralia')) ?? ['doctoralia.com.br', 0],
    procSocialPos1: tb.procedimento.pos1_por_tipo.social ?? 0,
    procMarketplacePos1: tb.procedimento.pos1_por_tipo.marketplace ?? 0,
    aio: {
      presente: aio.pct_presente,
      semAio: aio.pct_sem_aio,
      semAioMelhor: aio.sem_aio_melhor,
      semAioProc: aio.sem_aio_procedimento,
      citaMedicoPresente: aio.entre_presentes.pct_cita_medico,
      marketplacePresente: aio.entre_presentes.pct_marketplace,
    },
    chatgptPorEsp,
    topMedicos: (gpt.top_medicos || []).slice(0, 8),
    tabelaEsp,
    tabelaCidade,
  };
}

export function normalizeData(raw) {
  const c2 = raw.camada2_visibilidade_ia;
  const porEspecialidade = {};
  for (const [esp, v] of Object.entries(c2.por_especialidade)) {
    porEspecialidade[esp] = { visivel: v.pct, invisivel: Math.round((1 - v.pct) * 10000) / 10000 };
  }
  return {
    ...deriveInsights(raw),
    reporte: deriveReportInsights(raw),
    hero: { pctInvisivel: c2.pct_invisivel_ia, totalMedicos: c2.total_medicos },
    meta: { especialidades: raw.meta.especialidades, capitais: raw.meta.capitais,
            ressalvas: raw.meta.ressalvas || [] },
    serp: {
      melhorMarketplacePos1: raw.google_serp.por_tipo_busca.melhor.pos1_por_tipo.marketplace || 0,
      procMarketplacePos1: raw.google_serp.por_tipo_busca.procedimento.pos1_por_tipo.marketplace || 0,
      topDominios: raw.google_serp.top_dominios_pos1.slice(0, 6),
    },
    chatgpt: {
      citaMedico: raw.chatgpt.pct_cita_medico,
      doctoraliaFonte: raw.chatgpt.doctoralia_como_fonte_pct,
      instabilidade: raw.chatgpt.instabilidade_pct_top_medico_muda,
    },
    aio: { semAio: raw.google_aio.pct_sem_aio, semAioMelhor: raw.google_aio.sem_aio_melhor },
    porEspecialidade,
  };
}

export async function loadData(url = './aggregates.json') {
  const r = await fetch(url);
  if (!r.ok) throw new Error(`falha ao carregar ${url}: ${r.status}`);
  return normalizeData(await r.json());
}
