from __future__ import annotations
import re
from dataclasses import dataclass, field
from visibility.names import mentioned_names

# id canônico -> variações textuais (lowercase, sem exigir acento exato)
MARKETPLACES: dict[str, list[str]] = {
    "doctoralia": ["doctoralia"],
    "boaconsulta": ["boaconsulta", "boa consulta"],
    "google_maps": ["google maps", "google meu negócio", "google meu negocio"],
}

_RECUSA = re.compile(
    r"não (tenho|possuo|disponho)|nao (tenho|possuo)|não posso recomendar|"
    r"nao posso recomendar|sem informaç|sem informac", re.IGNORECASE)
_HOSPITAL = re.compile(r"\bhospital\b", re.IGNORECASE)
_CLINICA = re.compile(r"\bcl[íi]nica", re.IGNORECASE)

# Frases que sinalizam possível violação do CFM (heurística; confirmação por LLM é etapa futura).
CFM_FRASES_RISCO: list[re.Pattern] = [
    re.compile(r"resultado[s]? garantido", re.IGNORECASE),
    re.compile(r"cura (total|garantida)", re.IGNORECASE),
    re.compile(r"garante (o|a|um|uma)?\s*(resultado|cura|sucesso)", re.IGNORECASE),
    re.compile(r"100\s*%\s*(indolor|seguro|eficaz|garantido)", re.IGNORECASE),
    re.compile(r"\bindolor\b", re.IGNORECASE),
    re.compile(r"sem (riscos|dor|cicatriz)", re.IGNORECASE),
    re.compile(r"\bmilagr", re.IGNORECASE),
    # superlativo com escopo geográfico (vedado quando afirma "o melhor da cidade/estado/país")
    re.compile(r"melhor\s+\w+\s+d[oa]\s+(brasil|cidade|estado|pa[íi]s|mundo)", re.IGNORECASE),
]

@dataclass
class ResponseClassification:
    tipo_resposta: str                 # medico_nominal|marketplace|hospital|clinica|conteudo_generico|nenhum
    medicos: list[str] = field(default_factory=list)
    marketplaces: list[str] = field(default_factory=list)
    tem_clinica: bool = False
    tem_hospital: bool = False
    cfm_risco: list[str] = field(default_factory=list)

def _norm(s: str) -> str:
    return s.lower()

def _marketplaces_in(text: str) -> list[str]:
    low = _norm(text)
    out: list[str] = []
    for mid, variants in MARKETPLACES.items():
        if any(v in low for v in variants) and mid not in out:
            out.append(mid)
    return out

def cfm_risk(texto: str) -> list[str]:
    achados: list[str] = []
    for pat in CFM_FRASES_RISCO:
        m = pat.search(texto)
        if m:
            achados.append(m.group(0).strip().lower())
    return achados

def classify_response(texto: str) -> ResponseClassification:
    medicos = mentioned_names(texto)
    marketplaces = _marketplaces_in(texto)
    tem_hospital = bool(_HOSPITAL.search(texto))
    tem_clinica = bool(_CLINICA.search(texto))
    recusa = bool(_RECUSA.search(texto))

    if medicos:
        tipo = "medico_nominal"
    elif marketplaces:
        tipo = "marketplace"
    elif tem_hospital:
        tipo = "hospital"
    elif tem_clinica:
        tipo = "clinica"
    elif recusa:
        tipo = "nenhum"
    else:
        tipo = "conteudo_generico"

    cfm = cfm_risk(texto)
    return ResponseClassification(
        tipo_resposta=tipo, medicos=medicos, marketplaces=marketplaces,
        tem_clinica=tem_clinica, tem_hospital=tem_hospital, cfm_risco=cfm)
