import heapq
import logging
import sqlite3
from typing import List, Optional, Tuple

import numpy as np
from omegaconf import DictConfig
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

from utils.general_utils import cosine_similarity, init_db


class EmbeddingsGenerator:
    def __init__(
        self,
        cfg: DictConfig,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self.cfg = cfg
        self.logger = logger or logging.getLogger(__name__)
        self.sentence_transformer = SentenceTransformer(
            model_name_or_path=self.cfg.sentence_transformer
        )
        init_db(
            db_path=self.cfg.database.embeddings_db_path,
            sql_statements=[self.cfg.database.create_embeddings_table],
        )

    def _vector_to_blob(self, vector: np.ndarray) -> bytes:
        return vector.astype("float32").tobytes()

    def _blob_to_vector(self, blob: bytes) -> np.ndarray:
        return np.frombuffer(buffer=blob, dtype="float32")

    def _generate_embeddings_mode(
        self,
        source_db_path: str,
        embeddings_db_path: str,
        modality: str,
    ) -> None:
        self.logger.info(f"Generating embeddings for {modality}.")

        with sqlite3.connect(database=source_db_path) as read_conn:
            read_cursor = read_conn.cursor()
            if modality == "video":
                read_cursor.execute("SELECT file_name, object_name FROM video_events")
            else:
                read_cursor.execute("SELECT file_name, transcript FROM audio_events")

            rows = read_cursor.fetchall()

        with sqlite3.connect(database=embeddings_db_path) as write_conn:
            write_cursor = write_conn.cursor()

            pbar = tqdm(
                total=len(rows),
                desc=f"Embedding {modality}",
                dynamic_ncols=True,
                leave=True,
            )

            for file_name, object_name in rows:
                vec = self.sentence_transformer.encode(
                    object_name,
                    show_progress_bar=False,
                )
                blob = self._vector_to_blob(vector=vec)
                write_cursor.execute(
                    """
                    INSERT INTO embeddings (modality, file_name, vector)
                    VALUES (?, ?, ?)
                    """,
                    (modality, file_name, blob),
                )
                pbar.update(1)

            pbar.close()
            write_conn.commit()

        self.logger.info(f"Embeddings completed for {modality}.")

    def generate_embeddings(self) -> None:
        self._generate_embeddings_mode(
            source_db_path=self.cfg.database.source_db_path,
            embeddings_db_path=self.cfg.database.embeddings_db_path,
            modality="video",
        )
        self._generate_embeddings_mode(
            source_db_path=self.cfg.database.source_db_path,
            embeddings_db_path=self.cfg.database.embeddings_db_path,
            modality="audio",
        )

    def perform_retrieval(
        self, db_path: str, query: str, top_k: int
    ) -> List[Tuple[str, float]]:
        query_vec = np.asarray(
            self.sentence_transformer.encode(query),
            dtype="float32",
        )
        with sqlite3.connect(database=db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT file_name, vector FROM embeddings")
            results = []
            for file_name, blob in cursor.fetchall():
                vec = self._blob_to_vector(blob=blob)
                score = cosine_similarity(a=query_vec, b=vec)
                results.append((file_name, score))

        return heapq.nlargest(top_k, results, key=lambda x: x[1])
