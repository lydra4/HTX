import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { SearchPanel } from "../SearchPanel";
import type { SearchResponse, Video, Transcription } from "../../api/types";

describe("SearchPanel", () => {
  const mockVideos: Video[] = [
    {
      id: 1,
      filename: "video1.mp4",
      storage_path: "/path/to/video1",
      summary: "Detected objects: bright-scene, landscape",
      detected_objects: ["bright-scene", "landscape"],
      key_frames: ["frame1.jpg"],
      created_at: "2024-01-01T00:00:00Z",
    },
    {
      id: 2,
      filename: "video2.mp4",
      storage_path: "/path/to/video2",
      summary: "Detected objects: portrait",
      detected_objects: ["portrait"],
      key_frames: ["frame2.jpg"],
      created_at: "2024-01-02T00:00:00Z",
    },
  ];

  const mockTranscriptions: Transcription[] = [
    {
      id: 1,
      filename: "audio1.wav",
      storage_path: "/path/to/audio1",
      transcript: "This is a test transcription with searchable content",
      confidence_score: 0.95,
      video_id: null,
      created_at: "2024-01-01T00:00:00Z",
    },
    {
      id: 2,
      filename: "audio2.wav",
      storage_path: "/path/to/audio2",
      transcript: "Another transcription for testing purposes",
      confidence_score: 0.88,
      video_id: null,
      created_at: "2024-01-02T00:00:00Z",
    },
  ];

  const mockSearchResponse: SearchResponse = {
    videos: [mockVideos[0]],
    transcriptions: [mockTranscriptions[0]],
  };

  const mockOnTextSearch = vi.fn().mockResolvedValue(mockSearchResponse);
  const mockOnVisualSearch = vi.fn().mockResolvedValue(mockSearchResponse);
  const mockOnAudioSearch = vi.fn().mockResolvedValue(mockSearchResponse);

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("should render search panel with text input and search button", () => {
    render(
      <SearchPanel
        onTextSearch={mockOnTextSearch}
        onVisualSearch={mockOnVisualSearch}
        onAudioSearch={mockOnAudioSearch}
        videos={mockVideos}
        transcriptions={mockTranscriptions}
        results={null}
        isSearching={false}
        activeTerm=""
      />
    );

    expect(screen.getByText("Unified Search")).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/Search objects, transcripts/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Search/i })).toBeInTheDocument();
  });

  it("should perform text search across video and audio content", async () => {
    const user = userEvent.setup();
    render(
      <SearchPanel
        onTextSearch={mockOnTextSearch}
        onVisualSearch={mockOnVisualSearch}
        onAudioSearch={mockOnAudioSearch}
        videos={mockVideos}
        transcriptions={mockTranscriptions}
        results={null}
        isSearching={false}
        activeTerm=""
      />
    );

    const searchInput = screen.getByPlaceholderText(/Search objects, transcripts/i);
    await user.type(searchInput, "test");

    const searchButton = screen.getByRole("button", { name: /Search/i });
    await user.click(searchButton);

    await waitFor(() => {
      expect(mockOnTextSearch).toHaveBeenCalledWith("test");
    });
  });

  it("should display search results for both videos and transcriptions", () => {
    render(
      <SearchPanel
        onTextSearch={mockOnTextSearch}
        onVisualSearch={mockOnVisualSearch}
        onAudioSearch={mockOnAudioSearch}
        videos={mockVideos}
        transcriptions={mockTranscriptions}
        results={mockSearchResponse}
        isSearching={false}
        activeTerm="test"
      />
    );

    expect(screen.getByText(/Matched 1 videos and 1 transcriptions/i)).toBeInTheDocument();
    expect(screen.getByText("video1.mp4")).toBeInTheDocument();
    expect(screen.getByText("audio1.wav")).toBeInTheDocument();
  });

  it("should perform visual search using video reference", async () => {
    const user = userEvent.setup();
    render(
      <SearchPanel
        onTextSearch={mockOnTextSearch}
        onVisualSearch={mockOnVisualSearch}
        onAudioSearch={mockOnAudioSearch}
        videos={mockVideos}
        transcriptions={mockTranscriptions}
        results={null}
        isSearching={false}
        activeTerm=""
      />
    );

    const visualSelect = screen.getByText(/Visual Similarity/i).parentElement?.querySelector("select");
    if (visualSelect) {
      await user.selectOptions(visualSelect, "1");
    }

    await waitFor(() => {
      expect(mockOnVisualSearch).toHaveBeenCalledWith(mockVideos[0]);
    });
  });

  it("should perform audio search using transcription reference", async () => {
    const user = userEvent.setup();
    render(
      <SearchPanel
        onTextSearch={mockOnTextSearch}
        onVisualSearch={mockOnVisualSearch}
        onAudioSearch={mockOnAudioSearch}
        videos={mockVideos}
        transcriptions={mockTranscriptions}
        results={null}
        isSearching={false}
        activeTerm=""
      />
    );

    const audioSelect = screen.getByText(/Audio Similarity/i).parentElement?.querySelector("select");
    if (audioSelect) {
      await user.selectOptions(audioSelect, "1");
    }

    await waitFor(() => {
      expect(mockOnAudioSearch).toHaveBeenCalledWith(mockTranscriptions[0]);
    });
  });

  it("should display cross-media search results", () => {
    const crossMediaResults: SearchResponse = {
      videos: mockVideos,
      transcriptions: mockTranscriptions,
    };

    render(
      <SearchPanel
        onTextSearch={mockOnTextSearch}
        onVisualSearch={mockOnVisualSearch}
        onAudioSearch={mockOnAudioSearch}
        videos={mockVideos}
        transcriptions={mockTranscriptions}
        results={crossMediaResults}
        isSearching={false}
        activeTerm="cross-media search"
      />
    );

    expect(screen.getByText(/Matched 2 videos and 2 transcriptions/i)).toBeInTheDocument();
    expect(screen.getByText("video1.mp4")).toBeInTheDocument();
    expect(screen.getByText("video2.mp4")).toBeInTheDocument();
    expect(screen.getByText("audio1.wav")).toBeInTheDocument();
    expect(screen.getByText("audio2.wav")).toBeInTheDocument();
  });

  it("should disable search button when searching", () => {
    render(
      <SearchPanel
        onTextSearch={mockOnTextSearch}
        onVisualSearch={mockOnVisualSearch}
        onAudioSearch={mockOnAudioSearch}
        videos={mockVideos}
        transcriptions={mockTranscriptions}
        results={null}
        isSearching={true}
        activeTerm=""
      />
    );

    const searchButton = screen.getByRole("button", { name: /Search/i });
    expect(searchButton).toBeDisabled();
    expect(screen.getByText(/Searching…/i)).toBeInTheDocument();
  });

  it("should show empty state when no results", () => {
    render(
      <SearchPanel
        onTextSearch={mockOnTextSearch}
        onVisualSearch={mockOnVisualSearch}
        onAudioSearch={mockOnAudioSearch}
        videos={mockVideos}
        transcriptions={mockTranscriptions}
        results={null}
        isSearching={false}
        activeTerm=""
      />
    );

    expect(screen.getByText(/Run a search to see matches/i)).toBeInTheDocument();
  });
});

