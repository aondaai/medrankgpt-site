export function buildPayload(form, origem) {
  const nome = (form.nome || '').trim();
  const email = (form.email || '').trim().toLowerCase();
  if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) throw new Error('email inválido');
  return {
    nome, email, origem,
    especialidade: (form.especialidade || '').trim(),
    cidade: (form.cidade || '').trim(),
    capturado_em: new Date().toISOString(),
  };
}

// Endpoint do Google Sheet — definido na Frente 3. Vazio = modo log (não envia).
export const LEAD_ENDPOINT = '';

export async function submitLead(payload, endpoint = LEAD_ENDPOINT) {
  if (!endpoint) { console.info('[lead]', payload); return { ok: true, logged: true }; }
  const r = await fetch(endpoint, { method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload) });
  return { ok: r.ok };
}
