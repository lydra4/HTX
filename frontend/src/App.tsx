import { useEffect, useState } from "react";

import {
  API_BASE_URL,
  fetchTranscriptions,
  fetchVideos,
  searchContent,
} from "./api/client";
import type { SearchResponse, Transcription, UploadResult, Video } from "./api/types";
import { UploadPanel } from "./components/UploadPanel";
import { VideoGallery } from "./components/VideoGallery";
import { TranscriptionList } from "./components/TranscriptionList";
import { SearchPanel } from "./components/SearchPanel";

function App() {
  const [videos, setVideos] = useState<Video[]>([]);
  const [transcriptions, setTranscriptions] = useState<Transcription[]>([]);
  const [searchResults, setSearchResults] = useState<SearchResponse | null>(null);
  const [isSearching, setIsSearching] = useState(false);
  const [activeTerm, setActiveTerm] = useState("");

  useEffect(() => {
    refreshMedia();
  }, []);

  async function refreshMedia() {
    const [videoData, transcriptionData] = await Promise.all([
      fetchVideos(),
      fetchTranscriptions(),
    ]);
    setVideos(videoData);
    setTranscriptions(transcriptionData);
  }

  async function handleUpload(results: UploadResult[]) {
    const newVideos = results
      .map((result) => result.video)
      .filter((video): video is Video => Boolean(video));
    const newTranscriptions = results
      .map((result) => result.transcription)
      .filter((item): item is Transcription => Boolean(item));

    if (newVideos.length) setVideos((prev) => [...newVideos, ...prev]);
    if (newTranscriptions.length) setTranscriptions((prev) => [...newTranscriptions, ...prev]);
  }

  async function runSearch(term: string, strategy: "text" | "visual" | "audio") {
    if (!term.trim()) return;
    setIsSearching(true);
    setActiveTerm(`${strategy}: ${term}`);
    try {
      const response = await searchContent(term);
      setSearchResults(response);
    } finally {
      setIsSearching(false);
    }
  }

  return (
    <div className="app-shell">
      <header>
        <h1 style={{ marginBottom: "0.25rem" }}>HTX Media Intelligence Console</h1>
        <p style={{ margin: 0, color: "#475467" }}>
          Backend URL: <strong>{API_BASE_URL}</strong>
        </p>
      </header>

      <UploadPanel onUploaded={handleUpload} />

      <SearchPanel
        onTextSearch={(term) => runSearch(term, "text")}
        onVisualSearch={(video) => runSearch(video.summary || video.filename, "visual")}
        onAudioSearch={(transcription) =>
          runSearch(transcription.transcript.slice(0, 140), "audio")
        }
        videos={videos}
        transcriptions={transcriptions}
        results={searchResults}
        isSearching={isSearching}
        activeTerm={activeTerm}
      />

      <VideoGallery videos={videos} onSelectReference={(video) => runSearch(video.summary, "visual")} />
      <TranscriptionList
        transcriptions={transcriptions}
        onSelectReference={(transcription) => runSearch(transcription.transcript, "audio")}
      />
    </div>
  );
}

export default App;

