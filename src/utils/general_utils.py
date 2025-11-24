import logging
import logging.config
import os
import sqlite3
from typing import Sequence

import numpy as np
import yaml

logger = logging.getLogger(__name__)


def setup_logging(
    logging_config_path: str = "../conf/logging.yaml",
    default_level: int = logging.INFO,
) -> None:
    try:
        os.makedirs("logs", exist_ok=True)
        with open(logging_config_path, encoding="utf-8") as file:
            log_config = yaml.safe_load(file.read())
        logging.config.dictConfig(log_config)

    except Exception as error:
        logging.basicConfig(
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            level=default_level,
        )
        logger.info(error)
        logger.info("Logging config file is not found. Basic config is used.")


def init_db(
    db_path: str,
    sql_statements: Sequence[str],
) -> None:
    with sqlite3.connect(database=db_path) as conn:
        cursor = conn.cursor()
        for statement in sql_statements:
            cursor.execute(statement)
        conn.commit()


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return np.dot(a=a, b=b) / (np.linalg.norm(a) * np.linalg.norm(b))
