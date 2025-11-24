import logging
import os
import sqlite3
import time
from typing import Any, List, Optional, Tuple

import cv2
import torch
from omegaconf import DictConfig
from tqdm import tqdm
from transformers import pipeline
from ultralytics.models import YOLO

from utils.general_utils import init_db


class ExtractionPipeline:
    def __init__(
        self,
        cfg: DictConfig,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self.cfg = cfg
        self.logger = logger or logging.getLogger(__name__)

        self.device_video = "cuda" if torch.cuda.is_available() else "cpu"
        self.logger.info(f"Using device: {self.device_video}.")
        self.device_audio = 0 if torch.cuda.is_available() else -1

        self.video_model = YOLO(model=self.cfg.video.video_model).to(self.device_video)
        self.audio_model = pipeline(device=self.device_audio, **self.cfg.audio)

    def _get_video_list(
        self,
        dir_path: str,
        extension: str = ".mp4",
    ) -> List[str]:
        return [
            os.path.join(dir_path, file)
            for file in os.listdir(dir_path)
            if file.endswith(extension)
        ]

    def _process_video(self, db_path: str, video_path: str) -> None:
        video_name = os.path.basename(video_path)
        self.logger.info(f"Processing {video_name}.")

        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS) or None
        cap.release()

        if not fps or fps <= 0:
            fps = 30

        frame_interval = int(fps)
        results = self.video_model.predict(
            source=video_path,
            stream=True,
            vid_stride=frame_interval,
            verbose=True,
        )

        db_buffer: List[Tuple] = []

        for i, result in enumerate(results):
            actual_frame_idx = i * frame_interval
            timestamp_sec = actual_frame_idx / fps

            if result.boxes is None:
                continue

            for box in result.boxes:  # type: ignore[attr-defined]
                try:
                    cls_vals = getattr(box, "cls", None)
                    if cls_vals is not None:
                        cls_id = int(cls_vals[0].item())
                        object_name = self.video_model.names.get(cls_id, str(cls_id))
                    else:
                        object_name = "unknown"

                    db_buffer.append(
                        (video_name, object_name, actual_frame_idx, timestamp_sec)
                    )

                except Exception:
                    self.logger.exception(f"Error parsing box for {video_name}.")

        if db_buffer:
            with sqlite3.connect(database=db_path) as conn:
                cursor = conn.cursor()
                cursor.executemany(
                    """
                    INSERT INTO video_events (file_name, object_name, frame, timestamp)
                    VALUES (?, ?, ?, ?)
                    """,
                    db_buffer,
                )
                conn.commit()

    def _extract_audio(self, video_path: str) -> str:
        audio_path = video_path.replace(".mp4", ".wav")
        cmd = (
            f"ffmpeg -y -i '{video_path}' -vn "
            f"-acodec pcm_s16le -ar 16000 -ac 1 '{audio_path}'"
        )
        os.system(cmd)
        return audio_path

    def _process_audio(self, db_path: str, audio_path: str) -> None:
        audio_name = os.path.basename(audio_path)

        output: Any = self.audio_model(audio_path, return_timestamps=True)

        segments = output.get("chunks", [])
        db_buffer = [
            (
                audio_name,
                seg.get("text", ""),
                *(seg.get("timestamp") or (None, None)),
            )
            for seg in segments
            if seg.get("timestamp") is not None and seg["timestamp"][1] is not None
        ]

        if db_buffer:
            with sqlite3.connect(database=db_path) as conn:
                cursor = conn.cursor()
                cursor.executemany(
                    """
                    INSERT INTO audio_events (file_name, transcript, start, end)
                    VALUES (?, ?, ?, ?)
                    """,
                    db_buffer,
                )
                conn.commit()

    def run(self) -> None:
        start_time = time.time()

        init_db(
            db_path=self.cfg.database.db_path,
            sql_statements=[
                self.cfg.database.video_events,
                self.cfg.database.audio_events,
            ],
        )
        video_paths = self._get_video_list(dir_path=self.cfg.dir_path)
        for video_path in tqdm(video_paths):
            self.logger.info(f"Processing {os.path.basename(video_path)}.")
            self._process_video(
                db_path=self.cfg.database.db_path,
                video_path=video_path,
            )
            audio_path = self._extract_audio(video_path=video_path)
            self._process_audio(
                db_path=self.cfg.database.db_path,
                audio_path=audio_path,
            )

        elapsed = time.time() - start_time
        minutes, seconds = divmod(elapsed, 60)
        self.logger.info(f"Extraction took {int(minutes)}m {seconds:.2f}s.")
