import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { UploadPanel } from "../UploadPanel";
import * as client from "../../api/client";

// Mock the API client
vi.mock("../../api/client", () => ({
  uploadMedia: vi.fn(),
}));

describe("UploadPanel", () => {
  const mockOnUploaded = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("should render upload panel with video and audio options", () => {
    render(<UploadPanel onUploaded={mockOnUploaded} />);

    expect(screen.getByText("Upload Media")).toBeInTheDocument();
    expect(screen.getByText("Video")).toBeInTheDocument();
    expect(screen.getByText("Audio")).toBeInTheDocument();
  });

  it("should allow switching between video and audio media types", async () => {
    const user = userEvent.setup();
    render(<UploadPanel onUploaded={mockOnUploaded} />);

    const audioButton = screen.getByText("Audio");
    await user.click(audioButton);

    const fileInput = screen.getByLabelText("Files");
    expect(fileInput).toHaveAttribute("accept", "audio/*");
  });

  it("should handle video file upload", async () => {
    const user = userEvent.setup();
    const mockVideo: client.Video = {
      id: 1,
      filename: "test_video.mp4",
      storage_path: "/path/to/video",
      summary: "Test video",
      detected_objects: ["object1"],
      key_frames: ["frame1.jpg"],
      created_at: "2024-01-01T00:00:00Z",
    };

    vi.mocked(client.uploadMedia).mockResolvedValue([{ video: mockVideo }]);

    render(<UploadPanel onUploaded={mockOnUploaded} />);

    const file = new File(["video content"], "test_video.mp4", { type: "video/mp4" });
    const fileInput = screen.getByLabelText("Files");
    await user.upload(fileInput, file);

    const uploadButton = screen.getByRole("button", { name: /Process Videos/i });
    await user.click(uploadButton);

    await waitFor(() => {
      expect(client.uploadMedia).toHaveBeenCalledWith([file], "video");
      expect(mockOnUploaded).toHaveBeenCalledWith([{ video: mockVideo }]);
    });
  });

  it("should handle audio file upload", async () => {
    const user = userEvent.setup();
    const mockTranscription: client.Transcription = {
      id: 1,
      filename: "test_audio.wav",
      storage_path: "/path/to/audio",
      transcript: "Test transcription",
      confidence_score: 0.95,
      video_id: null,
      created_at: "2024-01-01T00:00:00Z",
    };

    vi.mocked(client.uploadMedia).mockResolvedValue([{ transcription: mockTranscription }]);

    render(<UploadPanel onUploaded={mockOnUploaded} />);

    // Switch to audio mode
    const audioButton = screen.getByText("Audio");
    await user.click(audioButton);

    const file = new File(["audio content"], "test_audio.wav", { type: "audio/wav" });
    const fileInput = screen.getByLabelText("Files");
    await user.upload(fileInput, file);

    const uploadButton = screen.getByRole("button", { name: /Process Audio/i });
    await user.click(uploadButton);

    await waitFor(() => {
      expect(client.uploadMedia).toHaveBeenCalledWith([file], "audio");
      expect(mockOnUploaded).toHaveBeenCalledWith([{ transcription: mockTranscription }]);
    });
  });

  it("should handle multiple file uploads", async () => {
    const user = userEvent.setup();
    const mockVideo1: client.Video = {
      id: 1,
      filename: "video1.mp4",
      storage_path: "/path/to/video1",
      summary: "Video 1",
      detected_objects: [],
      key_frames: [],
      created_at: "2024-01-01T00:00:00Z",
    };
    const mockVideo2: client.Video = {
      id: 2,
      filename: "video2.mp4",
      storage_path: "/path/to/video2",
      summary: "Video 2",
      detected_objects: [],
      key_frames: [],
      created_at: "2024-01-01T00:00:00Z",
    };

    vi.mocked(client.uploadMedia).mockResolvedValue([
      { video: mockVideo1 },
      { video: mockVideo2 },
    ]);

    render(<UploadPanel onUploaded={mockOnUploaded} />);

    const file1 = new File(["content1"], "video1.mp4", { type: "video/mp4" });
    const file2 = new File(["content2"], "video2.mp4", { type: "video/mp4" });
    const fileInput = screen.getByLabelText("Files");
    await user.upload(fileInput, [file1, file2]);

    const uploadButton = screen.getByRole("button", { name: /Process Videos/i });
    await user.click(uploadButton);

    await waitFor(() => {
      expect(client.uploadMedia).toHaveBeenCalledWith([file1, file2], "video");
      expect(mockOnUploaded).toHaveBeenCalledWith([
        { video: mockVideo1 },
        { video: mockVideo2 },
      ]);
    });
  });

  it("should display error message on upload failure", async () => {
    const user = userEvent.setup();
    vi.mocked(client.uploadMedia).mockRejectedValue(new Error("Upload failed"));

    render(<UploadPanel onUploaded={mockOnUploaded} />);

    const file = new File(["content"], "test.mp4", { type: "video/mp4" });
    const fileInput = screen.getByLabelText("Files");
    await user.upload(fileInput, file);

    const uploadButton = screen.getByRole("button", { name: /Process Videos/i });
    await user.click(uploadButton);

    await waitFor(() => {
      expect(screen.getByText(/Upload failed/i)).toBeInTheDocument();
    });
  });
});

