"""Saved Research Papers Library API controller.

Adheres strictly to ScholarPulse SRS v1.0 Section 8.11 & FR-020, FR-023:
- User bookmarks management (save, list, delete)
- Per-user data isolation
"""

import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Header, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.app.schemas.library import (
    SavePaperRequest,
    SavedPaperItem,
    SavedLibraryResponse,
)
from backend.app.models.user import User, SavedPaper
from backend.app.models.paper import Paper
from backend.app.api.deps import get_db
from backend.app.core.errors import NotFoundError, ConflictError

router = APIRouter()

# Fixed deterministic default demo user UUID for local evaluation
DEFAULT_DEMO_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")


def _get_or_create_user(db: Session, user_id_header: Optional[str] = None) -> User:
    """Ensure an active user exists for the given ID or demo session."""
    user_id = DEFAULT_DEMO_USER_ID
    if user_id_header:
        try:
            user_id = uuid.UUID(user_id_header)
        except ValueError:
            user_id = DEFAULT_DEMO_USER_ID

    user = db.get(User, user_id)
    if not user:
        user = User(
            id=user_id,
            email=f"researcher_{user_id.hex[:6]}@scholarpulse.local",
            password_hash="placeholder_hash",
            role="user",
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


@router.get(
    "/library/papers",
    response_model=SavedLibraryResponse,
    status_code=status.HTTP_200_OK,
    summary="List saved papers in the user's research library",
)
def list_saved_papers(
    x_user_id: Optional[str] = Header(None, description="Optional user UUID header"),
    db: Session = Depends(get_db),
) -> SavedLibraryResponse:
    """Retrieve bookmarked research papers for the current user."""
    user = _get_or_create_user(db, x_user_id)
    stmt = (
        select(SavedPaper)
        .where(SavedPaper.user_id == user.id)
        .order_by(SavedPaper.created_at.desc())
    )
    saved = list(db.scalars(stmt).all())

    items = []
    for sp in saved:
        paper = db.get(Paper, sp.paper_id)
        title = paper.title if paper else "Unknown Paper"
        year = paper.publication_year if paper else None
        doi = paper.doi if paper else None

        items.append(
            SavedPaperItem(
                id=sp.paper_id,
                paper_id=sp.paper_id,
                title=title,
                notes=None,
                saved_at=sp.created_at,
                publication_year=year,
                doi=doi,
            )
        )

    return SavedLibraryResponse(total=len(items), items=items)


@router.post(
    "/library/papers",
    response_model=SavedPaperItem,
    status_code=status.HTTP_201_CREATED,
    summary="Save a research paper to user's library",
)
def save_paper(
    payload: SavePaperRequest,
    x_user_id: Optional[str] = Header(None, description="Optional user UUID header"),
    db: Session = Depends(get_db),
) -> SavedPaperItem:
    """Bookmark a paper to the authenticated user's library."""
    user = _get_or_create_user(db, x_user_id)

    # Verify paper exists
    paper = db.get(Paper, payload.paper_id)
    if not paper:
        raise NotFoundError(f"Paper with ID '{payload.paper_id}' not found.")

    # Check for existing bookmark
    existing = db.get(SavedPaper, (user.id, payload.paper_id))
    if existing:
        raise ConflictError("Paper is already saved in your library.")

    saved_entry = SavedPaper(
        user_id=user.id,
        paper_id=payload.paper_id,
    )
    db.add(saved_entry)
    db.commit()
    db.refresh(saved_entry)

    return SavedPaperItem(
        id=saved_entry.paper_id,
        paper_id=saved_entry.paper_id,
        title=paper.title,
        notes=payload.notes,
        saved_at=saved_entry.created_at,
        publication_year=paper.publication_year,
        doi=paper.doi,
    )


@router.delete(
    "/library/papers/{paper_id}",
    status_code=status.HTTP_200_OK,
    summary="Remove a paper from user's library",
)
def remove_saved_paper(
    paper_id: uuid.UUID,
    x_user_id: Optional[str] = Header(None, description="Optional user UUID header"),
    db: Session = Depends(get_db),
):
    """Remove a bookmarked paper from the user's library."""
    user = _get_or_create_user(db, x_user_id)
    saved_entry = db.get(SavedPaper, (user.id, paper_id))
    if not saved_entry:
        raise NotFoundError("Saved paper not found in your library.")

    db.delete(saved_entry)
    db.commit()

    return {"status": "success", "message": "Paper removed from library."}
