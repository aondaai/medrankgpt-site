from __future__ import annotations
import argparse
import json
import sys
from datetime import datetime, timezone
from typing import Callable
from visibility.assembler import assemble_report
from visibility.config import Settings, build_collectors
from visibility.models import DoctorMeta
from visibility.validation import validate_report

def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def run(argv: list[str],
        collector_factory: Callable[[Settings], list] = build_collectors) -> int:
    parser = argparse.ArgumentParser(prog="medrank-visibility")
    parser.add_argument("--doctor", required=True, help="path to doctor input JSON")
    parser.add_argument("--out", help="output path (default: stdout)")
    parser.add_argument("--now", default=None, help="ISO timestamp override")
    parser.add_argument("--pipeline-version", default="0.1.0")
    args = parser.parse_args(argv)

    doctor = DoctorMeta.model_validate(json.loads(open(args.doctor, encoding="utf-8").read()))
    now = args.now or _utc_now()
    settings = Settings.from_env()
    collectors = collector_factory(settings)
    regiao = f"{doctor.cidade}, {doctor.uf}"
    report = assemble_report(doctor, collectors, now=now,
                             pipeline_version=args.pipeline_version, regiao_busca=regiao)
    data = report.model_dump(mode="json", exclude_none=True)
    validate_report(data)
    text = json.dumps(data, ensure_ascii=False, indent=2)
    if args.out:
        open(args.out, "w", encoding="utf-8").write(text)
    else:
        sys.stdout.write(text + "\n")
    return 0

def main() -> None:
    raise SystemExit(run(sys.argv[1:]))
