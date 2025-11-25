from typing import Any

from fastapi import FastAPI
from omegaconf import DictConfig, OmegaConf

from backend.database import init_database
from backend.routes import audio, health, search, videos
from backend.services.audio_processor import AudioProcessor
from backend.services.video_processor import VideoProcessor
from backend.settings import AppSettings, build_settings, ensure_storage_dirs


def create_app(cfg: DictConfig, project_root: str | None = None) -> FastAPI:
    """FastAPI application factory."""
    settings = _build_settings(cfg=cfg, project_root=project_root)
    ensure_storage_dirs(settings)
    init_database(database_url=settings.database.url)

    app = FastAPI(
        title="HTX Media Intelligence Backend",
        version="0.1.0",
        docs_url="/",
    )
    app.state.settings = settings
    app.state.video_processor = VideoProcessor(settings=settings)
    app.state.audio_processor = AudioProcessor(settings=settings)

    app.include_router(health.router, tags=["health"])
    app.include_router(videos.router, tags=["videos"])
    app.include_router(audio.router, tags=["audio"])
    app.include_router(search.router, tags=["search"])

    return app


def _build_settings(cfg: DictConfig, project_root: str | None) -> AppSettings:
    resolved: dict[str, Any] = OmegaConf.to_container(
        cfg, resolve=True, throw_on_missing=True
    )  # type: ignore[assignment]
    return build_settings(resolved, project_root=project_root)

