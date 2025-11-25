import type { Transcription } from "../api/types";

interface TranscriptionListProps {
  transcriptions: Transcription[];
  onSelectReference?: (transcription: Transcription) => void;
}

function formatConfidence(score: number) {
  return `${(score * 100).toFixed(1)}%`;
}

function synthesizeTimeline(transcript: string) {
  const tokens = transcript.split(" ");
  const segments: { text: string; timestamp: string }[] = [];

  for (let i = 0; i < tokens.length; i += 6) {
    const chunk = tokens.slice(i, i + 6).join(" ");
    const timestamp = `${String(Math.floor(i / 6))
      .padStart(2, "0")}:00`;
    segments.push({ text: chunk, timestamp });
  }

  return segments.length ? segments : [{ text: transcript, timestamp: "00:00" }];
}

export function TranscriptionList({
  transcriptions,
  onSelectReference,
}: TranscriptionListProps) {
  if (!transcriptions.length) {
    return (
      <div className="card">
        <div className="section-title">Processed Audio</div>
        <p>No transcriptions available yet.</p>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="section-title">
        Processed Audio
        <span className="badge">{transcriptions.length}</span>
      </div>
      <div className="grid">
        {transcriptions.map((item) => (
          <div key={item.id} className="transcription-item">
            <header style={{ display: "flex", justifyContent: "space-between" }}>
              <div>
                <strong>{item.filename}</strong>
                <p style={{ margin: "0.25rem 0", color: "#475467", fontSize: "0.9rem" }}>
                  {new Date(item.created_at).toLocaleString()}
                </p>
              </div>
              {onSelectReference && (
                <button
                  type="button"
                  style={{ padding: "0.3rem 0.8rem", fontSize: "0.85rem" }}
                  onClick={() => onSelectReference(item)}
                >
                  Use as Audio Anchor
                </button>
              )}
            </header>

            <small style={{ color: "#64748b" }}>
              Confidence: {formatConfidence(item.confidence_score)}
            </small>

            <div style={{ marginTop: "0.5rem", display: "flex", flexDirection: "column", gap: "0.25rem" }}>
              {synthesizeTimeline(item.transcript).map((segment) => (
                <div
                  key={`${item.id}-${segment.timestamp}`}
                  style={{ display: "flex", gap: "0.75rem", fontSize: "0.95rem" }}
                >
                  <span style={{ fontWeight: 600, color: "#1c4ed8", minWidth: "46px" }}>
                    {segment.timestamp}
                  </span>
                  <span>{segment.text}</span>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

