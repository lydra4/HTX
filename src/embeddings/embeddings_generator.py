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
            db_path=self.cfg.database.db_path,
            sql_statements=[self.cfg.database.create_table],
        )

    def _vector_to_blob(self, vector: np.ndarray) -> bytes:
        return vector.astype("float32").tobytes()

    def _blob_to_vector(self, blob: bytes) -> np.ndarray:
        return np.frombuffer(buffer=blob, dtype="float32")

    def _generate_embeddings_mode(self, db_path: str, modality: str) -> None:
        self.logger.info(f"Generating embeddings for {modality}.")
        with sqlite3.connect(database=db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT file_name, object_name FROM video_events")
            rows = cursor.fetchall()

            for file_name, object_name in tqdm(
                rows,
                leave=True,
                dynamic_ncols=True,
            ):
                vec = self.sentence_transformer.encode(object_name)
                blob = self._vector_to_blob(vector=vec)
                cursor.execute(
                    """
                               INSERT INTO embeddings (modality, file_name, vector)
                               VALUES (?, ?, ?)
                               """,
                    (modality, file_name, blob),
                )
            conn.commit()

        self.logger.info(f"Embeddings completed for {modality}.")

    def generate_embeddings(self) -> None:
        self._generate_embeddings_mode(
            db_path=self.cfg.database.db_path,
            modality="video",
        )
        self._generate_embeddings_mode(
            db_path=self.cfg.database.db_path,
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
