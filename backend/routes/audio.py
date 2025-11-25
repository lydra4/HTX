from __future__ import annotations

from fastapi import APIRouter, Depends, File, Request, UploadFile
from sqlalchemy.orm import Session

from backend import models
from backend.database import get_session
from backend.schemas import TranscriptionRead
from backend.services.audio_processor import AudioProcessor

router = APIRouter()


def get_audio_processor(request: Request) -> AudioProcessor:
    return request.app.state.audio_processor


@router.post(
    "/process/audio",
    response_model=TranscriptionRead,
    status_code=201,
)
async def process_audio(
    file: UploadFile = File(...),
    db: Session = Depends(get_session),
    audio_processor: AudioProcessor = Depends(get_audio_processor),
) -> TranscriptionRead:
    transcription = await audio_processor.process(file=file, db=db)
    return TranscriptionRead.model_validate(transcription)


@router.get("/transcriptions", response_model=list[TranscriptionRead])
def list_transcriptions(
    db: Session = Depends(get_session),
) -> list[TranscriptionRead]:
    rows = db.query(models.Transcription).order_by(models.Transcription.created_at).all()
    return [TranscriptionRead.model_validate(row) for row in rows]

