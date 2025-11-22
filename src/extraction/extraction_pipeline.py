import logging
import os
import sqlite3
from sqlite3 import Connection
from typing import Any, List, Optional

import cv2
from omegaconf import DictConfig
from tqdm import tqdm
from transformers import pipeline
from ultralytics.models import YOLO


class ExtractionPipeline:
    def __init__(
        self,
        cfg: DictConfig,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self.cfg = cfg
        self.logger = logger or logging.getLogger(__name__)
        self.video_model = YOLO(model=self.cfg.video.video_model)
        self.audio_model = pipeline(**self.cfg.audio)

    def _init_db(
        self,
        db_path: str,
        video_events: str,
        audio_events: str,
    ) -> None:
        conn = sqlite3.connect(database=db_path)
        cursor = conn.cursor()
        cursor.execute(video_events)
        cursor.execute(audio_events)
        conn.commit()

    def _get_video_list(
        self,
        dir_path: str,
        extension: str = ".mp4",
    ) -> List[str]:
        video_list = [
            os.path.join(dir_path, file)
            for file in os.listdir(dir_path)
            if file.endswith(extension)
        ]
        return video_list

    def _insert_video_event(
        self,
        conn: Connection,
        file_name: str,
        object_name: str,
        frame: int,
        timestamp: float,
    ) -> None:
        cursor = conn.cursor()
        cursor.execute(
            """
                       INSERT INTO video_events (file_name, object_name, frame, timestamp)
                        VALUES (?, ?, ?, ?)
                        """,
            (file_name, object_name, frame, timestamp),
        )
        conn.commit()

    def _insert_audio_event(
        self,
        conn: Connection,
        file_name: str,
        transcript: str,
        start: float,
        end: float,
    ) -> None:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO audio_events (file_name, transcript, start, end)
            VALUES (?, ?, ?, ?)
            """,
            (file_name, transcript, start, end),
        )
        conn.commit()

    def _process_video(self, db_path: str, video_path: str) -> None:
        conn = sqlite3.connect(database=db_path)
        cursor = conn.cursor()
        video_name = os.path.basename(video_path)

        self.logger.info(f"Processing {video_name}.")
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS) or None
        cap.release()
        results = self.video_model.predict(source=video_path, stream=True)

        for frame_idx, result in enumerate(results):
            if fps and fps > 0:
                timestamp_sec = frame_idx / float(fps)
            else:
                timestamp_sec = None

            if result.boxes is None:
                continue

            for box in result.boxes:  # type: ignore[attr-defined]
                try:
                    cls_vals = getattr(box, "cls", None)
                    if cls_vals is None:
                        object_name = "unknown"
                    else:
                        try:
                            cls_id = int(cls_vals[0].item())
                        except Exception:
                            try:
                                cls_id = int(cls_vals[0])
                            except Exception:
                                cls_id = 0
                        object_name = self.video_model.names.get(cls_id, str(cls_id))

                    cursor.execute(
                        """
                        INSERT INTO video_events (file_name, object_name, frame, timestamp)
                        VALUES (?, ?, ?, ?)
                        """,
                        (video_name, object_name, frame_idx, timestamp_sec),
                    )

                except Exception:
                    self.logger.exception(
                        f"Failed inserting video event for {video_name} at {frame_idx}."
                    )

        conn.commit()
        conn.close()

    def _process_audio(self, db_path: str, audio_path: str) -> None:
        conn = sqlite3.connect(db_path)
        audio_name = os.path.basename(audio_path)
        output: Any = self.audio_model(audio_path, return_timestamps=True)

        if isinstance(output, list):
            output = output[0]

        segments = output.get("chunks") or output.get("segments") or []

        cursor = conn.cursor()
        for seg in segments:
            cursor.execute(
                """
                INSERT INTO audio_events (file_name, transcript, start, end)
                VALUES (?, ?, ?, ?)

                        """,
                (audio_name, seg["text"], seg["start"], seg["end"]),
            )

        conn.commit()
        conn.close()

    def run(self) -> None:
        self._init_db(
            db_path=self.cfg.database.db_path,
            video_events=self.cfg.database.video_events,
            audio_events=self.cfg.database.audio_events,
        )
        video_paths = self._get_video_list(dir_path=self.cfg.dir_path)
        for video_path in tqdm(video_paths):
            self.logger.info(f"Processing {os.path.basename(video_path)}.")
            self._process_video(
                db_path=self.cfg.database.db_path,
                video_path=video_path,
            )
            self._process_audio(
                db_path=self.cfg.database.db_path,
                audio_path=video_path,
            )
