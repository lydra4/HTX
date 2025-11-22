import logging
import os

import hydra
from omegaconf import DictConfig

from utils.general_utils import setup_logging


@hydra.main(version_base=None, config_name="../config", config_path="extraction.yaml")
def main(cfg: DictConfig):
    logger = logging.getLogger(__name__)
    setup_logging(
        logging_config_path=os.path.join(
            hydra.utils.get_original_cwd(), "config", "logging.yaml"
        )
    )
    logger.info("Setting up logging configuration.")
