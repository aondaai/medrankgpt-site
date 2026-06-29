from visibility.study.aio import extract_aio_text, SerpApiAIOClient, aggregate_aio

def test_extract_text_paragraph_e_lista():
    ao = {"text_blocks": [
        {"type": "paragraph", "snippet": "Para escolher um dermatologista:"},
        {"type": "list", "list": [{"snippet": "Verifique o CRM"}, {"snippet": "Leia avaliações"}]},
    ]}
    txt = extract_aio_text(ao)
    assert "Para escolher um dermatologista:" in txt
    assert "Verifique o CRM" in txt and "Leia avaliações" in txt

def test_fetch_sem_aio_quando_ausente():
    cli = SerpApiAIOClient("k", get_json=lambda params: {"organic_results": []})
    r = cli.fetch("melhor dermatologista em SP")
    assert r["presente"] is False and r["sem_aio"] is True and r["texto"] == ""

def test_fetch_presente_com_text_blocks_direto():
    payload = {"ai_overview": {"text_blocks": [{"type": "paragraph", "snippet": "A IA diz X"}]}}
    cli = SerpApiAIOClient("k", get_json=lambda params: payload)
    r = cli.fetch("q")
    assert r["presente"] is True and r["sem_aio"] is False
    assert r["texto"] == "A IA diz X"

def test_fetch_page_token_segue_para_segunda_chamada():
    calls = []
    def fake(params):
        calls.append(params.get("engine"))
        if params.get("engine") == "google":
            return {"ai_overview": {"page_token": "TOK"}}
        return {"ai_overview": {"text_blocks": [{"type": "paragraph", "snippet": "conteúdo final"}]}}
    cli = SerpApiAIOClient("k", get_json=fake)
    r = cli.fetch("q")
    assert calls == ["google", "google_ai_overview"]
    assert r["presente"] is True and r["texto"] == "conteúdo final"

def test_fetch_page_token_segunda_chamada_vazia_vira_sem_aio():
    def fake(params):
        if params.get("engine") == "google":
            return {"ai_overview": {"page_token": "TOK"}}
        return {"error": "Google hasn't returned any results for this query."}
    cli = SerpApiAIOClient("k", get_json=fake)
    r = cli.fetch("q")
    assert r["presente"] is False and r["sem_aio"] is True

def test_aggregate_aio():
    recs = [
        {"especialidade": "Dermatologia", "presente": True, "sem_aio": False, "texto": "A Dra. Ana Lima é ótima."},
        {"especialidade": "Dermatologia", "presente": False, "sem_aio": True, "texto": ""},
        {"especialidade": "Cardiologia", "presente": True, "sem_aio": False, "texto": "Busque no Doctoralia."},
    ]
    agg = aggregate_aio(recs)
    assert agg["total"] == 3
    assert round(agg["pct_sem_aio"], 3) == round(1/3, 3)
    assert round(agg["pct_presente"], 3) == round(2/3, 3)
    # entre os presentes (2): 1 cita médico, 1 marketplace
    assert round(agg["entre_presentes"]["pct_cita_medico"], 3) == 0.5
    assert round(agg["entre_presentes"]["pct_marketplace"], 3) == 0.5
