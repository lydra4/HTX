import logging
import os
import sqlite3
from sqlite3 import Connection
from typing import Any, Optional, Sequence, Tuple, Union

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

    def _process_video(self, db_path: str, video_path: str) -> None:
        conn = sqlite3.connect(database=db_path)
        video_name = os.path.basename(video_path)

        self.logger.info(f"Processing {video_name}.")
        results = self.video_model.predict(source=video_path, stream=True)

        for result in results:
            if result.boxes is None:
                continue

            timestamp_sec = result["timestamp"]

            for box in result.boxes:  # type: ignore[attr-defined]
                cls_id = int(box.cls[0].item())
                object_name = self.video_model.names[cls_id]

                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO video_events (file_name, object_name, timestamp)
                    VALUES (?, ?, ?, ?)
                    """,
                    (video_name, object_name, timestamp_sec),
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

    def _process_file(self, args: Tuple[str, str]) -> None:
        db_path, file_path = args
        self._process_video(db_path=db_path, video_path=file_path)
        self._process_audio(db_path=db_path, audio_path=file_path)

    def run(
        self,
        dir_path: str,
        db_path: str,
        extension: str = ".mp4",
    ) -> None:
        pass
