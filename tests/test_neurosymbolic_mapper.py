import pandas as pd

from archguard.neurosymbolic_mapper import (
    build_taxonomy,
    identify_research_gaps,
    map_standards,
    study_matrix,
    summarize_mapping,
)


def sample_studies():
    return pd.DataFrame(
        [
            {
                "study_id": "S1",
                "title": "Neural-symbolic intent interpretation",
                "year": 2024,
                "neural_component": "Transformer",
                "symbolic_component": "Rules",
                "knowledge_representation": "Knowledge graph",
                "reasoning_method": "Rule reasoning",
                "autonomy_role": "Intent translation",
                "networking_relevance": "Intent-based networking",
                "evaluation_method": "Accuracy|Latency",
                "security_relevance": "Policy compliance",
                "standards_tags": "intent|policy",
            },
            {
                "study_id": "S2",
                "title": "Constraint-aware autonomous control",
                "year": 2025,
                "neural_component": "Neural policy",
                "symbolic_component": "Constraints",
                "knowledge_representation": "State machine",
                "reasoning_method": "Constraint checking",
                "autonomy_role": "Closed-loop control",
                "networking_relevance": "Autonomous networking",
                "evaluation_method": "Simulation",
                "security_relevance": "Safety constraints",
                "standards_tags": "closed-loop|autonomy",
            },
            {
                "study_id": "S3",
                "title": "Rule-guided intent assurance",
                "year": 2025,
                "neural_component": "Transformer",
                "symbolic_component": "Rules",
                "knowledge_representation": "Knowledge graph",
                "reasoning_method": "Rule reasoning",
                "autonomy_role": "Intent translation",
                "networking_relevance": "Intent-based networking",
                "evaluation_method": "Accuracy",
                "security_relevance": "Policy compliance",
                "standards_tags": "intent|policy",
            },
        ]
    )


def sample_standards():
    return pd.DataFrame(
        [
            {"standard_id": "STD-1", "concept": "Intent management", "tags": "intent|policy"},
            {"standard_id": "STD-2", "concept": "Autonomous closed loop", "tags": "autonomy|closed-loop"},
        ]
    )


def test_taxonomy_counts_categories():
    taxonomy = build_taxonomy(sample_studies())
    row = taxonomy[
        (taxonomy["dimension"] == "neural_component")
        & (taxonomy["category"] == "Transformer")
    ].iloc[0]
    assert row["study_count"] == 2


def test_study_matrix_is_structured():
    matrix = study_matrix(sample_studies())
    assert len(matrix) == 3
    assert "knowledge_representation" in matrix.columns


def test_gap_heuristic_flags_sparse_categories():
    gaps = identify_research_gaps(sample_studies(), max_studies=1)
    assert not gaps.empty
    assert (gaps["gap_type"] == "sparse_in_supplied_corpus").all()


def test_standards_mapping_uses_explicit_tags():
    mapped = map_standards(sample_studies(), sample_standards())
    assert ((mapped["study_id"] == "S1") & (mapped["standard_id"] == "STD-1")).any()
    assert ((mapped["study_id"] == "S2") & (mapped["standard_id"] == "STD-2")).any()


def test_summary_reports_mapped_studies():
    summary = summarize_mapping(sample_studies(), sample_standards())
    assert summary["studies"] == 3
    assert summary["mapped_studies"] == 3
