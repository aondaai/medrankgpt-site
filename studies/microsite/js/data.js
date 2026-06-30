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

export function normalizeData(raw) {
  const c2 = raw.camada2_visibilidade_ia;
  const porEspecialidade = {};
  for (const [esp, v] of Object.entries(c2.por_especialidade)) {
    porEspecialidade[esp] = { visivel: v.pct, invisivel: Math.round((1 - v.pct) * 10000) / 10000 };
  }
  return {
    ...deriveInsights(raw),
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
