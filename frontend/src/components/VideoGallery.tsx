import type { Video } from "../api/types";
import { resolveKeyFrameUrl } from "../api/client";

interface VideoGalleryProps {
  videos: Video[];
  onSelectReference?: (video: Video) => void;
}

export function VideoGallery({ videos, onSelectReference }: VideoGalleryProps) {
  if (!videos.length) {
    return (
      <div className="card">
        <div className="section-title">Processed Videos</div>
        <p>No videos processed yet. Upload a few to get started.</p>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="section-title">
        Processed Videos
        <span className="badge">{videos.length}</span>
      </div>
      <div className="grid video-grid">
        {videos.map((video) => (
          <article key={video.id} className="video-card">
            <header
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "flex-start",
                gap: "0.5rem",
              }}
            >
              <div>
                <strong>{video.filename}</strong>
                <p style={{ margin: "0.25rem 0", color: "#475467", fontSize: "0.9rem" }}>
                  {new Date(video.created_at).toLocaleString()}
                </p>
              </div>
              {onSelectReference && (
                <button
                  type="button"
                  style={{ padding: "0.3rem 0.8rem", fontSize: "0.85rem" }}
                  onClick={() => onSelectReference(video)}
                >
                  Use as Visual Anchor
                </button>
              )}
            </header>

            <p style={{ marginTop: "0.5rem" }}>{video.summary}</p>

            <div className="objects">
              {video.detected_objects.map((object) => (
                <span key={`${video.id}-${object}`}>{object}</span>
              ))}
            </div>

            <div className="keyframes" style={{ marginTop: "0.75rem" }}>
              {video.key_frames.map((frame) => {
                const src = resolveKeyFrameUrl(frame);
                return src ? (
                  <img key={frame} src={src} alt={`Key frame ${frame}`} />
                ) : (
                  <div
                    key={frame}
                    style={{
                      border: "1px dashed #cbd5f5",
                      borderRadius: "8px",
                      padding: "1.5rem",
                      textAlign: "center",
                      fontSize: "0.85rem",
                    }}
                  >
                    Frame unavailable
                  </div>
                );
              })}
            </div>
          </article>
        ))}
      </div>
    </div>
  );
}

