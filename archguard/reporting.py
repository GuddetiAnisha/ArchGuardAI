from __future__ import annotations

import csv
import json
from pathlib import Path

from .models import AssessmentReport


def write_json(report: AssessmentReport, path: str | Path) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report.model_dump(mode="json"), indent=2), encoding="utf-8")


def write_csv(report: AssessmentReport, path: str | Path) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["requirement_id", "title", "category", "status",
                                                        "confidence", "reasoning", "risk", "recommendation",
                                                        "evidence", "source", "requires_human_review"])
        writer.writeheader()
        for finding in report.findings:
            writer.writerow({"requirement_id": finding.requirement_id,
                             "title": finding.requirement_title, "category": finding.category,
                             "status": finding.status.value, "confidence": finding.confidence,
                             "reasoning": finding.reasoning, "risk": finding.risk,
                             "recommendation": finding.recommendation,
                             "evidence": " | ".join(item.excerpt for item in finding.evidence),
                             "source": finding.source,
                             "requires_human_review": finding.requires_human_review})
