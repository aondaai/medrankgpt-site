#!/usr/bin/env python3
"""Deriva cortes cruzados do aggregates.json para o microsite/PDF.

Não coleta nada: lê o agregado existente e produz dados prontos para tabelas e
gráficos (regional, mapa de oportunidade, melhor-vs-procedimento, AIO presente,
share da 1ª página). Reproduz a "segunda leitura" em JSON/CSV consumíveis.

    python3 studies/derive_insights.py            # usa studies/results/aggregates.json
    python3 studies/derive_insights.py <agg.json> # fonte alternativa
"""
from __future__ import annotations
import csv
import json
import sys
from pathlib import Path

RESULTS = Path(__file__).resolve().parent / "results"


def derive(agg: dict) -> dict:
    serp = agg["google_serp"]
    gpt = agg["chatgpt"]
    cam = agg["camada2_visibilidade_ia"]["por_especialidade"]
    aio = agg["google_aio"]

    def gpt_cidade(v):  # por_cidade pode ser float ou dict
        if isinstance(v, (int, float)):
            return v
        return v.get("pct_com_medico_nominal") or v.get("pct_cita_medico") or 0

    # 1. regional: Google espreme desigual, ChatGPT uniforme
    regional = []
    for cidade, sv in serp["por_cidade"].items():
        regional.append({
            "cidade": cidade,
            "marketplace_pos1_google": sv["pct_pos1_marketplace"],
            "cita_medico_chatgpt": gpt_cidade(gpt["por_cidade"].get(cidade, 0)),
        })
    regional.sort(key=lambda r: r["marketplace_pos1_google"])

    # 2. mapa de oportunidade: invisibilidade na IA x marketplace no Google.
    # score editorial 60/40 (declarado, não é métrica do engine).
    oportunidade = []
    for esp, v in cam.items():
        vis = v["pct"]
        mkt = serp["por_especialidade"].get(esp, {}).get("pct_pos1_marketplace", 0)
        oportunidade.append({
            "especialidade": esp,
            "visivel_ia": vis,
            "marketplace_pos1_google": mkt,
            "n_medicos": v["n"],
            "score_dor": round((1 - vis) * 0.6 + mkt * 0.4, 4),
        })
    oportunidade.sort(key=lambda r: r["score_dor"], reverse=True)

    # 3. melhor vs procedimento: jogos opostos no #1
    def tipo_busca(t):
        b = serp["por_tipo_busca"][t]
        return {
            "n": b["total"],
            "pos1_por_tipo": b["pos1_por_tipo"],
            "share_medio_por_tipo": b["share_medio_por_tipo"],
            "top_dominios_pos1": b["top_dominios_pos1"][:6],
        }

    return {
        "fonte": "derivado de aggregates.json (sem nova coleta)",
        "gerado_de": agg["meta"]["gerado_em"],
        "ressalva_score_dor": "score_dor = 0.6*(1-visivel_ia) + 0.4*marketplace_pos1; "
                              "composição editorial, não métrica do engine.",
        "regional": regional,
        "oportunidade": oportunidade,
        "melhor_vs_procedimento": {
            "melhor": tipo_busca("melhor"),
            "procedimento": tipo_busca("procedimento"),
        },
        "aio_presente": {
            "pct_sem_aio": aio["pct_sem_aio"],
            "sem_aio_melhor": aio["sem_aio_melhor"],
            "entre_presentes": aio["entre_presentes"],
        },
        "top_medicos_ia": gpt["top_medicos"][:10],
    }


def write_csvs(d: dict) -> list[Path]:
    out = []
    p = RESULTS / "insights-regional.csv"
    with p.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["cidade", "marketplace_pos1_google", "cita_medico_chatgpt"])
        for r in d["regional"]:
            w.writerow([r["cidade"], r["marketplace_pos1_google"], r["cita_medico_chatgpt"]])
    out.append(p)

    p = RESULTS / "insights-oportunidade.csv"
    with p.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["especialidade", "visivel_ia", "marketplace_pos1_google",
                    "n_medicos", "score_dor"])
        for r in d["oportunidade"]:
            w.writerow([r["especialidade"], r["visivel_ia"], r["marketplace_pos1_google"],
                        r["n_medicos"], r["score_dor"]])
    out.append(p)
    return out


def main() -> None:
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else RESULTS / "aggregates.json"
    agg = json.loads(src.read_text())
    derived = derive(agg)
    out_json = RESULTS / "insights-derivados.json"
    out_json.write_text(json.dumps(derived, ensure_ascii=False, indent=2) + "\n")
    csvs = write_csvs(derived)
    print(f"✓ {out_json.relative_to(RESULTS.parent)}")
    for c in csvs:
        print(f"✓ {c.relative_to(RESULTS.parent)}")


if __name__ == "__main__":
    main()
