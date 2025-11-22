import logging
import os
import sqlite3
from sqlite3 import Connection
from typing import Optional, Sequence, Union

from omegaconf import DictConfig
from transformers import pipeline
from ultralytics.models import YOLO


class ExtractionPipeline:
    def __init__(
        self,
        cfg: DictConfig,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self.cfg = cfg
        self.logger = logger
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
    ) -> Sequence[Union[str, None]]:
        video_list = [file for file in os.listdir(dir_path) if file.endswith(extension)]
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
