from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from archguard.catalogue import load_catalogue
from archguard.evaluator import assess
from archguard.parser import parse_document
from archguard.reporting import write_csv, write_json


def main() -> None:
    parser = argparse.ArgumentParser(description="Assess architecture documentation")
    parser.add_argument("--document", required=True)
    parser.add_argument("--requirements", default="requirements/synthetic_mars.yaml")
    parser.add_argument("--output", default="reports/assessment.json")
    args = parser.parse_args()
    document = parse_document(args.document)
    metadata, requirements = load_catalogue(args.requirements)
    report = assess(document, requirements, metadata, Path(args.document).name)
    write_json(report, args.output)
    csv_path = str(Path(args.output).with_suffix(".csv"))
    write_csv(report, csv_path)
    print(f"Wrote {args.output} and {csv_path}")
    for status, count in report.summary.items():
        print(f"{status}: {count}")


if __name__ == "__main__":
    main()
