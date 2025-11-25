import axios from "axios";

import type {
  MediaType,
  SearchResponse,
  Transcription,
  UploadResult,
  Video,
} from "./types";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, "") ??
  "http://127.0.0.1:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 20000,
});

export async function fetchVideos(): Promise<Video[]> {
  const { data } = await api.get<Video[]>("/videos");
  return data;
}

export async function fetchTranscriptions(): Promise<Transcription[]> {
  const { data } = await api.get<Transcription[]>("/transcriptions");
  return data;
}

export async function searchContent(term: string): Promise<SearchResponse> {
  const { data } = await api.get<SearchResponse>("/search", {
    params: { term },
  });
  return data;
}

export async function uploadMedia(
  files: File[],
  mediaType: MediaType,
): Promise<UploadResult[]> {
  const results: UploadResult[] = [];

  for (const file of files) {
    const formData = new FormData();
    formData.append("file", file, file.name);

    if (mediaType === "video") {
      const { data } = await api.post<Video>("/process/video", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      results.push({ video: data });
    } else {
      const { data } = await api.post<Transcription>(
        "/process/audio",
        formData,
        {
          headers: { "Content-Type": "multipart/form-data" },
        },
      );
      results.push({ transcription: data });
    }
  }

  return results;
}

export function resolveKeyFrameUrl(rawPath: string): string {
  if (!rawPath) {
    return "";
  }

  if (rawPath.startsWith("http://") || rawPath.startsWith("https://")) {
    return rawPath;
  }

  const normalized = rawPath.replaceAll("\\", "/");

  if (normalized.startsWith("/media/")) {
    return `${API_BASE_URL}${normalized}`;
  }

  const mediaIndex = normalized.lastIndexOf("/media/");
  if (mediaIndex !== -1) {
    return `${API_BASE_URL}${normalized.slice(mediaIndex)}`;
  }

  return `${API_BASE_URL}/media/${normalized.replace(/^\.?\//, "")}`;
}

export { API_BASE_URL };

