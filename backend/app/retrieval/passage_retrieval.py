"""Passage Retrieval and Snippet Extraction for academic research papers.

Segments text into sentence-level passages, scores relevance using query term coverage
and frequency, and generates highlighted snippets for search result previews.
"""

import re
from dataclasses import dataclass, field
from typing import List, Set, Optional

from backend.app.preprocessing.tokenizer import tokenize, stem, STOPWORDS


@dataclass
class ExtractedPassage:
    """Represents an extracted relevant text passage / snippet."""
    text: str
    highlighted_text: str
    score: float
    matched_terms: List[str] = field(default_factory=list)


class PassageRetrievalEngine:
    """Extracts and highlights top-scoring passages from paper abstracts or text."""

    def __init__(self, max_snippet_length: int = 250):
        self.max_snippet_length = max_snippet_length

    def split_sentences(self, text: str) -> List[str]:
        """Split text into sentences using punctuation boundaries."""
        if not text:
            return []
        # Split on sentence terminals followed by whitespace or end of string
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        return [s.strip() for s in sentences if s.strip()]

    def extract_best_passage(self, text: str, query: str) -> ExtractedPassage:
        """Extract the most relevant passage from text matching the query."""
        if not text or not text.strip():
            return ExtractedPassage(text="", highlighted_text="", score=0.0, matched_terms=[])

        sentences = self.split_sentences(text)
        if not sentences:
            return ExtractedPassage(text="", highlighted_text="", score=0.0, matched_terms=[])

        # Tokenize and stem query terms (ignoring stopwords)
        raw_query_tokens = [w.lower() for w in tokenize(query)]
        query_stems = {stem(w) for w in raw_query_tokens if w not in STOPWORDS}
        query_words_clean = {w for w in raw_query_tokens if w not in STOPWORDS}

        if not query_stems:
            # Fallback to first sentence if query has only stopwords or is empty
            first_sent = sentences[0][: self.max_snippet_length]
            return ExtractedPassage(
                text=first_sent,
                highlighted_text=first_sent,
                score=0.0,
                matched_terms=[],
            )

        best_idx = 0
        best_score = -1.0
        best_matched_terms: List[str] = []

        for idx, sentence in enumerate(sentences):
            sent_tokens = [w.lower() for w in tokenize(sentence)]
            sent_stems = [stem(w) for w in sent_tokens]

            matched = [w for w, s in zip(sent_tokens, sent_stems) if s in query_stems]
            unique_matched_stems = {s for s in sent_stems if s in query_stems}

            # Score prioritizes unique query term coverage, then total term occurrences
            coverage = len(unique_matched_stems) / float(len(query_stems))
            frequency = len(matched)
            # Length penalty for excessively long sentences
            len_penalty = 1.0 if len(sentence) <= self.max_snippet_length else 0.85
            score = (coverage * 2.0 + frequency * 0.5) * len_penalty

            if score > best_score:
                best_score = score
                best_idx = idx
                best_matched_terms = list(set(matched))

        chosen_text = sentences[best_idx]

        # If chosen sentence is very short, combine with adjacent sentence
        if len(chosen_text) < 100 and len(sentences) > 1:
            if best_idx + 1 < len(sentences):
                candidate = f"{chosen_text} {sentences[best_idx + 1]}"
                if len(candidate) <= self.max_snippet_length + 50:
                    chosen_text = candidate
            elif best_idx - 1 >= 0:
                candidate = f"{sentences[best_idx - 1]} {chosen_text}"
                if len(candidate) <= self.max_snippet_length + 50:
                    chosen_text = candidate

        # Truncate if exceeds max length
        if len(chosen_text) > self.max_snippet_length:
            chosen_text = chosen_text[: self.max_snippet_length].rstrip() + "..."

        # Generate highlighted text with <mark> tags
        highlighted = chosen_text
        if best_matched_terms:
            # Case-insensitive replacement with <mark>
            for term in sorted(best_matched_terms, key=len, reverse=True):
                pattern = re.compile(rf"\b({re.escape(term)})\b", re.IGNORECASE)
                highlighted = pattern.sub(r"<mark>\1</mark>", highlighted)

        return ExtractedPassage(
            text=chosen_text,
            highlighted_text=highlighted,
            score=round(max(0.0, best_score), 4),
            matched_terms=best_matched_terms,
        )
