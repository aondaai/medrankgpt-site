export function buildBridgePayload(form) {
  const nome = (form.nome || '').trim();
  const email = (form.email || '').trim().toLowerCase();
  if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) throw new Error('email inválido');
  const especialidade = (form.especialidade || '').trim();
  const cidade = (form.cidade || '').trim();
  return {
    nome,
    email,
    telefone: (form.telefone || '').trim(),
    perfil: 'Índice MedRank 2026',
    especialidade: cidade ? `${especialidade} — ${cidade}` : especialidade,
  };
}

// Bridge de leads da mainpage (posta no Slack #medrankgpt). Segredo fica no bridge.
export const LEAD_ENDPOINT = 'https://mainline-finance.onrender.com/api/medrank-lead';

export async function submitLead(payload, endpoint = LEAD_ENDPOINT) {
  try {
    const r = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
      body: JSON.stringify(payload),
    });
    return { ok: r.ok };
  } catch {
    return { ok: false };
  }
}
