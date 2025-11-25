from __future__ import annotations

import hashlib
import os

from fastapi import UploadFile
from sqlalchemy.orm import Session

from backend import models
from backend.settings import AppSettings


class AudioProcessor:
    """Persist audio uploads and generate lightweight transcripts."""

    def __init__(self, settings: AppSettings) -> None:
        self.settings = settings

    async def process(self, file: UploadFile, db: Session) -> models.Transcription:
        storage_path = await self._persist_file(file)
        transcript, confidence = await self._transcribe(storage_path)

        transcription = models.Transcription(
            filename=file.filename,
            storage_path=storage_path,
            transcript=transcript,
            confidence_score=confidence,
        )
        db.add(transcription)
        db.commit()
        db.refresh(transcription)
        return transcription

    async def _persist_file(self, file: UploadFile) -> str:
        dest_path = os.path.join(self.settings.storage.audio_input_dir, file.filename)
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)

        contents = await file.read()
        with open(dest_path, "wb") as buffer:
            buffer.write(contents)
        await file.seek(0)
        return dest_path

    async def _transcribe(self, audio_path: str) -> tuple[str, float]:
        """Placeholder transcription that hashes audio content."""
        with open(audio_path, "rb") as audio_file:
            data = audio_file.read()

        digest = hashlib.sha256(data).hexdigest()
        transcript = f"Placeholder transcription (sha256={digest[:12]})."
        confidence = 0.5
        return transcript, confidence

