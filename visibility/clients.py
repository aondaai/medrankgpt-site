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

class PlacesClient(Protocol):
    def text_search(self, query: str) -> dict: ...

class GooglePlacesClient:
    def __init__(self, api_key: str, timeout: float = 20.0):
        self.api_key = api_key
        self._client = httpx.Client(timeout=timeout)
    def text_search(self, query: str) -> dict:
        r = self._client.get(
            "https://maps.googleapis.com/maps/api/place/textsearch/json",
            params={"query": query, "key": self.api_key, "language": "pt-BR"})
        r.raise_for_status()
        return r.json()

class LLMClient(Protocol):
    name: str
    def ask(self, prompt: str) -> str: ...

class OpenAICompatibleClient:
    """Works for OpenAI (chatgpt) and Perplexity — same chat-completions shape.
    `extra_body` is merged into the request (e.g. {"web_search_options": {}} to enable
    browsing with gpt-4o-search-preview)."""
    def __init__(self, name: str, api_key: str, model: str,
                 base_url: str = "https://api.openai.com/v1", timeout: float = 60.0,
                 extra_body: dict | None = None):
        self.name = name; self.model = model; self.base_url = base_url.rstrip("/")
        self.extra_body = extra_body or {}
        self._client = httpx.Client(timeout=timeout,
                                    headers={"Authorization": f"Bearer {api_key}"})
    def ask(self, prompt: str) -> str:
        body = {"model": self.model, "messages": [{"role": "user", "content": prompt}],
                **self.extra_body}
        r = self._client.post(f"{self.base_url}/chat/completions", json=body)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]

class GeminiClient:
    def __init__(self, name: str, api_key: str, model: str = "gemini-1.5-pro",
                 timeout: float = 60.0):
        self.name = name; self.model = model; self.api_key = api_key
        self._client = httpx.Client(timeout=timeout)
    def ask(self, prompt: str) -> str:
        r = self._client.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent",
            params={"key": self.api_key},
            json={"contents": [{"parts": [{"text": prompt}]}]})
        r.raise_for_status()
        return r.json()["candidates"][0]["content"]["parts"][0]["text"]
