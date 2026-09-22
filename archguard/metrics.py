from __future__ import annotations

from collections import Counter

import numpy as np
from sklearn.metrics import cohen_kappa_score, confusion_matrix, precision_recall_fscore_support

from .models import Status


LABELS = [status.value for status in Status]


def evaluate_labels(reference: dict[str, str], predictions: dict[str, str],
                    reference_minutes: float | None = None,
                    assisted_minutes: float | None = None) -> dict:
    common = sorted(set(reference) & set(predictions))
    if not common:
        raise ValueError("Reference and prediction sets have no common requirement IDs")
    truth = [reference[item] for item in common]
    guess = [predictions[item] for item in common]
    unknown = (set(truth) | set(guess)) - set(LABELS)
    if unknown:
        raise ValueError(f"Unknown labels: {sorted(unknown)}")
    precision, recall, f1, support = precision_recall_fscore_support(
        truth, guess, labels=LABELS, zero_division=0)
    matrix = confusion_matrix(truth, guess, labels=LABELS)
    agreement = float(np.mean(np.array(truth) == np.array(guess)))
    observed = support > 0
    non_compliant_index = LABELS.index(Status.NON_COMPLIANT.value)
    false_positives = sum(matrix[row, non_compliant_index] for row in range(len(LABELS)) if row != non_compliant_index)
    actual_negatives = sum(matrix[row].sum() for row in range(len(LABELS)) if row != non_compliant_index)
    result = {
        "requirements_compared": len(common),
        "agreement": agreement,
        "cohen_kappa": float(cohen_kappa_score(truth, guess, labels=LABELS)),
        "macro_precision": float(np.mean(precision)),
        "macro_recall": float(np.mean(recall)),
        "macro_f1": float(np.mean(f1)),
        "observed_class_macro_precision": float(np.mean(precision[observed])),
        "observed_class_macro_recall": float(np.mean(recall[observed])),
        "observed_class_macro_f1": float(np.mean(f1[observed])),
        "non_compliance_false_positive_rate": float(false_positives / actual_negatives) if actual_negatives else 0.0,
        "per_class": {label: {"precision": float(precision[idx]), "recall": float(recall[idx]),
                              "f1": float(f1[idx]), "support": int(support[idx])}
                      for idx, label in enumerate(LABELS)},
        "confusion_matrix": {actual: {predicted: int(matrix[i, j]) for j, predicted in enumerate(LABELS)}
                             for i, actual in enumerate(LABELS)},
        "reference_distribution": dict(Counter(truth)),
        "prediction_distribution": dict(Counter(guess)),
    }
    if reference_minutes is not None and assisted_minutes is not None:
        result["review_effort"] = {
            "reference_minutes": reference_minutes, "assisted_minutes": assisted_minutes,
            "minutes_saved": reference_minutes - assisted_minutes,
            "reduction_fraction": (reference_minutes - assisted_minutes) / reference_minutes if reference_minutes else 0,
        }
    return result
