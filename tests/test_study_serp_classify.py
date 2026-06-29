from visibility.study.serp_classify import classify_serp_item, summarize_serp

def test_marketplace():
    assert classify_serp_item("https://www.doctoralia.com.br/dermatologista/sao-paulo", "Os 20 mais") == "marketplace"
    assert classify_serp_item("https://www.boaconsulta.com/x", "y") == "marketplace"

def test_social():
    assert classify_serp_item("https://www.instagram.com/dra.marina/", "Marina") == "social"

def test_conteudo():
    assert classify_serp_item("https://www.tuasaude.com/melasma/", "Melasma") == "conteudo"

def test_clinica_e_hospital():
    assert classify_serp_item("https://clinicaxyz.com.br", "Clínica XYZ") == "clinica"
    assert classify_serp_item("https://site.com", "Hospital Albert Einstein") == "hospital"

def test_institucional():
    assert classify_serp_item("https://portal.cfm.org.br", "CFM") == "institucional"

def test_outro_residual():
    assert classify_serp_item("https://drfulano.com.br", "Dr. Fulano") == "outro"

def test_summarize_conta_tipos_e_posicao1():
    items = [
        {"position": 1, "title": "Os 20 mais", "link": "https://www.doctoralia.com.br/x"},
        {"position": 2, "title": "Marina", "link": "https://www.instagram.com/dra.marina/"},
        {"position": 3, "title": "Clínica XYZ", "link": "https://clinicaxyz.com.br"},
    ]
    s = summarize_serp(items)
    assert s["n"] == 3
    assert s["posicao_1_tipo"] == "marketplace"
    assert s["por_tipo"]["marketplace"] == 1
    assert s["por_tipo"]["social"] == 1
    assert s["por_tipo"]["clinica"] == 1

def test_summarize_vazio():
    s = summarize_serp([])
    assert s["n"] == 0 and s["posicao_1_tipo"] is None and s["por_tipo"] == {}
