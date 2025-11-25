"""Unit tests for audio processing functionality."""

from __future__ import annotations

import os
from io import BytesIO

import pytest
from fastapi import UploadFile
from sqlalchemy.orm import Session

from backend.services.audio_processor import AudioProcessor


class TestAudioTranscription:
    """Test audio transcription accuracy."""

    @pytest.mark.asyncio
    async def test_transcribe_generates_transcript(
        self, test_settings, db_session: Session, sample_audio_file: str
    ):
        """Test that transcription generates a transcript string."""
        processor = AudioProcessor(settings=test_settings)
        
        transcript, confidence = await processor._transcribe(sample_audio_file)
        
        assert isinstance(transcript, str)
        assert len(transcript) > 0
        assert "Placeholder transcription" in transcript

    @pytest.mark.asyncio
    async def test_transcribe_returns_confidence_score(
        self, test_settings, db_session: Session, sample_audio_file: str
    ):
        """Test that transcription returns a confidence score."""
        processor = AudioProcessor(settings=test_settings)
        
        transcript, confidence = await processor._transcribe(sample_audio_file)
        
        assert isinstance(confidence, float)
        assert 0.0 <= confidence <= 1.0

    @pytest.mark.asyncio
    async def test_transcribe_consistent_for_same_file(
        self, test_settings, db_session: Session, sample_audio_file: str
    ):
        """Test that transcription is consistent for the same audio file."""
        processor = AudioProcessor(settings=test_settings)
        
        transcript1, confidence1 = await processor._transcribe(sample_audio_file)
        transcript2, confidence2 = await processor._transcribe(sample_audio_file)
        
        assert transcript1 == transcript2
        assert confidence1 == confidence2

    @pytest.mark.asyncio
    async def test_transcribe_different_for_different_files(
        self, test_settings, db_session: Session, temp_dir: str
    ):
        """Test that different audio files produce different transcripts."""
        processor = AudioProcessor(settings=test_settings)
        
        # Create two different audio files
        audio1_path = os.path.join(temp_dir, "audio1.wav")
        audio2_path = os.path.join(temp_dir, "audio2.wav")
        
        # Create minimal WAV files with different content
        for path, data in [(audio1_path, b"data1"), (audio2_path, b"data2")]:
            with open(path, "wb") as f:
                f.write(b"RIFF")
                f.write((36).to_bytes(4, "little"))
                f.write(b"WAVE")
                f.write(b"fmt ")
                f.write((16).to_bytes(4, "little"))
                f.write((1).to_bytes(2, "little"))
                f.write((1).to_bytes(2, "little"))
                f.write((44100).to_bytes(4, "little"))
                f.write((88200).to_bytes(4, "little"))
                f.write((2).to_bytes(2, "little"))
                f.write((16).to_bytes(2, "little"))
                f.write(b"data")
                f.write((len(data)).to_bytes(4, "little"))
                f.write(data)
        
        transcript1, _ = await processor._transcribe(audio1_path)
        transcript2, _ = await processor._transcribe(audio2_path)
        
        assert transcript1 != transcript2

