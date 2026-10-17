"""Tokenizer and stemmer module using NLTK with guaranteed offline fallbacks.

Adheres to ScholarPulse IR syllabus (Inverted Index, Dictionary construction, Tokenization):
- Token extraction and filtering
- Case folding
- Stopword removal
- Porter Stemming
- Searchable text assembly
"""

import re
from typing import List, Optional, Set
import nltk
from nltk.stem import PorterStemmer
from backend.app.preprocessing.normalizer import normalize_text

# Built-in standard English stopwords fallback for guaranteed offline execution
FALLBACK_STOPWORDS: Set[str] = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are",
    "aren't", "as", "at", "be", "because", "been", "before", "being", "below", "between", "both",
    "but", "by", "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't",
    "doing", "don't", "down", "during", "each", "few", "for", "from", "further", "had", "hadn't",
    "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here",
    "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll",
    "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's",
    "me", "more", "most", "mustn't", "my", "myself", "no", "nor", "not", "of", "off", "on",
    "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own",
    "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some",
    "such", "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then",
    "there", "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this",
    "those", "through", "to", "too", "under", "until", "up", "very", "was", "wasn't", "we",
    "we'd", "we'll", "we're", "we've", "were", "weren't", "what", "what's", "when", "when's",
    "where", "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with",
    "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your",
    "yours", "yourself", "yourselves",
}

# Try loading NLTK stopwords, fallback to static set if offline
try:
    from nltk.corpus import stopwords
    try:
        STOPWORDS: Set[str] = set(stopwords.words("english"))
    except LookupError:
        nltk.download("stopwords", quiet=True)
        STOPWORDS = set(stopwords.words("english"))
except Exception:
    STOPWORDS = FALLBACK_STOPWORDS

stemmer = PorterStemmer()


def tokenize(text: str) -> List[str]:
    """Tokenize normalized text into clean alphanumeric words."""
    cleaned = normalize_text(text)
    # Split by whitespace and remove non-alphanumeric punctuation
    raw_tokens = re.findall(r"\b[a-zA-Z0-9]+(?:-[a-zA-Z0-9]+)*\b", cleaned)
    return raw_tokens


def stem(token: str) -> str:
    """Stem a token using Porter Stemmer."""
    return stemmer.stem(token.lower())


def preprocess_text(text: Optional[str], remove_stopwords: bool = True, apply_stemming: bool = True) -> List[str]:
    """Complete preprocessing pipeline: tokenize -> remove stopwords -> stem."""
    if not text:
        return []
    tokens = tokenize(text)
    result = []
    for token in tokens:
        token_lower = token.lower()
        if len(token_lower) <= 1:
            continue
        if remove_stopwords and token_lower in STOPWORDS:
            continue
        if apply_stemming:
            token_lower = stem(token_lower)
        result.append(token_lower)
    return result


def build_searchable_text(title: str, abstract: Optional[str] = None, keywords: Optional[List[str]] = None) -> str:
    """Combine title, abstract, and keywords into a single normalized searchable string."""
    parts = [title]
    if abstract:
        parts.append(abstract)
    if keywords:
        parts.extend(keywords)
    combined = " ".join(parts)
    processed_tokens = preprocess_text(combined, remove_stopwords=True, apply_stemming=True)
    return " ".join(processed_tokens)
