from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from archguard.metrics import evaluate_labels


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare architecture findings with expert reference labels")
    parser.add_argument("--predictions", required=True)
    parser.add_argument("--reference", required=True)
    parser.add_argument("--assisted-minutes", type=float)
    args = parser.parse_args()
    predicted_report = json.loads(Path(args.predictions).read_text(encoding="utf-8"))
    reference = json.loads(Path(args.reference).read_text(encoding="utf-8"))
    predictions = {item["requirement_id"]: item["status"] for item in predicted_report["findings"]}
    result = evaluate_labels(reference["labels"], predictions, reference.get("review_minutes"), args.assisted_minutes)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
