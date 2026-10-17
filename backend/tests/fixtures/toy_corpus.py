"""Toy fixture corpus for deterministic Information Retrieval algorithm testing.

Contains 5 small, hand-checkable documents designed to rigorously test:
- Boolean intersection, union, difference, and negation
- Term frequency saturation (BM25 vs TF-IDF)
- Document length normalization penalty
"""

from typing import List, Dict

TOY_DOCUMENTS: List[Dict[str, str]] = [
    {
        "id": "doc1",
        "title": "Information Retrieval Basics",
        "text": "information retrieval inverted index search query processing",
    },
    {
        "id": "doc2",
        "title": "Advanced Information Retrieval",
        "text": "information retrieval search search search ranking bm25 probabilistic model",
    },
    {
        "id": "doc3",
        "title": "Machine Learning and Neural Networks",
        "text": "machine learning deep learning neural networks classification",
    },
    {
        "id": "doc4",
        "title": "Deep Learning for Search",
        "text": "deep learning neural networks information retrieval search ranking",
    },
    {
        "id": "doc5",
        "title": "Database Systems",
        "text": "database systems relational sql transactions indexing",
    },
]
