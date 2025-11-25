import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { TranscriptionList } from "../TranscriptionList";
import type { Transcription } from "../../api/types";

describe("TranscriptionList", () => {
  const mockTranscriptions: Transcription[] = [
    {
      id: 1,
      filename: "audio1.wav",
      storage_path: "/path/to/audio1",
      transcript: "This is a test transcription with multiple words to test the timeline synthesis functionality",
      confidence_score: 0.95,
      video_id: null,
      created_at: "2024-01-01T00:00:00Z",
    },
    {
      id: 2,
      filename: "audio2.wav",
      storage_path: "/path/to/audio2",
      transcript: "Another transcription for testing purposes with different content",
      confidence_score: 0.88,
      video_id: 1,
      created_at: "2024-01-02T00:00:00Z",
    },
  ];

  it("should display empty state when no transcriptions", () => {
    render(<TranscriptionList transcriptions={[]} />);

    expect(screen.getByText("Processed Audio")).toBeInTheDocument();
    expect(screen.getByText(/No transcriptions available yet/i)).toBeInTheDocument();
  });

  it("should display transcription items with filenames", () => {
    render(<TranscriptionList transcriptions={mockTranscriptions} />);

    expect(screen.getByText("Processed Audio")).toBeInTheDocument();
    expect(screen.getByText("audio1.wav")).toBeInTheDocument();
    expect(screen.getByText("audio2.wav")).toBeInTheDocument();
  });

  it("should display confidence scores as percentages", () => {
    render(<TranscriptionList transcriptions={mockTranscriptions} />);

    expect(screen.getByText(/95.0%/i)).toBeInTheDocument();
    expect(screen.getByText(/88.0%/i)).toBeInTheDocument();
  });

  it("should display transcript text with timeline segments", () => {
    render(<TranscriptionList transcriptions={mockTranscriptions} />);

    // Check that transcript text is displayed
    expect(screen.getByText(/This is a test transcription/i)).toBeInTheDocument();
    expect(screen.getByText(/Another transcription for testing/i)).toBeInTheDocument();
  });

  it("should display timestamps for transcript segments", () => {
    render(<TranscriptionList transcriptions={mockTranscriptions} />);

    // Check for timestamp format (00:00, 01:00, etc.)
    // Note: getAllByText with regex doesn't work the same way, so we check for presence differently
    const timestampElements = screen.getAllByText(/00:00|01:00|02:00/);
    expect(timestampElements.length).toBeGreaterThan(0);
  });

  it("should call onSelectReference when transcription is selected", async () => {
    const user = userEvent.setup();
    const mockOnSelectReference = vi.fn();

    render(
      <TranscriptionList
        transcriptions={mockTranscriptions}
        onSelectReference={mockOnSelectReference}
      />
    );

    const selectButtons = screen.getAllByText("Use as Audio Anchor");
    await user.click(selectButtons[0]);

    expect(mockOnSelectReference).toHaveBeenCalledWith(mockTranscriptions[0]);
  });

  it("should format created_at timestamp correctly", () => {
    render(<TranscriptionList transcriptions={mockTranscriptions} />);

    // Check that dates are displayed (format may vary by locale)
    const dateElements = screen.getAllByText(/2024/i);
    expect(dateElements.length).toBeGreaterThan(0);
  });

  it("should display transcription count badge", () => {
    render(<TranscriptionList transcriptions={mockTranscriptions} />);

    const badge = screen.getByText("2");
    expect(badge).toBeInTheDocument();
  });

  it("should handle long transcripts by segmenting them", () => {
    const longTranscript: Transcription = {
      id: 3,
      filename: "long_audio.wav",
      storage_path: "/path/to/long_audio",
      transcript:
        "This is a very long transcription that should be split into multiple segments for better readability and user experience when displaying the content",
      confidence_score: 0.92,
      video_id: null,
      created_at: "2024-01-03T00:00:00Z",
    };

    render(<TranscriptionList transcriptions={[longTranscript]} />);

    expect(screen.getByText("long_audio.wav")).toBeInTheDocument();
    // Should have multiple timestamp segments
    const timestampElements = screen.getAllByText(/00:00|01:00|02:00|03:00/);
    expect(timestampElements.length).toBeGreaterThan(1);
  });
});

