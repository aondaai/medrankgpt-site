from __future__ import annotations
import httpx

SERPER_URL = "https://google.serper.dev/search"

def parse_organic(payload: dict) -> list[dict]:
    out: list[dict] = []
    for o in payload.get("organic", []):
        out.append({"position": o.get("position"), "title": o.get("title", ""),
                    "link": o.get("link", "")})
    return out

class SerperClient:
    """Google organic SERP via Serper.dev. Retorna lista normalizada de orgânicos."""
    name = "google_serp"

    def __init__(self, api_key: str, gl: str = "br", hl: str = "pt-br", timeout: float = 60.0):
        self.gl = gl
        self.hl = hl
        self._client = httpx.Client(timeout=timeout,
            headers={"X-API-KEY": api_key, "Content-Type": "application/json"})

    def search(self, query: str, location: str | None = None) -> list[dict]:
        body = {"q": query, "gl": self.gl, "hl": self.hl}
        if location:
            body["location"] = location
        r = self._client.post(SERPER_URL, json=body)
        r.raise_for_status()
        return parse_organic(r.json())
