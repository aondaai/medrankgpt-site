from __future__ import annotations
import httpx
from visibility.study.classify import classify_response

def extract_aio_text(ai_overview: dict) -> str:
    parts: list[str] = []
    for b in ai_overview.get("text_blocks", []) or []:
        if b.get("snippet"):
            parts.append(b["snippet"])
        for item in b.get("list", []) or []:
            if item.get("snippet"):
                parts.append(item["snippet"])
    return "\n".join(parts)

class SerpApiAIOClient:
    """Google AI Overview via SerpApi (best-effort; trata page_token e ausência)."""
    name = "google_ai"

    def __init__(self, api_key: str, get_json=None, timeout: float = 60.0):
        self.api_key = api_key
        self._client = httpx.Client(timeout=timeout)
        self._get = get_json or self._default_get

    def _default_get(self, params: dict) -> dict:
        r = self._client.get("https://serpapi.com/search.json", params=params)
        r.raise_for_status()
        return r.json()

    def fetch(self, query: str) -> dict:
        d = self._get({"engine": "google", "q": query, "hl": "pt-br", "gl": "br",
                       "google_domain": "google.com.br", "api_key": self.api_key})
        if d.get("error"):
            return {"presente": False, "sem_aio": True, "texto": "", "erro": d["error"]}
        ao = d.get("ai_overview")
        if not ao:
            return {"presente": False, "sem_aio": True, "texto": "", "erro": None}
        if ao.get("text_blocks"):
            return {"presente": True, "sem_aio": False, "texto": extract_aio_text(ao), "erro": None}
        if ao.get("page_token"):
            d2 = self._get({"engine": "google_ai_overview", "page_token": ao["page_token"],
                            "api_key": self.api_key})
            ao2 = d2.get("ai_overview", {}) or {}
            if d2.get("error") or not ao2.get("text_blocks"):
                return {"presente": False, "sem_aio": True, "texto": "", "erro": d2.get("error")}
            return {"presente": True, "sem_aio": False, "texto": extract_aio_text(ao2), "erro": None}
        return {"presente": False, "sem_aio": True, "texto": "", "erro": None}

def _safe_div(a, b): return a / b if b else 0.0

def aggregate_aio(records: list[dict]) -> dict:
    total = len(records)
    presentes = [r for r in records if r.get("presente")]
    n_sem = sum(1 for r in records if r.get("sem_aio"))
    cita_medico = 0
    marketplace = 0
    for r in presentes:
        c = classify_response(r.get("texto", ""))
        if c.tipo_resposta == "medico_nominal":
            cita_medico += 1
        elif c.tipo_resposta == "marketplace":
            marketplace += 1
    return {
        "total": total,
        "pct_presente": _safe_div(len(presentes), total),
        "pct_sem_aio": _safe_div(n_sem, total),
        "entre_presentes": {
            "n": len(presentes),
            "pct_cita_medico": _safe_div(cita_medico, len(presentes)),
            "pct_marketplace": _safe_div(marketplace, len(presentes)),
        },
    }
