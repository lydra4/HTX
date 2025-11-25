from __future__ import annotations

from datetime import datetime
from typing import List

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str


class VideoBase(BaseModel):
    filename: str
    summary: str
    detected_objects: List[str]
    key_frames: List[str]


class VideoRead(VideoBase):
    id: int
    storage_path: str
    created_at: datetime

    class Config:
        from_attributes = True


class TranscriptionBase(BaseModel):
    filename: str
    transcript: str
    confidence_score: float


class TranscriptionRead(TranscriptionBase):
    id: int
    storage_path: str
    video_id: int | None
    created_at: datetime

    class Config:
        from_attributes = True


class SearchResponse(BaseModel):
    videos: List[VideoRead]
    transcriptions: List[TranscriptionRead]

