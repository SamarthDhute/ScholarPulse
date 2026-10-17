"""Ingestion Service for processing, deduplicating, and persisting academic research records.

Enforces ScholarPulse SRS v1.0 Section 4 (FR-001, FR-002, FR-003, FR-004, FR-005):
- Validates input metadata
- Prevents duplicates via Deduplicator
- Rebuilds searchable normalized text
- Preserves author order, keyword vocabulary, and categories
- Records ingestion run statistics and provenance
"""

import json
import os
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session

from backend.app.models.paper import (
    Paper,
    Author,
    PaperAuthor,
    Keyword,
    PaperKeyword,
    Category,
    PaperCategory,
)
from backend.app.models.ingestion import IngestionRun
from backend.app.repositories.paper_repository import PaperRepository
from backend.app.repositories.author_repository import AuthorRepository
from backend.app.repositories.keyword_repository import KeywordRepository
from backend.app.repositories.category_repository import CategoryRepository
from backend.app.repositories.ingestion_repository import IngestionRepository
from backend.app.ingestion.validation import validate_paper_payload
from backend.app.ingestion.deduplication import Deduplicator, DeduplicationResult
from backend.app.preprocessing.tokenizer import build_searchable_text
from backend.app.core.errors import ValidationError
from backend.app.core.logging import logger


class IngestionService:
    """Service handling paper validation, deduplication, and persistence."""

    def __init__(self, db: Session):
        self.db = db
        self.paper_repo = PaperRepository(db)
        self.author_repo = AuthorRepository(db)
        self.keyword_repo = KeywordRepository(db)
        self.category_repo = CategoryRepository(db)
        self.ingestion_repo = IngestionRepository(db)
        self.deduplicator = Deduplicator(db)

    def ingest_record(self, raw_record: Dict[str, Any]) -> Tuple[Optional[Paper], str, Optional[str]]:
        """Validate, deduplicate, and ingest a single paper record.

        Returns: (paper, status, details) where status is 'created', 'updated', or 'skipped'.
        """
        # 1. Validation
        validated = validate_paper_payload(raw_record)

        # 2. Deduplication check
        dedup_result = self.deduplicator.check_duplicate(validated)

        if dedup_result.status == "ambiguous":
            logger.warning("Skipping ambiguous record: %s (Reason: %s)", validated["title"], dedup_result.details)
            return None, "skipped", dedup_result.details

        if dedup_result.status == "duplicate" and dedup_result.existing_paper is not None:
            existing = dedup_result.existing_paper
            # Enrich existing paper if incoming has missing abstract or details
            updated = False
            if not existing.abstract and validated.get("abstract"):
                existing.abstract = validated["abstract"]
                updated = True
            if not existing.source_url and validated.get("source_url"):
                existing.source_url = validated["source_url"]
                updated = True
            if not existing.external_id and validated.get("external_id"):
                existing.external_id = validated["external_id"]
                updated = True

            # If updated, recompute normalized text
            if updated:
                existing_keywords = [pk.keyword.display_term for pk in existing.keywords]
                existing.normalized_text = build_searchable_text(
                    title=existing.title,
                    abstract=existing.abstract,
                    keywords=existing_keywords,
                )
                self.db.commit()
                return existing, "updated", f"Enriched existing record (matched via {dedup_result.match_reason})"
            return existing, "skipped", f"Exact duplicate ignored (matched via {dedup_result.match_reason})"

        # 3. Create new Paper entity
        keyword_terms = [k["display_term"] for k in validated["keywords"]]
        searchable_text = build_searchable_text(
            title=validated["title"],
            abstract=validated.get("abstract"),
            keywords=keyword_terms,
        )

        paper = Paper(
            title=validated["title"],
            abstract=validated.get("abstract"),
            publication_year=validated.get("publication_year"),
            doi=validated.get("doi"),
            source_name=validated["source_name"],
            source_url=validated.get("source_url"),
            external_id=validated.get("external_id"),
            document_type=validated.get("document_type"),
            language=validated.get("language"),
            raw_metadata=validated.get("raw_metadata"),
            normalized_text=searchable_text,
        )
        self.db.add(paper)
        self.db.flush()

        # 4. Attach Authors in order
        for author_data in validated.get("authors", []):
            author = self.author_repo.get_or_create(
                display_name=author_data["display_name"],
                normalized_name=author_data["normalized_name"],
                external_id=author_data.get("external_id"),
            )
            pa = PaperAuthor(
                paper_id=paper.id,
                author_id=author.id,
                author_order=author_data.get("author_order", 1),
            )
            self.db.add(pa)

        # 5. Attach Keywords
        for kw_data in validated.get("keywords", []):
            kw = self.keyword_repo.get_or_create(
                display_term=kw_data["display_term"],
                normalized_term=kw_data["normalized_term"],
            )
            pk = PaperKeyword(
                paper_id=paper.id,
                keyword_id=kw.id,
                origin=kw_data.get("origin", "source"),
            )
            self.db.add(pk)

        # 6. Attach Categories
        for cat_name in validated.get("categories", []):
            cat = self.category_repo.get_or_create(name=cat_name)
            pc = PaperCategory(
                paper_id=paper.id,
                category_id=cat.id,
                label_source="verified",
                confidence=1.0,
            )
            self.db.add(pc)

        self.db.commit()
        self.db.refresh(paper)
        return paper, "created", "Successfully created new paper record"

    def ingest_from_file(self, file_path: str, source_name: Optional[str] = None) -> IngestionRun:
        """Ingest all paper records from a local JSON file repeatably."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Dataset file not found at: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        if not isinstance(raw_data, list):
            raise ValueError("Dataset JSON must contain an array of paper records.")

        src = source_name or (raw_data[0].get("source_name", "local_file") if raw_data else "local_file")
        run = self.ingestion_repo.start_run(source_name=src)

        seen = 0
        created = 0
        updated = 0
        skipped = 0
        errors = 0
        skipped_details: List[str] = []

        for record in raw_data:
            seen += 1
            try:
                paper, action, detail = self.ingest_record(record)
                if action == "created":
                    created += 1
                elif action == "updated":
                    updated += 1
                elif action == "skipped":
                    skipped += 1
                    if detail:
                        skipped_details.append(detail)
            except Exception as e:
                errors += 1
                logger.error("Error ingesting record: %s", str(e))

        summary = {
            "file_path": file_path,
            "total_seen": seen,
            "created": created,
            "updated": updated,
            "skipped": skipped,
            "errors": errors,
            "skipped_sample": skipped_details[:5],
        }

        status = "completed" if errors == 0 else ("failed" if created == 0 else "completed_with_errors")
        final_run = self.ingestion_repo.finish_run(
            run_id=run.id,
            status=status,
            records_seen=seen,
            records_created=created,
            records_updated=updated,
            records_skipped=skipped,
            error_count=errors,
            summary=summary,
        )
        return final_run or run
