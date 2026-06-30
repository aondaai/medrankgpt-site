export function normalizeData(raw) {
  const c2 = raw.camada2_visibilidade_ia;
  const porEspecialidade = {};
  for (const [esp, v] of Object.entries(c2.por_especialidade)) {
    porEspecialidade[esp] = { visivel: v.pct, invisivel: Math.round((1 - v.pct) * 10000) / 10000 };
  }
  return {
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
