from __future__ import annotations

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .models import Requirement
from .parser import split_passages


class RequirementRetriever:
    def __init__(self, document: str):
        self.passages = split_passages(document)
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words="english", sublinear_tf=True)
        self.matrix = self.vectorizer.fit_transform([item[2] for item in self.passages])

    def retrieve(self, requirement: Requirement, top_k: int = 3) -> list[dict]:
        query = " ".join([requirement.title, requirement.statement, *requirement.evidence_any,
                          *requirement.contradiction_any])
        vector = self.vectorizer.transform([query])
        scores = cosine_similarity(vector, self.matrix)[0]
        indices = np.argsort(scores)[::-1][:top_k]
        return [{"start": self.passages[idx][0], "end": self.passages[idx][1],
                 "text": self.passages[idx][2], "score": float(scores[idx])} for idx in indices]
