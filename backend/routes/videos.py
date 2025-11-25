from __future__ import annotations

from fastapi import APIRouter, Depends, File, Request, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend import models
from backend.database import get_session
from backend.schemas import VideoRead
from backend.services.video_processor import VideoProcessor

router = APIRouter()


def get_video_processor(request: Request) -> VideoProcessor:
    return request.app.state.video_processor


@router.post(
    "/process/video",
    response_model=VideoRead,
    status_code=201,
)
async def process_video(
    file: UploadFile = File(...),
    db: Session = Depends(get_session),
    video_processor: VideoProcessor = Depends(get_video_processor),
) -> VideoRead:
    video = await video_processor.process(file=file, db=db)
    return VideoRead.model_validate(video)


@router.get("/videos", response_model=list[VideoRead])
def list_videos(db: Session = Depends(get_session)) -> list[VideoRead]:
    rows = db.scalars(select(models.Video).order_by(models.Video.created_at)).all()
    return [VideoRead.model_validate(row) for row in rows]

