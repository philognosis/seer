import { create } from 'zustand';

interface VideoState {
  currentVideoId: string | null;
  processingVideos: Map<string, { progress: number; status: string }>;
  setCurrentVideo: (id: string | null) => void;
  updateProcessing: (
    id: string,
    data: { progress: number; status: string }
  ) => void;
  removeProcessing: (id: string) => void;
}

export const useVideoStore = create<VideoState>((set) => ({
  currentVideoId: null,
  processingVideos: new Map(),
  setCurrentVideo: (id) => set({ currentVideoId: id }),
  updateProcessing: (id, data) =>
    set((state) => {
      const updated = new Map(state.processingVideos);
      updated.set(id, data);
      return { processingVideos: updated };
    }),
  removeProcessing: (id) =>
    set((state) => {
      const updated = new Map(state.processingVideos);
      updated.delete(id);
      return { processingVideos: updated };
    }),
}));
