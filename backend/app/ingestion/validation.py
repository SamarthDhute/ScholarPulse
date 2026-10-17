"""Data validation for ingested paper records.

Enforces ScholarPulse SRS v1.0 Section 4 (FR-003) and Section 11 (T-001):
- Required title (reject blank values)
- Plausible publication year range
- Normalized DOI and source identifiers
"""

from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from backend.app.core.errors import ValidationError
from backend.app.preprocessing.normalizer import clean_doi, normalize_text


def validate_paper_payload(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and clean incoming raw paper dictionary.

    Returns sanitized dictionary or raises ValidationError with field details.
    """
    errors: Dict[str, str] = {}

    # 1. Validate title
    raw_title = raw.get("title")
    if not raw_title or not isinstance(raw_title, str) or not raw_title.strip():
        errors["title"] = "Title is required and cannot be empty or whitespace."
        title = ""
    else:
        title = raw_title.strip()

    # 2. Validate abstract
    raw_abstract = raw.get("abstract")
    abstract = raw_abstract.strip() if isinstance(raw_abstract, str) and raw_abstract.strip() else None

    # 3. Validate publication year
    raw_year = raw.get("publication_year")
    current_year = datetime.now(timezone.utc).year
    year: Optional[int] = None
    if raw_year is not None:
        try:
            year = int(raw_year)
            if year < 1800 or year > current_year + 5:
                errors["publication_year"] = f"Publication year {year} is out of plausible range [1800, {current_year + 5}]."
        except (ValueError, TypeError):
            errors["publication_year"] = f"Publication year '{raw_year}' is not a valid integer."

    # 4. Clean DOI
    raw_doi = raw.get("doi")
    doi = clean_doi(raw_doi) if isinstance(raw_doi, str) else None

    # 5. Source metadata
    source_name = raw.get("source_name", "local_sample")
    if not isinstance(source_name, str) or not source_name.strip():
        source_name = "local_sample"
    source_name = source_name.strip().lower()

    source_url = raw.get("source_url")
    if source_url and isinstance(source_url, str):
        source_url = source_url.strip()
    else:
        source_url = None

    external_id = raw.get("external_id")
    if external_id and isinstance(external_id, str):
        external_id = external_id.strip()
    else:
        external_id = None

    # 6. Authors list
    raw_authors = raw.get("authors", [])
    authors: List[Dict[str, Any]] = []
    if isinstance(raw_authors, list):
        for idx, item in enumerate(raw_authors):
            if isinstance(item, str) and item.strip():
                authors.append({
                    "display_name": item.strip(),
                    "normalized_name": normalize_text(item),
                    "author_order": idx + 1,
                })
            elif isinstance(item, dict) and item.get("display_name"):
                name = item["display_name"].strip()
                authors.append({
                    "display_name": name,
                    "normalized_name": normalize_text(name),
                    "author_order": item.get("author_order", idx + 1),
                    "external_id": item.get("external_id"),
                })

    # 7. Keywords list
    raw_keywords = raw.get("keywords", [])
    keywords: List[Dict[str, str]] = []
    if isinstance(raw_keywords, list):
        for item in raw_keywords:
            if isinstance(item, str) and item.strip():
                keywords.append({
                    "display_term": item.strip(),
                    "normalized_term": normalize_text(item),
                    "origin": "source",
                })

    # 8. Categories list
    raw_categories = raw.get("categories", [])
    categories: List[str] = []
    if isinstance(raw_categories, list):
        for item in raw_categories:
            if isinstance(item, str) and item.strip():
                categories.append(item.strip())

    if errors:
        raise ValidationError(message="Paper validation failed.", details=errors)

    return {
        "title": title,
        "abstract": abstract,
        "publication_year": year,
        "doi": doi,
        "source_name": source_name,
        "source_url": source_url,
        "external_id": external_id,
        "document_type": raw.get("document_type", "paper"),
        "language": raw.get("language", "en"),
        "raw_metadata": raw.get("raw_metadata") or {},
        "authors": authors,
        "keywords": keywords,
        "categories": categories,
    }
