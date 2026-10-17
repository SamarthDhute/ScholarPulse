"""Text normalization utilities for ScholarPulse preprocessing.

Performs:
- Lowercasing and whitespace normalization
- Punctuation removal while preserving alphanumeric tokens and hyphens
- Unicode normalization (NFKD) to handle accented characters
"""

import re
import unicodedata
from typing import Optional


def normalize_text(text: Optional[str]) -> str:
    """Normalize input string to clean, lowercase, ASCII-compatible text."""
    if not text:
        return ""
    # Replace em-dashes, en-dashes, and special dashes with spaces
    text = re.sub(r"[\u2010-\u2015\u2212—–]", " ", text)
    # Normalize unicode characters (e.g. naive -> naive, cafe -> cafe)
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("utf-8")
    # Convert to lowercase
    text = text.lower()
    # Replace newlines, tabs, and multiple spaces with a single space
    text = re.sub(r"[\r\n\t]+", " ", text)
    # Remove special characters except alphanumeric, whitespace, and hyphens
    text = re.sub(r"[^\w\s\-]", " ", text)
    # Collapse multiple spaces
    text = re.sub(r"\s+", " ", text).strip()
    return text


def clean_doi(doi: Optional[str]) -> Optional[str]:
    """Clean and normalize a DOI string (e.g., strip URL prefix, lowercase)."""
    if not doi:
        return None
    cleaned = doi.strip().lower()
    # Remove standard URL prefixes
    prefixes = [
        "https://doi.org/",
        "http://doi.org/",
        "https://dx.doi.org/",
        "http://dx.doi.org/",
        "doi:",
    ]
    for prefix in prefixes:
        if cleaned.startswith(prefix):
            cleaned = cleaned[len(prefix):]
    cleaned = cleaned.strip()
    return cleaned if cleaned else None
