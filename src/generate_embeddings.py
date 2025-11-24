import logging
import os

import hydra
from omegaconf import DictConfig

from embeddings.embeddings_generator import EmbeddingsGenerator
from utils.general_utils import setup_logging


@hydra.main(
    version_base=None,
    config_path="../config",
    config_name="generate_embeddings.yaml",
)
def main(cfg: DictConfig):
    logger = logging.getLogger(__name__)
    setup_logging(
        logging_config_path=os.path.join(
            hydra.utils.get_original_cwd(), "config", "logging.yaml"
        )
    )

    generate_embeddings = EmbeddingsGenerator(cfg=cfg, logger=logger)
    generate_embeddings.generate_embeddings()


if __name__ == "__main__":
    main()
