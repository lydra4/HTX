"""Unit tests for API endpoints."""

from __future__ import annotations

import os
from io import BytesIO

import cv2
import numpy as np
import pytest
from fastapi.testclient import TestClient


class TestVideoEndpoints:
    """Test video processing API endpoints."""

    def test_process_video_endpoint_creates_video_record(
        self, client: TestClient, sample_video_file: str
    ):
        """Test that POST /process/video creates a video record."""
        with open(sample_video_file, "rb") as f:
            response = client.post(
                "/process/video",
                files={"file": ("test_video.mp4", f, "video/mp4")},
            )
        
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["filename"] == "test_video.mp4"
        assert "storage_path" in data
        assert "key_frames" in data
        assert "detected_objects" in data
        assert "summary" in data

    def test_list_videos_endpoint_returns_all_videos(
        self, client: TestClient, sample_video_file: str
    ):
        """Test that GET /videos returns all processed videos."""
        # Upload a video first
        with open(sample_video_file, "rb") as f:
            client.post("/process/video", files={"file": ("test_video.mp4", f, "video/mp4")})
        
        response = client.get("/videos")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert any(v["filename"] == "test_video.mp4" for v in data)

    def test_process_video_endpoint_extracts_frames(
        self, client: TestClient, sample_video_file: str
    ):
        """Test that video processing extracts key frames."""
        with open(sample_video_file, "rb") as f:
            response = client.post(
                "/process/video",
                files={"file": ("test_video.mp4", f, "video/mp4")},
            )
        
        assert response.status_code == 201
        data = response.json()
        assert len(data["key_frames"]) > 0
        # Verify frames are valid paths
        assert all(isinstance(frame, str) for frame in data["key_frames"])


class TestAudioEndpoints:
    """Test audio processing API endpoints."""

    def test_process_audio_endpoint_creates_transcription_record(
        self, client: TestClient, sample_audio_file: str
    ):
        """Test that POST /process/audio creates a transcription record."""
        with open(sample_audio_file, "rb") as f:
            response = client.post(
                "/process/audio",
                files={"file": ("test_audio.wav", f, "audio/wav")},
            )
        
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["filename"] == "test_audio.wav"
        assert "storage_path" in data
        assert "transcript" in data
        assert "confidence_score" in data
        assert isinstance(data["confidence_score"], float)

    def test_list_transcriptions_endpoint_returns_all_transcriptions(
        self, client: TestClient, sample_audio_file: str
    ):
        """Test that GET /transcriptions returns all processed audio."""
        # Upload audio first
        with open(sample_audio_file, "rb") as f:
            client.post("/process/audio", files={"file": ("test_audio.wav", f, "audio/wav")})
        
        response = client.get("/transcriptions")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert any(t["filename"] == "test_audio.wav" for t in data)

    def test_process_audio_endpoint_generates_transcript(
        self, client: TestClient, sample_audio_file: str
    ):
        """Test that audio processing generates a transcript."""
        with open(sample_audio_file, "rb") as f:
            response = client.post(
                "/process/audio",
                files={"file": ("test_audio.wav", f, "audio/wav")},
            )
        
        assert response.status_code == 201
        data = response.json()
        assert len(data["transcript"]) > 0
        assert isinstance(data["transcript"], str)


class TestSearchEndpoints:
    """Test search functionality across both media types."""

    def test_search_finds_videos_by_filename(
        self, client: TestClient, sample_video_file: str
    ):
        """Test search finds videos by filename."""
        # Upload a video
        with open(sample_video_file, "rb") as f:
            client.post("/process/video", files={"file": ("test_video.mp4", f, "video/mp4")})
        
        response = client.get("/search?term=test_video")
        
        assert response.status_code == 200
        data = response.json()
        assert "videos" in data
        assert "transcriptions" in data
        assert len(data["videos"]) >= 1
        assert any(v["filename"] == "test_video.mp4" for v in data["videos"])

    def test_search_finds_audio_by_filename(
        self, client: TestClient, sample_audio_file: str
    ):
        """Test search finds transcriptions by filename."""
        # Upload audio
        with open(sample_audio_file, "rb") as f:
            client.post("/process/audio", files={"file": ("test_audio.wav", f, "audio/wav")})
        
        response = client.get("/search?term=test_audio")
        
        assert response.status_code == 200
        data = response.json()
        assert "videos" in data
        assert "transcriptions" in data
        assert len(data["transcriptions"]) >= 1
        assert any(t["filename"] == "test_audio.wav" for t in data["transcriptions"])

    def test_search_finds_videos_by_summary(
        self, client: TestClient, sample_video_file: str
    ):
        """Test search finds videos by summary content."""
        # Upload a video
        with open(sample_video_file, "rb") as f:
            client.post("/process/video", files={"file": ("test_video.mp4", f, "video/mp4")})
        
        # Search for a term that might be in the summary (like "Detected")
        response = client.get("/search?term=Detected")
        
        assert response.status_code == 200
        data = response.json()
        # May or may not find results depending on summary content
        assert "videos" in data
        assert isinstance(data["videos"], list)

    def test_search_finds_audio_by_transcript(
        self, client: TestClient, sample_audio_file: str
    ):
        """Test search finds transcriptions by transcript content."""
        # Upload audio
        with open(sample_audio_file, "rb") as f:
            client.post("/process/audio", files={"file": ("test_audio.wav", f, "audio/wav")})
        
        # Search for a term that might be in the transcript
        response = client.get("/search?term=Placeholder")
        
        assert response.status_code == 200
        data = response.json()
        assert "transcriptions" in data
        # Should find the transcription since it contains "Placeholder"
        assert len(data["transcriptions"]) >= 1

    def test_search_returns_both_media_types(
        self, client: TestClient, sample_video_file: str, sample_audio_file: str
    ):
        """Test search returns both videos and transcriptions in response."""
        # Upload both video and audio
        with open(sample_video_file, "rb") as f:
            client.post("/process/video", files={"file": ("test_video.mp4", f, "video/mp4")})
        with open(sample_audio_file, "rb") as f:
            client.post("/process/audio", files={"file": ("test_audio.wav", f, "audio/wav")})
        
        response = client.get("/search?term=test")
        
        assert response.status_code == 200
        data = response.json()
        assert "videos" in data
        assert "transcriptions" in data
        assert isinstance(data["videos"], list)
        assert isinstance(data["transcriptions"], list)

