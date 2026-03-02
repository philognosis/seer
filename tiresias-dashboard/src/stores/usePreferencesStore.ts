import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface PreferencesState {
  voice: string;
  llmProvider: string;
  descriptionDensity: string;
  voiceSpeed: number;
  duckingLevel: number;
  audioFeedbackEnabled: boolean;
  highContrastMode: boolean;
  setVoice: (voice: string) => void;
  setLlmProvider: (provider: string) => void;
  setDensity: (density: string) => void;
  setVoiceSpeed: (speed: number) => void;
  setDuckingLevel: (level: number) => void;
  setAudioFeedback: (enabled: boolean) => void;
  setHighContrast: (enabled: boolean) => void;
  resetAll: () => void;
}

const DEFAULT_STATE = {
  voice: 'female_us',
  llmProvider: 'gemini',
  descriptionDensity: 'standard',
  voiceSpeed: 1.0,
  duckingLevel: -8.0,
  audioFeedbackEnabled: true,
  highContrastMode: true,
};

export const usePreferencesStore = create<PreferencesState>()(
  persist(
    (set) => ({
      ...DEFAULT_STATE,
      setVoice: (voice) => set({ voice }),
      setLlmProvider: (llmProvider) => set({ llmProvider }),
      setDensity: (descriptionDensity) => set({ descriptionDensity }),
      setVoiceSpeed: (voiceSpeed) => set({ voiceSpeed }),
      setDuckingLevel: (duckingLevel) => set({ duckingLevel }),
      setAudioFeedback: (audioFeedbackEnabled) =>
        set({ audioFeedbackEnabled }),
      setHighContrast: (highContrastMode) => set({ highContrastMode }),
      resetAll: () => set(DEFAULT_STATE),
    }),
    {
      name: 'tiresias-preferences',
    }
  )
);
