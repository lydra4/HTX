import { useState } from "react";

import type { MediaType, UploadResult } from "../api/types";
import { uploadMedia } from "../api/client";

interface UploadPanelProps {
  onUploaded: (results: UploadResult[]) => void;
}

const MEDIA_OPTIONS: { label: string; value: MediaType }[] = [
  { label: "Video", value: "video" },
  { label: "Audio", value: "audio" },
];

export function UploadPanel({ onUploaded }: UploadPanelProps) {
  const [mediaType, setMediaType] = useState<MediaType>("video");
  const [files, setFiles] = useState<FileList | null>(null);
  const [busy, setBusy] = useState(false);
  const [status, setStatus] = useState<string | null>(null);

  async function handleUpload() {
    if (!files || busy) return;
    setBusy(true);
    setStatus("Processing...");

    try {
      const payload = Array.from(files);
      const results = await uploadMedia(payload, mediaType);
      onUploaded(results);
      setStatus(`Uploaded ${results.length} ${mediaType}(s) successfully.`);
      setFiles(null);
      (document.getElementById("media-files") as HTMLInputElement | null)?.value =
        "";
    } catch (error) {
      console.error(error);
      setStatus("Upload failed. Check console for details.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="card">
      <div className="section-title">
        Upload Media
        <span className="badge">Batch Supported</span>
      </div>
      <p>Select one or more files and choose whether they should be processed as video or audio.</p>

      <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
        <label style={{ fontWeight: 600 }}>
          Media Type
          <div className="pill-toggle" style={{ marginTop: "0.5rem" }}>
            {MEDIA_OPTIONS.map((option) => (
              <button
                key={option.value}
                type="button"
                className={mediaType === option.value ? "active" : ""}
                onClick={() => setMediaType(option.value)}
              >
                {option.label}
              </button>
            ))}
          </div>
        </label>

        <label style={{ fontWeight: 600 }}>
          Files
          <input
            id="media-files"
            type="file"
            multiple
            accept={mediaType === "video" ? "video/*" : "audio/*"}
            onChange={(event) => setFiles(event.target.files)}
            style={{ marginTop: "0.4rem" }}
          />
        </label>

        <button type="button" disabled={!files?.length || busy} onClick={handleUpload}>
          {busy ? "Processing…" : `Process ${mediaType === "video" ? "Videos" : "Audio"}`}
        </button>

        {status && (
          <span style={{ color: busy ? "#1c4ed8" : "#059669", fontWeight: 600 }}>
            {status}
          </span>
        )}
      </div>
    </div>
  );
}

