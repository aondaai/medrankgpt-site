from visibility.study.config import DemandMatrix
from visibility.study.serp import (build_serp_queries, run_serp, aggregate_serp,
                                    SerpRecord, SerpAggregate)

def _matrix():
    return DemandMatrix(
        especialidades=["Dermatologia", "Cardiologia"],
        cidades=["São Paulo"],
        procedimentos={"Dermatologia": ["botox"], "Cardiologia": []},
        prompt_tipos=["melhor_especialista", "procedimento"],
        engines=["google_serp"], repeticoes=1)

def test_build_serp_queries_usa_praticante_e_fallback():
    qs = build_serp_queries(_matrix(), praticantes={"Dermatologia": "dermatologista"})
    qmap = {q["query"] for q in qs}
    # Dermatologia tem praticante + 1 procedimento; Cardiologia cai no fallback, sem procedimento
    assert "melhor dermatologista em São Paulo" in qmap
    assert "botox em São Paulo" in qmap
    assert "melhor Cardiologia em São Paulo" in qmap   # fallback p/ nome da especialidade
    # 'melhor' (1 por esp) + procedimentos (1 derm, 0 cardio) = 2 + 1 = 3
    assert len(qs) == 3

class FakeSerper:
    """Devolve uma SERP canônica por substring da query."""
    def __init__(self, mapa): self.mapa = mapa
    def search(self, query, location=None):
        for needle, items in self.mapa.items():
            if needle in query:
                return items
        return []

def test_run_serp_monta_records():
    derm = [{"position":1,"title":"Os mais","link":"https://www.doctoralia.com.br/dermatologista/sao-paulo"},
            {"position":2,"title":"Dra","link":"https://www.instagram.com/dra.x/"}]
    cli = FakeSerper({"dermatologista": derm})
    qs = [q for q in build_serp_queries(_matrix(), {"Dermatologia":"dermatologista"})
          if "dermatologista" in q["query"]]
    recs = run_serp(qs, cli, now="2026-06-28T15:00:00Z")
    assert len(recs) == 1
    r = recs[0]
    assert isinstance(r, SerpRecord)
    assert r.posicao_1_tipo == "marketplace"
    assert r.por_tipo["marketplace"] == 1 and r.por_tipo["social"] == 1
    assert r.dominios[0]["tipo"] == "marketplace"

def _rec(esp, cidade, pos1, por_tipo, link1):
    return SerpRecord(esp, cidade, "melhor", None, "q", "t", pos1, por_tipo,
                      [{"position":1,"tipo":pos1,"link":link1}])

def test_aggregate_serp():
    recs = [
        _rec("Dermatologia","SP","marketplace",{"marketplace":1,"outro":1},"https://www.doctoralia.com.br/a"),
        _rec("Dermatologia","RJ","outro",{"outro":2},"https://drfulano.com.br"),
        _rec("Cardiologia","SP","marketplace",{"marketplace":1},"https://www.doctoralia.com.br/b"),
    ]
    agg = aggregate_serp(recs)
    assert isinstance(agg, SerpAggregate)
    assert agg.total_queries == 3
    assert round(agg.pos1_por_tipo["marketplace"], 3) == round(2/3, 3)
    assert agg.por_especialidade["Dermatologia"]["pct_pos1_marketplace"] == 0.5
    assert agg.por_cidade["SP"]["pct_pos1_marketplace"] == 1.0
    assert agg.top_dominios_pos1[0] == ["doctoralia.com.br", 2]
