from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict


@dataclass(slots=True)
class StorageSettings:
    raw_data_dir: str
    preprocessing_data_dir: str
    processed_data_dir: str
    video_input_dir: str
    audio_input_dir: str
    key_frame_dir: str


@dataclass(slots=True)
class DatabaseSettings:
    url: str


@dataclass(slots=True)
class ServerSettings:
    host: str
    port: int
    reload: bool


@dataclass(slots=True)
class AppSettings:
    storage: StorageSettings
    database: DatabaseSettings
    server: ServerSettings
    project_root: str


def build_settings(config: Dict[str, Any], project_root: str | None = None) -> AppSettings:
    base_path = project_root or os.getcwd()

    def _resolve(path: str) -> str:
        return path if os.path.isabs(path) else os.path.abspath(os.path.join(base_path, path))

    storage_config: Dict[str, Any] = config.get("storage", {})
    raw_dir = _resolve(config.get("raw_data_dir", "./data/01-raw"))
    preprocessing_dir = _resolve(config.get("preprocessing_data_dir", "./data/02-preprocessed"))
    processed_dir = _resolve(config.get("processed_data_dir", "./data/03-processed"))

    video_subdir = storage_config.get("video_subdir", "videos")
    audio_subdir = storage_config.get("audio_subdir", "audio")
    keyframe_subdir = storage_config.get("keyframes_subdir", "keyframes")

    storage = StorageSettings(
        raw_data_dir=raw_dir,
        preprocessing_data_dir=preprocessing_dir,
        processed_data_dir=processed_dir,
        video_input_dir=os.path.join(raw_dir, video_subdir),
        audio_input_dir=os.path.join(raw_dir, audio_subdir),
        key_frame_dir=os.path.join(processed_dir, keyframe_subdir),
    )

    database_config: Dict[str, Any] = config.get("database", {})
    database_url = database_config.get("url", "sqlite:///./backend.db")
    if database_url.startswith("sqlite:///"):
        sqlite_path = database_url.replace("sqlite:///", "", 1)
        database_url = f"sqlite:///{_resolve(sqlite_path)}"

    database = DatabaseSettings(url=database_url)

    backend_config: Dict[str, Any] = config.get("backend", {})
    server = ServerSettings(
        host=backend_config.get("host", "0.0.0.0"),
        port=int(backend_config.get("port", 8000)),
        reload=bool(backend_config.get("reload", False)),
    )

    return AppSettings(
        storage=storage,
        database=database,
        server=server,
        project_root=base_path,
    )


def ensure_storage_dirs(settings: AppSettings) -> None:
    os.makedirs(settings.storage.raw_data_dir, exist_ok=True)
    os.makedirs(settings.storage.preprocessing_data_dir, exist_ok=True)
    os.makedirs(settings.storage.processed_data_dir, exist_ok=True)
    os.makedirs(settings.storage.video_input_dir, exist_ok=True)
    os.makedirs(settings.storage.audio_input_dir, exist_ok=True)
    os.makedirs(settings.storage.key_frame_dir, exist_ok=True)

