"""Deduplication logic for research paper records.

Enforces ScholarPulse SRS v1.0 Section 4 (FR-004) and Section 11 (T-002):
- Exact normalized DOI match
- Source name + external identifier match
- Fallback normalized title + author match
- Ambiguous matches are NEVER silently merged
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from sqlalchemy import select
from sqlalchemy.orm import Session
from backend.app.models.paper import Paper, Author, PaperAuthor
from backend.app.preprocessing.normalizer import normalize_text


@dataclass
class DeduplicationResult:
    """Outcome of duplicate detection check."""

    status: str  # "unique", "duplicate", "ambiguous"
    existing_paper: Optional[Paper] = None
    match_reason: Optional[str] = None
    details: Optional[str] = None


class Deduplicator:
    """Identifies duplicate or ambiguous paper records in the database."""

    def __init__(self, db: Session):
        self.db = db

    def check_duplicate(self, validated_record: Dict[str, Any]) -> DeduplicationResult:
        """Evaluate a validated paper dictionary against existing records in the database."""
        doi = validated_record.get("doi")
        source_name = validated_record.get("source_name")
        external_id = validated_record.get("external_id")
        title = validated_record.get("title", "")
        normalized_title = normalize_text(title)
        incoming_authors = validated_record.get("authors", [])

        # 1. Exact DOI match
        if doi:
            stmt = select(Paper).where(Paper.doi == doi)
            match = self.db.scalars(stmt).first()
            if match:
                return DeduplicationResult(
                    status="duplicate",
                    existing_paper=match,
                    match_reason="exact_doi",
                    details=f"Exact match on DOI: {doi}",
                )

        # 2. Source and External ID match
        if source_name and external_id:
            stmt = select(Paper).where(
                (Paper.source_name == source_name) & (Paper.external_id == external_id)
            )
            match = self.db.scalars(stmt).first()
            if match:
                return DeduplicationResult(
                    status="duplicate",
                    existing_paper=match,
                    match_reason="source_external_id",
                    details=f"Exact match on source ({source_name}) and external ID ({external_id})",
                )

        # 3. Fallback: Normalized Title search
        if normalized_title:
            # Look for papers with exact or identical normalized title
            stmt = select(Paper)
            all_papers = self.db.scalars(stmt).all()
            for p in all_papers:
                if normalize_text(p.title) == normalized_title:
                    # Check author overlap
                    existing_authors = [pa.author.normalized_name for pa in p.authors]
                    incoming_author_names = [a.get("normalized_name") for a in incoming_authors if a.get("normalized_name")]

                    # If both have authors and at least one author overlaps -> duplicate
                    has_author_overlap = any(
                        inc in existing_authors or any(inc in ex or ex in inc for ex in existing_authors)
                        for inc in incoming_author_names
                    )

                    if has_author_overlap:
                        return DeduplicationResult(
                            status="duplicate",
                            existing_paper=p,
                            match_reason="title_and_author",
                            details="Identical normalized title and matching author",
                        )
                    else:
                        # Identical title but completely different/missing authors -> ambiguous!
                        return DeduplicationResult(
                            status="ambiguous",
                            existing_paper=p,
                            match_reason="title_match_author_mismatch",
                            details="Identical title detected but author list does not match; not merged.",
                        )

        return DeduplicationResult(status="unique")
