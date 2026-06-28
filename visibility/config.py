from __future__ import annotations
import os
from dataclasses import dataclass
from visibility.clients import (
    HttpxClient, SerpApiClient, GooglePlacesClient,
    OpenAICompatibleClient, GeminiClient, LLMClient,
)
from visibility.collectors.site_analysis import SiteAnalysisCollector
from visibility.collectors.google_search import GoogleSearchCollector
from visibility.collectors.google_maps import GoogleMapsCollector
from visibility.collectors.medical_platforms import MedicalPlatformsCollector
from visibility.collectors.ai_engines import AiEnginesCollector

@dataclass
class Settings:
    serpapi_key: str | None = None
    google_places_key: str | None = None
    openai_api_key: str | None = None
    perplexity_api_key: str | None = None
    gemini_api_key: str | None = None

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            serpapi_key=os.getenv("SERPAPI_KEY"),
            google_places_key=os.getenv("GOOGLE_PLACES_KEY"),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            perplexity_api_key=os.getenv("PERPLEXITY_API_KEY"),
            gemini_api_key=os.getenv("GEMINI_API_KEY"),
        )

def build_engines(s: Settings) -> dict[str, LLMClient]:
    engines: dict[str, LLMClient] = {}
    if s.openai_api_key:
        engines["chatgpt"] = OpenAICompatibleClient("chatgpt", s.openai_api_key, "gpt-4o")
    if s.perplexity_api_key:
        engines["perplexity"] = OpenAICompatibleClient(
            "perplexity", s.perplexity_api_key, "sonar",
            base_url="https://api.perplexity.ai")
    if s.gemini_api_key:
        engines["gemini"] = GeminiClient("gemini", s.gemini_api_key)
        engines["google_ai"] = GeminiClient("google_ai", s.gemini_api_key)
    return engines

def build_collectors(s: Settings) -> list:
    http = HttpxClient()
    collectors: list = [
        SiteAnalysisCollector(http=http),
        MedicalPlatformsCollector(http=http),
        AiEnginesCollector(engines=build_engines(s)),
    ]
    if s.serpapi_key:
        collectors.append(GoogleSearchCollector(search=SerpApiClient(s.serpapi_key)))
    if s.google_places_key:
        collectors.append(GoogleMapsCollector(places=GooglePlacesClient(s.google_places_key)))
    return collectors
