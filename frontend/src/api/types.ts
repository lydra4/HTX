export type MediaType = "video" | "audio";

export interface Video {
  id: number;
  filename: string;
  storage_path: string;
  summary: string;
  detected_objects: string[];
  key_frames: string[];
  created_at: string;
}

export interface Transcription {
  id: number;
  filename: string;
  storage_path: string;
  transcript: string;
  confidence_score: number;
  video_id: number | null;
  created_at: string;
}

export interface SearchResponse {
  videos: Video[];
  transcriptions: Transcription[];
}

export interface UploadResult {
  video?: Video;
  transcription?: Transcription;
}

