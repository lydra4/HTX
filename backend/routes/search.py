from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import String, cast, or_, select
from sqlalchemy.orm import Session

from backend import models
from backend.database import get_session
from backend.schemas import SearchResponse, TranscriptionRead, VideoRead

router = APIRouter()


@router.get("/search", response_model=SearchResponse)
def search_media(
    term: str = Query(..., min_length=1, description="Full-text search query."),
    db: Session = Depends(get_session),
) -> SearchResponse:
    term_like = f"%{term.lower()}%"

    video_stmt = select(models.Video).where(
        or_(
            models.Video.filename.ilike(term_like),
            models.Video.summary.ilike(term_like),
            cast(models.Video.detected_objects, String).ilike(term_like),
        )
    )
    transcription_stmt = select(models.Transcription).where(
        or_(
            models.Transcription.filename.ilike(term_like),
            models.Transcription.transcript.ilike(term_like),
        )
    )

    video_rows = db.scalars(video_stmt).all()
    transcription_rows = db.scalars(transcription_stmt).all()

    return SearchResponse(
        videos=[VideoRead.model_validate(row) for row in video_rows],
        transcriptions=[
            TranscriptionRead.model_validate(row) for row in transcription_rows
        ],
    )

