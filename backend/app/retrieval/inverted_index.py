"""Custom Inverted Index implementation for ScholarPulse.

Adheres strictly to Information Retrieval syllabus:
- Dictionary mapping terms to document frequency (df)
- Posting lists mapping terms to (document ID, term frequency tf)
- Document length tracking (|d| and avgdl)
- Serialization to and from JSON artifacts
"""

import json
import os
from collections import defaultdict
from typing import Dict, List, Set, Optional, Tuple, Sequence
from backend.app.preprocessing.tokenizer import preprocess_text


class InvertedIndex:
    """Inverted index data structure mapping terms to document postings."""

    def __init__(self):
        # term -> {doc_id: term_frequency}
        self.postings: Dict[str, Dict[str, int]] = defaultdict(dict)
        # doc_id -> total token count in document
        self.doc_lengths: Dict[str, int] = {}
        # List of all unique document IDs
        self.doc_ids: Set[str] = set()

    @property
    def doc_count(self) -> int:
        """Total number of documents in collection (N)."""
        return len(self.doc_ids)

    @property
    def avg_doc_length(self) -> float:
        """Average document length across the collection (avgdl)."""
        if not self.doc_lengths:
            return 0.0
        return sum(self.doc_lengths.values()) / len(self.doc_lengths)

    def add_document(self, doc_id: str, text: str) -> None:
        """Tokenize, stem, and index a document."""
        tokens = preprocess_text(text, remove_stopwords=True, apply_stemming=True)
        self.doc_ids.add(doc_id)
        self.doc_lengths[doc_id] = len(tokens)

        # Count frequencies for this document
        counts: Dict[str, int] = defaultdict(int)
        for token in tokens:
            counts[token] += 1

        for term, freq in counts.items():
            self.postings[term][doc_id] = freq

    def build_from_documents(self, documents: Sequence[Tuple[str, str]]) -> None:
        """Batch build index from list of (doc_id, text) pairs."""
        for doc_id, text in documents:
            self.add_document(doc_id, text)

    def get_postings(self, term: str) -> Dict[str, int]:
        """Return postings mapping doc_id -> tf for a given term."""
        return self.postings.get(term.lower(), {})

    def get_doc_frequency(self, term: str) -> int:
        """Return document frequency (df) for a term."""
        return len(self.get_postings(term))

    def get_term_frequency(self, term: str, doc_id: str) -> int:
        """Return term frequency (tf) of term in a specific document."""
        return self.get_postings(term).get(doc_id, 0)

    def get_vocabulary(self) -> Set[str]:
        """Return set of all unique terms in dictionary."""
        return set(self.postings.keys())

    def save(self, filepath: str) -> None:
        """Serialize index to JSON artifact."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        data = {
            "postings": {t: dict(p) for t, p in self.postings.items()},
            "doc_lengths": self.doc_lengths,
            "doc_ids": list(self.doc_ids),
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)

    @classmethod
    def load(cls, filepath: str) -> "InvertedIndex":
        """Deserialize index from JSON artifact."""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Inverted index artifact not found at {filepath}")

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        index = cls()
        index.postings = defaultdict(dict, {t: dict(p) for t, p in data.get("postings", {}).items()})
        index.doc_lengths = data.get("doc_lengths", {})
        index.doc_ids = set(data.get("doc_ids", []))
        return index
