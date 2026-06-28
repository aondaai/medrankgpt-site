from visibility.config import Settings, build_engines

def test_engines_only_when_keys_present(monkeypatch):
    s = Settings(openai_api_key="x", gemini_api_key=None, perplexity_api_key=None)
    engines = build_engines(s)
    assert set(engines) == {"chatgpt"}

def test_all_engines(monkeypatch):
    s = Settings(openai_api_key="x", gemini_api_key="y", perplexity_api_key="z")
    engines = build_engines(s)
    assert set(engines) == {"chatgpt", "perplexity", "gemini", "google_ai"}

def test_from_env(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "abc")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    s = Settings.from_env()
    assert s.openai_api_key == "abc"
