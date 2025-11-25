import os

import hydra
import uvicorn
from omegaconf import DictConfig

from backend import create_app
from utils.general_utils import setup_logging


@hydra.main(
    version_base=None,
    config_path="../config",
    config_name="backend_app.yaml",
)
def main(cfg: DictConfig):
    setup_logging(
        logging_config_path=os.path.join(
            hydra.utils.get_original_cwd(), "config", "logging.yaml"
        )
    )
    project_root = hydra.utils.get_original_cwd()
    app = create_app(cfg=cfg, project_root=project_root)
    uvicorn.run(
        app,
        host=cfg.backend.host,
        port=cfg.backend.port,
        reload=cfg.backend.reload,
    )


if __name__ == "__main__":
    main()
