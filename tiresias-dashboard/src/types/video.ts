/**
 * Video type definitions
 */

export interface Video {
  id: string;
  title: string | null;
  duration: number | null;
  resolution: string | null;
  fps: number | null;
  source_type: string;
  source_url: string | null;
  status: VideoStatus;
  progress: number;
  descriptions_count: number;
  dialogue_interruptions: number;
  community_rating: number | null;
  professionally_approved: boolean;
  created_at: string;
  processed_at: string | null;
}

export type VideoStatus =
  | 'queued'
  | 'downloading'
  | 'analyzing'
  | 'transcribing'
  | 'generating'
  | 'mixing'
  | 'completed'
  | 'failed';

export interface Description {
  id: string;
  timestamp: number;
  duration: number;
  text: string;
  priority: number | null;
  scene_type: string | null;
  ai_confidence: number | null;
}

export interface CommunityDescription {
  id: string;
  video_id: string;
  contributor_id: string | null;
  timestamp: number;
  text: string;
  upvotes: number;
  downvotes: number;
  reviewed_by_professional: boolean;
  is_approved: boolean;
  created_at: string;
}
