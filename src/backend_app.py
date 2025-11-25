import os

import hydra
from omegaconf import DictConfig

from utils.general_utils import setup_logging


@hydra.main(
    version_base=None,
    config_path="../config",
    config_name="backend_app.yaml",
)
def main(cfg: DictConfig):
    # logger = logging.getLogger(__name__)
    setup_logging(
        logging_config_path=os.path.join(
            hydra.utils.get_original_cwd(), "config", "logging.yaml"
        )
    )


if __name__ == "__main__":
    main()
