from __future__ import annotations
import re
import httpx

_NAME_RE = re.compile(r'"name"\s*:\s*"(Dr[a]?\.?\s+[^"]{2,60})"')

def parse_doctoralia_names(html: str, max_n: int | None = None) -> list[str]:
    seen: list[str] = []
    for m in _NAME_RE.findall(html or ""):
        nome = re.sub(r"\s+", " ", m).strip()
        if nome not in seen:
            seen.append(nome)
        if max_n is not None and len(seen) >= max_n:
            break
    return seen

def doctoralia_url(praticante_slug: str, cidade_slug: str) -> str:
    return f"https://www.doctoralia.com.br/{praticante_slug}/{cidade_slug}"

def build_roster_entries(nomes: list[str], *, especialidade: str, cidade: str,
                         uf: str) -> list[dict]:
    return [{"nome": n, "especialidade_principal": especialidade,
             "cidade": cidade, "uf": uf} for n in nomes]

class DoctoraliaClient:
    """Fetch de página de listagem (só produção; não usado em teste)."""
    def __init__(self, timeout: float = 30.0):
        self._client = httpx.Client(timeout=timeout, follow_redirects=True, headers={
            "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                           "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36")})

    def listing_html(self, praticante_slug: str, cidade_slug: str) -> str:
        r = self._client.get(doctoralia_url(praticante_slug, cidade_slug))
        r.raise_for_status()
        return r.text
