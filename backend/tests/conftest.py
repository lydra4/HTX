"""Shared pytest fixtures for backend tests."""

from __future__ import annotations

import os
import tempfile

import cv2
import numpy as np
import pytest
from fastapi.testclient import TestClient
from omegaconf import OmegaConf
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.app import create_app
from backend.models import Base
from backend.settings import AppSettings, build_settings


@pytest.fixture
def temp_dir() -> str:
    """Create a temporary directory for test data."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def test_settings(temp_dir: str) -> AppSettings:
    """Create test settings with temporary directories."""
    config_dict = {
        "raw_data_dir": os.path.join(temp_dir, "raw"),
        "preprocessing_data_dir": os.path.join(temp_dir, "preprocessed"),
        "processed_data_dir": os.path.join(temp_dir, "processed"),
        "storage": {
            "video_subdir": "videos",
            "audio_subdir": "audio",
            "keyframes_subdir": "keyframes",
        },
        "database": {"url": f"sqlite:///{os.path.join(temp_dir, 'test.db')}"},
        "backend": {"host": "127.0.0.1", "port": 8000, "reload": False},
    }
    return build_settings(config_dict, project_root=temp_dir)


@pytest.fixture
def db_session(test_settings: AppSettings) -> Session:
    """Create a test database session."""
    engine = create_engine(test_settings.database.url)
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_app(test_settings: AppSettings):
    """Create a test FastAPI app."""
    cfg = OmegaConf.create(
        {
            "raw_data_dir": test_settings.storage.raw_data_dir,
            "preprocessing_data_dir": test_settings.storage.preprocessing_data_dir,
            "processed_data_dir": test_settings.storage.processed_data_dir,
            "storage": {
                "video_subdir": "videos",
                "audio_subdir": "audio",
                "keyframes_subdir": "keyframes",
            },
            "database": {"url": test_settings.database.url},
            "backend": {
                "host": "127.0.0.1",
                "port": 8000,
                "reload": False,
            },
        }
    )
    app = create_app(cfg, project_root=test_settings.project_root)
    return app


@pytest.fixture
def client(test_app):
    """Create a test client."""
    return TestClient(test_app)


@pytest.fixture
def sample_video_file(temp_dir: str) -> str:
    """Create a sample video file for testing."""
    video_path = os.path.join(temp_dir, "test_video.mp4")
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(video_path, fourcc, 20.0, (640, 480))
    
    # Write 60 frames (3 seconds at 20 fps)
    for i in range(60):
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        out.write(frame)
    out.release()
    
    return video_path


@pytest.fixture
def sample_audio_file(temp_dir: str) -> str:
    """Create a sample audio file for testing."""
    audio_path = os.path.join(temp_dir, "test_audio.wav")
    # Create a minimal WAV file header (44 bytes) + some data
    with open(audio_path, "wb") as f:
        # WAV header
        f.write(b"RIFF")
        f.write((36).to_bytes(4, "little"))  # File size - 8
        f.write(b"WAVE")
        f.write(b"fmt ")
        f.write((16).to_bytes(4, "little"))  # fmt chunk size
        f.write((1).to_bytes(2, "little"))  # Audio format (PCM)
        f.write((1).to_bytes(2, "little"))  # Number of channels
        f.write((44100).to_bytes(4, "little"))  # Sample rate
        f.write((88200).to_bytes(4, "little"))  # Byte rate
        f.write((2).to_bytes(2, "little"))  # Block align
        f.write((16).to_bytes(2, "little"))  # Bits per sample
        f.write(b"data")
        f.write((1000).to_bytes(4, "little"))  # Data size
        # Some dummy audio data
        f.write(b"\x00" * 1000)
    return audio_path

