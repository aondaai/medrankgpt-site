from visibility.study.serper import parse_organic

def test_parse_organic_normaliza():
    payload = {"organic": [
        {"position": 1, "title": "A", "link": "https://doctoralia.com.br/x", "snippet": "..."},
        {"position": 2, "title": "B", "link": "https://instagram.com/y"},
    ], "credits": 1}
    out = parse_organic(payload)
    assert out == [
        {"position": 1, "title": "A", "link": "https://doctoralia.com.br/x"},
        {"position": 2, "title": "B", "link": "https://instagram.com/y"},
    ]

def test_parse_organic_vazio():
    assert parse_organic({}) == []
