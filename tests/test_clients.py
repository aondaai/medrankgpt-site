from visibility.clients import OpenAICompatibleClient


class _FakeResp:
    def raise_for_status(self): pass
    def json(self): return {"choices": [{"message": {"content": "oi"}}]}


class _FakePost:
    def __init__(self): self.captured = {}
    def post(self, url, json):
        self.captured["url"] = url
        self.captured["json"] = json
        return _FakeResp()


def test_extra_body_is_merged_into_request():
    c = OpenAICompatibleClient("chatgpt", "k", "gpt-4o-search-preview",
                               extra_body={"web_search_options": {}})
    fake = _FakePost()
    c._client = fake
    out = c.ask("Quem é o melhor dermatologista em SP?")
    assert out == "oi"
    body = fake.captured["json"]
    assert body["model"] == "gpt-4o-search-preview"
    assert body["web_search_options"] == {}
    assert body["messages"][0]["content"] == "Quem é o melhor dermatologista em SP?"


def test_no_extra_body_by_default():
    c = OpenAICompatibleClient("chatgpt", "k", "gpt-4o")
    fake = _FakePost()
    c._client = fake
    c.ask("oi")
    assert "web_search_options" not in fake.captured["json"]
