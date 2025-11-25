import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { VideoGallery } from "../VideoGallery";
import type { Video } from "../../api/types";

// Mock the API client
vi.mock("../../api/client", () => ({
  resolveKeyFrameUrl: vi.fn((path: string) => `http://localhost:8000/media/${path}`),
}));

describe("VideoGallery", () => {
  const mockVideos: Video[] = [
    {
      id: 1,
      filename: "test_video1.mp4",
      storage_path: "/path/to/video1",
      summary: "Detected objects: bright-scene, landscape",
      detected_objects: ["bright-scene", "landscape"],
      key_frames: ["keyframes/frame1.jpg", "keyframes/frame2.jpg"],
      created_at: "2024-01-01T00:00:00Z",
    },
    {
      id: 2,
      filename: "test_video2.mp4",
      storage_path: "/path/to/video2",
      summary: "Detected objects: portrait, low-light-scene",
      detected_objects: ["portrait", "low-light-scene"],
      key_frames: ["keyframes/frame3.jpg"],
      created_at: "2024-01-02T00:00:00Z",
    },
  ];

  it("should display empty state when no videos", () => {
    render(<VideoGallery videos={[]} />);

    expect(screen.getByText("Processed Videos")).toBeInTheDocument();
    expect(screen.getByText(/No videos processed yet/i)).toBeInTheDocument();
  });

  it("should display video cards with object detection results", () => {
    render(<VideoGallery videos={mockVideos} />);

    expect(screen.getByText("Processed Videos")).toBeInTheDocument();
    expect(screen.getByText("test_video1.mp4")).toBeInTheDocument();
    expect(screen.getByText("test_video2.mp4")).toBeInTheDocument();
    expect(screen.getByText("Detected objects: bright-scene, landscape")).toBeInTheDocument();
    expect(screen.getByText("Detected objects: portrait, low-light-scene")).toBeInTheDocument();
  });

  it("should display detected objects as badges", () => {
    render(<VideoGallery videos={mockVideos} />);

    expect(screen.getByText("bright-scene")).toBeInTheDocument();
    expect(screen.getByText("landscape")).toBeInTheDocument();
    expect(screen.getByText("portrait")).toBeInTheDocument();
    expect(screen.getByText("low-light-scene")).toBeInTheDocument();
  });

  it("should display key frames for each video", () => {
    render(<VideoGallery videos={mockVideos} />);

    const images = screen.getAllByRole("img");
    // Should have 3 images total (2 from video1, 1 from video2)
    expect(images.length).toBe(3);
    
    images.forEach((img) => {
      expect(img).toHaveAttribute("alt");
      expect(img.getAttribute("alt")).toMatch(/Key frame/i);
    });
  });

  it("should call onSelectReference when video is selected", async () => {
    const user = userEvent.setup();
    const mockOnSelectReference = vi.fn();

    render(<VideoGallery videos={mockVideos} onSelectReference={mockOnSelectReference} />);

    const selectButtons = screen.getAllByText("Use as Visual Anchor");
    await user.click(selectButtons[0]);

    expect(mockOnSelectReference).toHaveBeenCalledWith(mockVideos[0]);
  });

  it("should format created_at timestamp correctly", () => {
    render(<VideoGallery videos={mockVideos} />);

    // Check that dates are displayed (format may vary by locale)
    const dateElements = screen.getAllByText(/2024/i);
    expect(dateElements.length).toBeGreaterThan(0);
  });

  it("should handle videos with no key frames", () => {
    const videoNoFrames: Video = {
      id: 3,
      filename: "no_frames.mp4",
      storage_path: "/path/to/video3",
      summary: "No frames",
      detected_objects: [],
      key_frames: [],
      created_at: "2024-01-03T00:00:00Z",
    };

    render(<VideoGallery videos={[videoNoFrames]} />);

    expect(screen.getByText("no_frames.mp4")).toBeInTheDocument();
    // Should not have any key frame images
    const images = screen.queryAllByRole("img");
    expect(images.length).toBe(0);
  });

  it("should display video count badge", () => {
    render(<VideoGallery videos={mockVideos} />);

    const badge = screen.getByText("2");
    expect(badge).toBeInTheDocument();
  });
});

