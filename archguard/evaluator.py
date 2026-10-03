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
                prefix = lowered