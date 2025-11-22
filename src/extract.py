import logging
import os

import hydra
from omegaconf import DictConfig

from extraction.extraction_pipeline import ExtractionPipeline
from utils.general_utils import setup_logging


@hydra.main(
    version_base=None,
    config_path="../config",
    config_name="extract_config.yaml",
)
def main(cfg: DictConfig):
    logger = logging.getLogger(__name__)
    setup_logging(
        logging_config_path=os.path.join(
            hydra.utils.get_original_cwd(), "config", "logging.yaml"
        )
    )
    logger.info("Setting up logging configuration.")

    extraction_pipeline = ExtractionPipeline(cfg=cfg, logger=logger)
    extraction_pipeline.run()


if __name__ == "__main__":
    main()
