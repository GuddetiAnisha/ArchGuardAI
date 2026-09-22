from pathlib import Path

from archguard.catalogue import load_catalogue
from archguard.evaluator import assess, evaluate_requirement
from archguard.models import Status
from archguard.parser import parse_document


ROOT = Path(__file__).resolve().parents[1]


def requirements():
    return load_catalogue(ROOT / "requirements/synthetic_mars.yaml")


def test_example_matches_expert_reference():
    metadata, items = requirements()
    document = parse_document(ROOT / "examples/sample_architecture.md")
    report = assess(document, items, metadata)
    labels = {item.requirement_id: item.status for item in report.findings}
    assert labels["SYN-AUTH-001"] == Status.COMPLIANT
    assert labels["SYN-PRIV-008"] == Status.NOT_ENOUGH_INFORMATION


def test_explicit_contradiction_is_non_compliant():
    _, items = requirements()
    requirement = next(item for item in items if item.id == "SYN-SECRET-005")
    finding = evaluate_requirement("The service uses a hard-coded password in source code.", requirement)
    assert finding.status == Status.NON_COMPLIANT
    assert finding.evidence


def test_missing_evidence_is_not_a_violation():
    _, items = requirements()
    requirement = next(item for item in items if item.id == "SYN-DATA-004")
    finding = evaluate_requirement("The system has an API and a database.", requirement)
    assert finding.status == Status.NOT_ENOUGH_INFORMATION
