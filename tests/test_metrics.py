from archguard.metrics import evaluate_labels


def test_perfect_agreement():
    labels = {"A": "COMPLIANT", "B": "NON_COMPLIANT", "C": "NOT_ENOUGH_INFORMATION"}
    result = evaluate_labels(labels, labels, 20, 10)
    assert result["agreement"] == 1.0
    assert result["cohen_kappa"] == 1.0
    assert result["non_compliance_false_positive_rate"] == 0.0
    assert result["review_effort"]["reduction_fraction"] == 0.5
