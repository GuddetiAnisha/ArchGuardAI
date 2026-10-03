from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field, field_validator


class Status(str, Enum):
    COMPLIANT = "COMPLIANT"
    NON_COMPLIANT = "NON_COMPLIANT"
    NOT_ENOUGH_INFORMATION = "NOT_ENOUGH_INFORMATION"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class Requirement(BaseModel):
    id: str
    title: str
    category: str
    statement: str
    risk: str
    recommendation: str
    evidence_any: list[str] = Field(default_factory=list)
    contradiction_any: list[str] = Field(default_factory=list)
    not_applicable_any: list[str] = Field(default_factory=list)


class Evidence(BaseModel):
    excerpt: str
    start: int
    end: int


class Finding(BaseModel):
    requirement_id: str
    requirement_title: str
    category: str
    status: Status
    confidence: float = Field(ge=0, le=1)
    evidence: list[Evidence] = Field(default_factory=list)
    reasoning: str
    risk: str
    recommendation: str
    source: str = "deterministic"
    requires_human_review: bool = True

    @field_validator("reasoning")
    @classmethod
    def reasoning_not_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("reasoning must not be empty")
        return value


class AssessmentReport(BaseModel):
    document_name: str
    catalogue_name: str
    catalogue_version: str
    findings: list[Finding]
    summary: dict[str, int]
    warnings: list[str] = Field(default_factory=list)
