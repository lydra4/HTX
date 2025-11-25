"""Unit tests for video processing functionality."""

from __future__ import annotations

import os
from io import BytesIO

import cv2
import numpy as np
import pytest
from fastapi import UploadFile
from sqlalchemy.orm import Session

from backend.services.video_processor import VideoProcessor


class TestVideoFrameExtraction:
    """Test video frame extraction logic."""

    def test_extract_key_frames_extracts_correct_number(
        self, test_settings, db_session: Session, sample_video_file: str
    ):
        """Test that key frames are extracted at the correct intervals."""
        processor = VideoProcessor(settings=test_settings, frame_interval=10, max_frames=3)
        
        key_frames = processor._extract_key_frames(sample_video_file)
        
        # Should extract frames at indices 0, 10, 20 (3 frames max)
        assert len(key_frames) == 3
        assert all(os.path.exists(
            os.path.join(test_settings.storage.processed_data_dir, frame)
        ) for frame in key_frames)

    def test_extract_key_frames_respects_max_frames(
        self, test_settings, db_session: Session, sample_video_file: str
    ):
        """Test that max_frames limit is respected."""
        processor = VideoProcessor(settings=test_settings, frame_interval=5, max_frames=2)
        
        key_frames = processor._extract_key_frames(sample_video_file)
        
        assert len(key_frames) <= 2

    def test_extract_key_frames_creates_valid_images(
        self, test_settings, db_session: Session, sample_video_file: str
    ):
        """Test that extracted frames are valid image files."""
        processor = VideoProcessor(settings=test_settings, frame_interval=15, max_frames=2)
        
        key_frames = processor._extract_key_frames(sample_video_file)
        
        for frame_path in key_frames:
            full_path = os.path.join(test_settings.storage.processed_data_dir, frame_path)
            img = cv2.imread(full_path)
            assert img is not None
            assert img.shape == (480, 640, 3)


class TestObjectDetection:
    """Test object detection accuracy."""

    def test_detect_objects_classifies_bright_scene(
        self, test_settings, db_session: Session, temp_dir: str
    ):
        """Test detection of bright scenes based on brightness threshold."""
        processor = VideoProcessor(settings=test_settings)
        
        # Create a bright frame
        bright_frame_path = os.path.join(temp_dir, "bright_frame.jpg")
        bright_frame = np.full((480, 640, 3), 200, dtype=np.uint8)
        cv2.imwrite(bright_frame_path, bright_frame)
        
        rel_path = os.path.relpath(
            bright_frame_path, start=test_settings.storage.processed_data_dir
        ).replace("\\", "/")
        
        detected = processor._detect_objects([rel_path])
        
        assert "bright-scene" in detected

    def test_detect_objects_classifies_landscape_orientation(
        self, test_settings, db_session: Session, temp_dir: str
    ):
        """Test detection of landscape orientation."""
        processor = VideoProcessor(settings=test_settings)
        
        # Create a landscape frame (width > height)
        landscape_frame_path = os.path.join(temp_dir, "landscape_frame.jpg")
        landscape_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.imwrite(landscape_frame_path, landscape_frame)
        
        rel_path = os.path.relpath(
            landscape_frame_path, start=test_settings.storage.processed_data_dir
        ).replace("\\", "/")
        
        detected = processor._detect_objects([rel_path])
        
        assert "landscape" in detected

    def test_detect_objects_classifies_portrait_orientation(
        self, test_settings, db_session: Session, temp_dir: str
    ):
        """Test detection of portrait orientation."""
        processor = VideoProcessor(settings=test_settings)
        
        # Create a portrait frame (height > width)
        portrait_frame_path = os.path.join(temp_dir, "portrait_frame.jpg")
        portrait_frame = np.zeros((640, 480, 3), dtype=np.uint8)
        cv2.imwrite(portrait_frame_path, portrait_frame)
        
        rel_path = os.path.relpath(
            portrait_frame_path, start=test_settings.storage.processed_data_dir
        ).replace("\\", "/")
        
        detected = processor._detect_objects([rel_path])
        
        assert "portrait" in detected

    def test_detect_objects_handles_multiple_frames(
        self, test_settings, db_session: Session, temp_dir: str
    ):
        """Test object detection aggregates results from multiple frames."""
        processor = VideoProcessor(settings=test_settings)
        
        # Create frames with different properties
        frame1_path = os.path.join(temp_dir, "frame1.jpg")
        frame2_path = os.path.join(temp_dir, "frame2.jpg")
        cv2.imwrite(frame1_path, np.full((480, 640, 3), 200, dtype=np.uint8))
        cv2.imwrite(frame2_path, np.zeros((640, 480, 3), dtype=np.uint8))
        
        rel_paths = [
            os.path.relpath(f, start=test_settings.storage.processed_data_dir).replace("\\", "/")
            for f in [frame1_path, frame2_path]
        ]
        
        detected = processor._detect_objects(rel_paths)
        
        # Should contain objects from both frames
        assert len(detected) > 1
        assert "bright-scene" in detected or "well-lit-scene" in detected
        assert "portrait" in detected

