from archguard.llm import LLMJudgement, apply_llm_suggestion
from archguard.models import Finding, Status


def base_finding(status=Status.NOT_ENOUGH_INFORMATION):
    return Finding(requirement_id="R1", requirement_title="Test", category="Security",
                   status=status, confidence=0.8, reasoning="Missing evidence.",
                   risk="Risk", recommendation="Document it")


def test_unverifiable_conclusive_llm_claim_is_rejected():
    judgement = LLMJudgement(status=Status.COMPLIANT, confidence=0.95,
                             evidence_quote="mTLS everywhere", reasoning="Compliant",
                             recommendation="None")
    result = apply_llm_suggestion("No transport details.", base_finding(), judgement)
    assert result.status == Status.NOT_ENOUGH_INFORMATION
    assert "rejected" in result.source


def test_deterministic_contradiction_cannot_be_overridden():
    judgement = LLMJudgement(status=Status.COMPLIANT, confidence=0.9,
                             evidence_quote="control", reasoning="Compliant",
                             recommendation="None")
    finding = base_finding(Status.NON_COMPLIANT)
    assert apply_llm_suggestion("control", finding, judgement).status == Status.NON_COMPLIANT
