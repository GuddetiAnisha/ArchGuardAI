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


def test_explicit_scope_exclusion_is_not_applicable():
    _, items = requirements()
    requirement = next(item for item in items if item.id == "SYN-PRIV-008")
    finding = evaluate_requirement("The system processes no personal or sensitive data.", requirement)
    assert finding.status == Status.NOT_APPLICABLE
    assert finding.evidence


def test_balanced_four_class_scenario():
    metadata, items = requirements()
    document = parse_document(ROOT / "examples/four_class_architecture.md")
    report = assess(document, items, metadata)
    labels = {item.requirement_id: item.status for item in report.findings}

    expected = {
        "SYN-AUTH-001": Status.COMPLIANT,
        "SYN-AUTHZ-002": Status.NON_COMPLIANT,
        "SYN-DATA-003": Status.COMPLIANT,
        "SYN-DATA-004": Status.NON_COMPLIANT,
        "SYN-SECRET-005": Status.NOT_ENOUGH_INFORMATION,
        "SYN-LOG-006": Status.NOT_APPLICABLE,
        "SYN-RES-007": Status.NOT_ENOUGH_INFORMATION,
        "SYN-PRIV-008": Status.NOT_APPLICABLE,
    }

    assert labels == expected
    assert report.summary == {
        "COMPLIANT": 2,
        "NON_COMPLIANT": 2,
        "NOT_ENOUGH_INFORMATION": 2,
        "NOT_APPLICABLE": 2,
    }
