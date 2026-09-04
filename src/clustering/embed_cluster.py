"""Embeddings-based clustering + dedupe (offline TF-IDF stand-in)."""

from __future__ import annotations

from sklearn.cluster import MiniBatchKMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


def cluster_issues(texts: list[str], n_clusters: int = 12, seed: int = 0) -> tuple[np.ndarray, object]:
    vectorizer = TfidfVectorizer(max_features=2000, ngram_range=(1, 2))
    X = vectorizer.fit_transform(texts)
    k = min(n_clusters, max(1, len(texts) // 5))
    model = MiniBatchKMeans(n_clusters=k, random_state=seed, n_init=3, batch_size=256)
    labels = model.fit_predict(X)
    return labels, (vectorizer, X, model)


def dedupe_within_clusters(
    texts: list[str], labels: np.ndarray, X, threshold: float = 0.92
) -> list[bool]:
    """Return keep-mask: True = canonical issue, False = near-duplicate."""
    keep = [True] * len(texts)
    for c in np.unique(labels):
        idx = np.where(labels == c)[0]
        for i, a in enumerate(idx):
            if not keep[a]:
                continue
            for b in idx[i + 1 :]:
                if not keep[b]:
                    continue
                sim = cosine_similarity(X[a], X[b])[0, 0]
                if sim >= threshold:
                    keep[b] = False
    return keep
