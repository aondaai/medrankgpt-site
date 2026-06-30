from __future__ import annotations
from collections import Counter
from urllib.parse import urlparse

# Domínios de marketplaces médicos (agregadores onde o paciente cai em vez do médico).
MARKETPLACES = ["doctoralia.", "boaconsulta.", "agendarconsulta.", "docplanner.", "bookingsaude."]
SOCIAL = ["instagram.com", "facebook.com", "linkedin.com", "youtube.com", "tiktok.com",
          "twitter.com", "x.com", "kwai.com"]
CONTEUDO = ["tuasaude.com", "minhavida.", "drauziovarella.", "saude.abril.", "vivabem.uol.",
            "biggera.", "mdsaude.", "veja.abril."]
INSTITUCIONAL = [".gov.br", "cfm.org", "sbd.org", "amb.org", "conselho"]

def _host(link: str) -> str:
    h = (urlparse(link).hostname or "").lower()
    return h[4:] if h.startswith("www.") else h

def classify_serp_item(link: str, title: str) -> str:
    host = _host(link)
    t = (title or "").lower()
    if any(m in host for m in MARKETPLACES):
        return "marketplace"
    if any(s in host for s in SOCIAL):
        return "social"
    if any(c in host for c in CONTEUDO):
        return "conteudo"
    if any(i in host for i in INSTITUCIONAL):
        return "institucional"
    if "hospital" in host or "hospital" in t:
        return "hospital"
    if "clinica" in host or "clínica" in t or "clinica" in t or "instituto" in host:
        return "clinica"
    # residual: provavelmente site do próprio médico ou outro — rotulado "outro" (honesto)
    return "outro"

def summarize_serp(items: list[dict], top_k: int = 10) -> dict:
    top = items[:top_k]
    cnt = Counter(classify_serp_item(i["link"], i.get("title", "")) for i in top)
    pos1 = classify_serp_item(top[0]["link"], top[0].get("title", "")) if top else None
    return {"n": len(top), "posicao_1_tipo": pos1, "por_tipo": dict(cnt)}
