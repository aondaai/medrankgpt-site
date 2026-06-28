from visibility.assembler import assemble_report, CATEGORY_LABELS
from visibility.collectors.base import CollectorContext, CollectorOutput, SignalResult
from visibility.models import DoctorMeta, Status, PromptIA

class FakeCollector:
    def __init__(self, category, signals, prompts=None):
        self.category = category; self._signals = signals; self._prompts = prompts or []
    def collect(self, ctx) -> CollectorOutput:
        return CollectorOutput(signals=self._signals, prompts=self._prompts)

def _sr(id_, status, weight, cat_specific=True):
    return SignalResult(id_, id_, status, True, weight, 1.0, "m",
                        [{"fonte": "x", "resumo": "r"}])

def _doctor():
    return DoctorMeta(nome="Dra. Fulana", especialidade_principal="Dermatologia",
                      cidade="São Paulo", uf="SP")

def test_assemble_groups_scores_and_validates():
    collectors = [
        FakeCollector("busca_tradicional", [
            _sr("google_marca", Status.partial, 12.5), _sr("google_maps", Status.fail, 12.5)]),
        FakeCollector("visibilidade_ia",
            [_sr("ia_marca", Status.fail, 12.5), _sr("ia_procedimento", Status.fail, 12.5)],
            prompts=[PromptIA(id="p1", prompt="q", tipo="procedimento", engine="chatgpt",
                              medico_citado=False, concorrentes_citados=["Dr. X"])]),
    ]
    report = assemble_report(_doctor(), collectors, now="2026-06-28T14:00:00Z",
                             pipeline_version="0.1.0", regiao_busca="São Paulo, SP")
    assert report.categorias["busca_tradicional"].label == CATEGORY_LABELS["busca_tradicional"]
    assert report.categorias["busca_tradicional"].score == 6.25
    assert report.score.total == 6.25
    assert report.score.tier == "Bronze"
    assert report.concorrentes.ofensores_recorrentes[0].nome == "Dr. X"
    # serializes + validates against the schema
    from visibility.validation import validate_report
    validate_report(report.model_dump(mode="json", exclude_none=True))
