from __future__ import annotations
import argparse
import json
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from typing import Callable
from visibility.config import Settings, build_engines, build_collectors
from visibility.models import VisibilityReport
from visibility.study.config import StudyConfig
from visibility.study.demand import build_demand_prompts, DemandRunner, DemandResponse
from visibility.study.supply import run_supply
from visibility.study.aggregate import aggregate_demand, aggregate_supply
from visibility.study.cost import (estimate_demand_calls, estimate_supply_calls,
                                   estimate_cost)
from visibility.study.export import build_aggregates, validate_aggregates

def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def _write(path: str | None, text: str) -> None:
    if path:
        open(path, "w", encoding="utf-8").write(text)
    else:
        sys.stdout.write(text + "\n")

def _cmd_plan(args) -> int:
    cfg = StudyConfig.from_file(args.config)
    n_demand = estimate_demand_calls(cfg.demand)
    supply = estimate_supply_calls(
        n_medicos=args.roster_size * max(len(cfg.rosters), 1),
        media_procedimentos=args.media_procedimentos, n_motores=len(cfg.demand.engines))
    custo = estimate_cost(llm=n_demand + supply["llm"],
                          serpapi=supply["serpapi"], places=supply["places"])
    print(f"Demanda: {n_demand} chamadas LLM")
    print(f"Oferta:  {supply['llm']} LLM + {supply['serpapi']} SerpApi + "
          f"{supply['places']} Places")
    print(f"Custo estimado: USD {custo:.2f}")
    return 0

def _cmd_demand(args, engines_factory) -> int:
    cfg = StudyConfig.from_file(args.config)
    now = args.now or _utc_now()
    engines = engines_factory(Settings.from_env())
    # respeita o subconjunto declarado na matriz
    engines = {k: v for k, v in engines.items() if k in cfg.demand.engines}
    prompts = build_demand_prompts(cfg.demand)
    responses = DemandRunner(engines=engines, repeticoes=cfg.demand.repeticoes).run(prompts, now)
    _write(args.out, json.dumps([asdict(r) for r in responses], ensure_ascii=False, indent=2))
    return 0

def _cmd_supply(args, collector_factory) -> int:
    cfg = StudyConfig.from_file(args.config)
    now = args.now or _utc_now()
    reports = run_supply(cfg.rosters, collector_factory=collector_factory,
                         settings=Settings.from_env(), now=now,
                         pipeline_version=args.pipeline_version)
    serial = {esp: [r.model_dump(mode="json", exclude_none=True) for r in rs]
              for esp, rs in reports.items()}
    _write(args.out, json.dumps(serial, ensure_ascii=False, indent=2))
    return 0

def _cmd_aggregate(args) -> int:
    now = args.now or _utc_now()
    demand_raw = json.loads(open(args.demand, encoding="utf-8").read())
    responses = [DemandResponse(**d) for d in demand_raw]
    supply_raw = json.loads(open(args.supply, encoding="utf-8").read())
    reports = {esp: [VisibilityReport.model_validate(r) for r in rs]
               for esp, rs in supply_raw.items()}
    demand_agg = aggregate_demand(responses)
    supply_agg = aggregate_supply(reports)
    data = build_aggregates(demand_agg, supply_agg, now=now,
                            pipeline_version=args.pipeline_version)
    validate_aggregates(data)
    _write(args.out, json.dumps(data, ensure_ascii=False, indent=2))
    return 0

def run(argv: list[str],
        engines_factory: Callable[[Settings], dict] = build_engines,
        collector_factory: Callable[[Settings], list] = build_collectors) -> int:
    parser = argparse.ArgumentParser(prog="medrank-study")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_plan = sub.add_parser("plan", help="estima chamadas e custo de API")
    p_plan.add_argument("--config", required=True)
    p_plan.add_argument("--roster-size", type=int, default=0,
                        help="médicos por roster (para estimar a oferta)")
    p_plan.add_argument("--media-procedimentos", type=int, default=4)

    p_dem = sub.add_parser("demand", help="roda os prompts de demanda")
    p_dem.add_argument("--config", required=True)
    p_dem.add_argument("--out")
    p_dem.add_argument("--now", default=None)

    p_sup = sub.add_parser("supply", help="roda o Visibility Score nos rosters")
    p_sup.add_argument("--config", required=True)
    p_sup.add_argument("--out")
    p_sup.add_argument("--now", default=None)
    p_sup.add_argument("--pipeline-version", default="0.1.0")

    p_agg = sub.add_parser("aggregate", help="agrega + valida o aggregates.json")
    p_agg.add_argument("--demand", required=True)
    p_agg.add_argument("--supply", required=True)
    p_agg.add_argument("--out")
    p_agg.add_argument("--now", default=None)
    p_agg.add_argument("--pipeline-version", default="0.1.0")

    args = parser.parse_args(argv)
    if args.cmd == "plan":
        return _cmd_plan(args)
    if args.cmd == "demand":
        return _cmd_demand(args, engines_factory)
    if args.cmd == "supply":
        return _cmd_supply(args, collector_factory)
    if args.cmd == "aggregate":
        return _cmd_aggregate(args)
    return 2

def main() -> None:
    raise SystemExit(run(sys.argv[1:]))


if __name__ == "__main__":
    main()
