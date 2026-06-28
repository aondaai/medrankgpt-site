from __future__ import annotations
from typing import Protocol
import httpx

class HttpClient(Protocol):
    def get_text(self, url: str) -> str: ...

class HttpxClient:
    def __init__(self, timeout: float = 15.0):
        self._client = httpx.Client(timeout=timeout, follow_redirects=True,
                                    headers={"User-Agent": "MedRankGPT-VisibilityBot/0.1"})
    def get_text(self, url: str) -> str:
        r = self._client.get(url)
        r.raise_for_status()
        return r.text
