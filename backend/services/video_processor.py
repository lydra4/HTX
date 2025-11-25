from __future__ import annotations

import os
from pathlib import Path
from typing import List

import cv2
from fastapi import UploadFile
from sqlalchemy.orm import Session

from backend import models
from backend.settings import AppSettings


class VideoProcessor:
    """Process uploaded videos by extracting key frames and object summaries."""

    def __init__(self, settings: AppSettings, frame_interval: int = 30, max_frames: int = 5) -> None:
        self.settings = settings
        self.frame_interval = frame_interval
        self.max_frames = max_frames

    async def process(self, file: UploadFile, db: Session) -> models.Video:
        video_path = await self._persist_file(file)
        key_frames = self._extract_key_frames(video_path)
        detected_objects = self._detect_objects(key_frames)
        summary = self._summarize(detected_objects)

        video = models.Video(
            filename=file.filename,
            storage_path=video_path,
            key_frames=key_frames,
            detected_objects=detected_objects,
            summary=summary,
        )
        db.add(video)
        db.commit()
        db.refresh(video)
        return video

    async def _persist_file(self, file: UploadFile) -> str:
        dest_path = os.path.join(self.settings.storage.video_input_dir, file.filename)
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        contents = await file.read()
        with open(dest_path, "wb") as buffer:
            buffer.write(contents)
        await file.seek(0)
        return dest_path

    def _extract_key_frames(self, video_path: str) -> List[str]:
        capture = cv2.VideoCapture(video_path)
        saved_frames: List[str] = []
        success, frame = capture.read()
        frame_idx = 0

        while success and len(saved_frames) < self.max_frames:
            if frame_idx % self.frame_interval == 0:
                frame_name = f"{Path(video_path).stem}_frame_{frame_idx:04d}.jpg"
                frame_path = os.path.join(self.settings.storage.key_frame_dir, frame_name)
                os.makedirs(os.path.dirname(frame_path), exist_ok=True)
                cv2.imwrite(frame_path, frame)
                saved_frames.append(frame_path)
            success, frame = capture.read()
            frame_idx += 1

        capture.release()
        if not saved_frames:
            saved_frames.append(video_path)
        return saved_frames

    def _detect_objects(self, key_frames: List[str]) -> List[str]:
        objects: set[str] = set()
        for frame_path in key_frames:
            frame = cv2.imread(frame_path)
            if frame is None:
                continue
            brightness = frame.mean()
            if brightness > 180:
                objects.add("bright-scene")
            elif brightness > 120:
                objects.add("well-lit-scene")
            else:
                objects.add("low-light-scene")

            if frame.shape[1] > frame.shape[0]:
                objects.add("landscape")
            else:
                objects.add("portrait")

        return sorted(objects) if objects else ["unclassified"]

    def _summarize(self, detected_objects: List[str]) -> str:
        return (
            "Detected objects: " + ", ".join(detected_objects)
            if detected_objects
            else "No objects detected."
        )

