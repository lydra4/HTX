import { useState } from "react";

import type { SearchResponse, Transcription, Video } from "../api/types";

interface SearchPanelProps {
  onTextSearch: (term: string) => Promise<SearchResponse>;
  onVisualSearch: (video: Video) => Promise<SearchResponse>;
  onAudioSearch: (transcription: Transcription) => Promise<SearchResponse>;
  videos: Video[];
  transcriptions: Transcription[];
  results: SearchResponse | null;
  isSearching: boolean;
  activeTerm: string;
}

export function SearchPanel({
  onTextSearch,
  onVisualSearch,
  onAudioSearch,
  videos,
  transcriptions,
  results,
  isSearching,
  activeTerm,
}: SearchPanelProps) {
  const [term, setTerm] = useState("");

  return (
    <div className="card">
      <div className="section-title">
        Unified Search
        <span className="badge">Text · Visual · Audio</span>
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
        <label style={{ fontWeight: 600 }}>
          Text Query
          <div style={{ display: "flex", gap: "0.5rem", marginTop: "0.35rem" }}>
            <input
              type="text"
              placeholder="Search objects, transcripts, filenames..."
              value={term}
              onChange={(event) => setTerm(event.target.value)}
            />
            <button
              type="button"
              onClick={() => onTextSearch(term)}
              disabled={!term.trim() || isSearching}
            >
              Search
            </button>
          </div>
        </label>

        <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap" }}>
          <div style={{ flex: 1, minWidth: "240px" }}>
            <strong style={{ display: "block", marginBottom: "0.35rem" }}>
              Visual Similarity
            </strong>
            <select
              onChange={(event) => {
                const selected = videos.find(
                  (video) => String(video.id) === event.target.value,
                );
                if (selected) onVisualSearch(selected);
              }}
              defaultValue=""
            >
              <option value="" disabled>
                Choose reference video
              </option>
              {videos.map((video) => (
                <option key={video.id} value={video.id}>
                  {video.filename}
                </option>
              ))}
            </select>
          </div>

          <div style={{ flex: 1, minWidth: "240px" }}>
            <strong style={{ display: "block", marginBottom: "0.35rem" }}>
              Audio Similarity
            </strong>
            <select
              onChange={(event) => {
                const selected = transcriptions.find(
                  (item) => String(item.id) === event.target.value,
                );
                if (selected) onAudioSearch(selected);
              }}
              defaultValue=""
            >
              <option value="" disabled>
                Choose reference transcription
              </option>
              {transcriptions.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.filename}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="search-results">
          <strong>Latest Results</strong>
          <small>
            {isSearching
              ? "Searching…"
              : results
                ? `Matched ${results.videos.length} videos and ${results.transcriptions.length} transcriptions for "${activeTerm}".`
                : "Run a search to see matches."}
          </small>

          {results && (
            <>
              <div>
                <strong>Videos</strong>
                <div style={{ display: "flex", flexDirection: "column", gap: "0.35rem" }}>
                  {results.videos.map((video) => (
                    <div key={`search-video-${video.id}`}>
                      <span style={{ fontWeight: 600 }}>{video.filename}</span>
                      <small style={{ display: "block" }}>{video.summary}</small>
                    </div>
                  ))}
                  {!results.videos.length && <small>No video matches.</small>}
                </div>
              </div>
              <div>
                <strong>Transcriptions</strong>
                <div style={{ display: "flex", flexDirection: "column", gap: "0.35rem" }}>
                  {results.transcriptions.map((item) => (
                    <div key={`search-trans-${item.id}`}>
                      <span style={{ fontWeight: 600 }}>{item.filename}</span>
                      <small style={{ display: "block" }}>
                        {item.transcript.slice(0, 140)}
                        {item.transcript.length > 140 ? "…" : ""}
                      </small>
                    </div>
                  ))}
                  {!results.transcriptions.length && <small>No transcription matches.</small>}
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

