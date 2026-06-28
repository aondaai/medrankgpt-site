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

class SearchClient(Protocol):
    def search(self, query: str, location: str | None = None) -> dict: ...

class SerpApiClient:
    def __init__(self, api_key: str, timeout: float = 20.0):
        self.api_key = api_key
        self._client = httpx.Client(timeout=timeout)
    def search(self, query: str, location: str | None = None) -> dict:
        params = {"engine": "google", "q": query, "api_key": self.api_key,
                  "hl": "pt-br", "google_domain": "google.com.br", "num": 10}
        if location:
            params["location"] = location
        r = self._client.get("https://serpapi.com/search.json", params=params)
        r.raise_for_status()
        return r.json()
