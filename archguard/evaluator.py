from __future__ import annotations

import re
from collections import Counter

from .models import AssessmentReport, Evidence, Finding, Requirement, Status
from .retrieval import RequirementRetriever


def _match_phrases(document: str, phrases: list[str], skip_negated: bool = False) -> list[Evidence]:
    evidence = []
    lowered = document.lower()
    for phrase in phrases:
        for match in re.finditer(re.escape(phrase.lower()), lowered):
            if skip_negated:
                prefix = lowered[max(0, match.start() - 45):match.start()]
                if re.search(r"\b(?:no|not|without|missing)\b|does not describe|is not documented", prefix):
                    continue
            left, right = max(0, match.start() - 90), min(len(document), match.end() + 90)
            excerpt = document[left:right].strip()
            if excerpt not in {item.excerpt for item in evidence}:
                evidence.append(Evidence(excerpt=excerpt, start=left, end=right))
    return evidence


def evaluate_requirement(document: str, requirement: Requirement) -> Finding:
    not_applicable = _match_phrases(document, requirement.not_applicable_any)
    contradictions = _match_phrases(document, requirement.contradiction_any)
    supporting = _match_phrases(document, requirement.evidence_any, skip_negated=True)

    # Applicability must be explicit in the architecture text. We do not infer
    # NOT_APPLICABLE merely because evidence is absent.
    if not_applicable:
        return Finding(
            requirement_id=requirement.id, requirement_title=requirement.title,
            category=requirement.category, status=Status.NOT_APPLICABLE, confidence=0.92,
            evidence=not_applicable,
            reasoning="The document explicitly states that this requirement is outside the declared system scope or that the relevant data/component is not present.",
            risk=requirement.risk,
            recommendation="Confirm the stated scope exclusion with the system owner and retain the justification for review.",
            requires_human_review=True)
    if contradictions:
        return Finding(
            requirement_id=requirement.id, requirement_title=requirement.title,
            category=requirement.category, status=Status.NON_COMPLIANT, confidence=0.94,
            evidence=contradictions,
            reasoning="The document explicitly describes a condition that conflicts with the requirement.",
            risk=requirement.risk, recommendation=requirement.recommendation,
            requires_human_review=True)
    if supporting:
        return Finding(
            requirement_id=requirement.id, requirement_title=requirement.title,
            category=requirement.category, status=Status.COMPLIANT, confidence=0.86,
            evidence=supporting,
            reasoning="The document contains explicit evidence matching the defined compliance criterion.",
            risk=requirement.risk, recommendation="Verify the stated control in implementation and operational evidence.",
            requires_human_review=True)
    return Finding(
        requirement_id=requirement.id, requirement_title=requirement.title,
        category=requirement.category, status=Status.NOT_ENOUGH_INFORMATION, confidence=0.78,
        evidence=[],
        reasoning="The document does not provide enough explicit evidence to confirm compliance and contains no explicit contradiction. This is a documentary gap, not proof of implementation failure.",
        risk=requirement.risk,
        recommendation=f"Document the relevant design decision and evidence. {requirement.recommendation}",
        requires_human_review=True)


def assess(document: str, requirements: list[Requirement], catalogue: dict | None = None,
           document_name: str = "architecture") -> AssessmentReport:
    catalogue = catalogue or {}
    retriever = RequirementRetriever(document)
    findings = []
    for requirement in requirements:
        finding = evaluate_requirement(document, requirement)
        if not finding.evidence:
            passages = retriever.retrieve(requirement, top_k=1)
            # Retrieved context is not treated as proof; it only helps human review.
            if passages and passages[0]["score"] >= 0.08:
                passage = passages[0]
                finding.evidence = [Evidence(excerpt=passage["text"], start=passage["start"], end=passage["end"])]
                finding.reasoning += " The most relevant passage is included for reviewer context but does not satisfy the criterion."
        findings.append(finding)
    counts = Counter(item.status.value for item in findings)
    summary = {status.value: counts.get(status.value, 0) for status in Status}
    return AssessmentReport(
        document_name=document_name,
        catalogue_name=catalogue.get("name", "Requirement catalogue"),
        catalogue_version=str(catalogue.get("version", "unknown")),
        findings=findings, summary=summary,
        warnings=["Synthetic requirements only; all findings require qualified human review."])
