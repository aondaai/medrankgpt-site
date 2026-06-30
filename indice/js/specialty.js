export function especialidadesList(norm) {
  return Object.entries(norm.porEspecialidade)
    .map(([nome, v]) => ({ nome, visivel: v.visivel, invisivel: v.invisivel }))
    .sort((a, b) => a.visivel - b.visivel);
}

export function specialtyValue(norm, especialidade) {
  const v = norm.porEspecialidade[especialidade];
  return v ? { visivel: v.visivel, invisivel: v.invisivel } : null;
}
