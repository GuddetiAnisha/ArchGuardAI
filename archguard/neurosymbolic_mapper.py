"""Research-mapping utilities for neuro-symbolic AI studies.

This extension supports systematic classification of structured paper metadata
for portfolio/research-prototyping use. It helps build a taxonomy, identify
coverage gaps, and map study concepts to user-supplied networking-standard
concepts.

It does NOT automatically conduct a systematic literature review, verify
citations, or claim completeness of the research landscape. The quality of the
output depends on the supplied study metadata and coding decisions.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

import pandas as pd


TAXONOMY_FIELDS = (
    "neural_component",
    "symbolic_component",
    "knowledge_representation",
    "reasoning_method",
    "autonomy_role",
    "networking_relevance",
    "evaluation_method",
    "security_relevance",
)


def _tokens(value) -> set[str]:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return set()
    if isinstance(value, str):
        normalized = value.replace(";", "|").replace(",", "|")
        return {x.strip() for x in normalized.split("|") if x.strip()}
    if isinstance(value, Iterable):
        return {str(x).strip() for x in value if str(x).strip()}
    return {str(value).strip()}


def validate_studies(studies: pd.DataFrame) -> pd.DataFrame:
    required = {"study_id", "title", "year", *TAXONOMY_FIELDS}
    missing = required - set(studies.columns)
    if missing:
        raise ValueError(f"missing columns: {sorted(missing)}")
    if studies["study_id"].astype(str).duplicated().any():
        raise ValueError("study_id values must be unique")
    if studies["study_id"].astype(str).str.strip().eq("").any():
        raise ValueError("study_id must not be blank")
    return studies.copy()


def build_taxonomy(studies: pd.DataFrame) -> pd.DataFrame:
    """Return category counts for each taxonomy dimension."""
    data = validate_studies(studies)
    rows = []
    for field in TAXONOMY_FIELDS:
        counts: dict[str, int] = {}
        for value in data[field]:
            for token in _tokens(value):
                counts[token] = counts.get(token, 0) + 1
        for category, count in sorted(counts.items(), key=lambda x: (-x[1], x[0].lower())):
            rows.append(
                {
                    "dimension": field,
                    "category": category,
                    "study_count": int(count),
                    "share_of_studies": float(count / len(data)) if len(data) else 0.0,
                }
            )
    return pd.DataFrame(rows)


def study_matrix(studies: pd.DataFrame) -> pd.DataFrame:
    """Create a human-reviewable study x taxonomy representation."""
    data = validate_studies(studies)
    rows = []
    for _, row in data.iterrows():
        record = {
            "study_id": str(row["study_id"]),
            "title": str(row["title"]),
            "year": int(row["year"]),
        }
        for field in TAXONOMY_FIELDS:
            record[field] = " | ".join(sorted(_tokens(row[field])))
        rows.append(record)
    return pd.DataFrame(rows)


def identify_research_gaps(
    studies: pd.DataFrame,
    dimensions: Sequence[str] = TAXONOMY_FIELDS,
    max_studies: int = 1,
) -> pd.DataFrame:
    """Flag sparsely represented coded categories.

    This is a descriptive coverage-gap heuristic, not proof that a genuine
    scientific research gap exists.
    """
    taxonomy = build_taxonomy(studies)
    taxonomy = taxonomy[taxonomy["dimension"].isin(dimensions)].copy()
    gaps = taxonomy[taxonomy["study_count"] <= max_studies].copy()
    gaps["gap_type"] = "sparse_in_supplied_corpus"
    return gaps.reset_index(drop=True)


def map_standards(
    studies: pd.DataFrame,
    standards: pd.DataFrame,
) -> pd.DataFrame:
    """Map studies to user-supplied standards concepts by explicit tags.

    Required standards columns:
      standard_id, concept, tags

    Study matching uses networking_relevance, autonomy_role, reasoning_method,
    and optional standards_tags if present.
    """
    data = validate_studies(studies)

    required = {"standard_id", "concept", "tags"}
    missing = required - set(standards.columns)
    if missing:
        raise ValueError(f"missing standards columns: {sorted(missing)}")

    rows = []
    for _, study in data.iterrows():
        study_tags = set()
        for field in ("networking_relevance", "autonomy_role", "reasoning_method"):
            study_tags |= {x.lower() for x in _tokens(study[field])}
        if "standards_tags" in data.columns:
            study_tags |= {x.lower() for x in _tokens(study.get("standards_tags"))}

        for _, standard in standards.iterrows():
            standard_tags = {x.lower() for x in _tokens(standard["tags"])}
            overlap = study_tags & standard_tags
            if overlap:
                rows.append(
                    {
                        "study_id": str(study["study_id"]),
                        "standard_id": str(standard["standard_id"]),
                        "standard_concept": str(standard["concept"]),
                        "matched_tags": " | ".join(sorted(overlap)),
                        "match_count": len(overlap),
                    }
                )

    return pd.DataFrame(
        rows,
        columns=[
            "study_id",
            "standard_id",
            "standard_concept",
            "matched_tags",
            "match_count",
        ],
    )


def summarize_mapping(
    studies: pd.DataFrame,
    standards: pd.DataFrame,
) -> dict:
    data = validate_studies(studies)
    mapped = map_standards(data, standards)
    mapped_studies = set(mapped["study_id"]) if len(mapped) else set()
    return {
        "studies": len(data),
        "taxonomy_dimensions": len(TAXONOMY_FIELDS),
        "standard_concepts": len(standards),
        "mapped_studies": len(mapped_studies),
        "unmapped_studies": len(data) - len(mapped_studies),
        "mapping_rows": len(mapped),
    }
