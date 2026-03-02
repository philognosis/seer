'use client';

import React, { createContext, useContext } from 'react';
import { type SoundEffect, playSound, setAudioEnabled } from '@/lib/audio';

interface AudioFeedbackContextType {
  play: (sound: SoundEffect, volume?: number) => Promise<void>;
  enable: () => void;
  disable: () => void;
}

const AudioFeedbackContext = createContext<AudioFeedbackContextType>({
  play: async () => {},
  enable: () => {},
  disable: () => {},
});

export function useAudioFeedbackContext() {
  return useContext(AudioFeedbackContext);
}

export function AudioFeedbackProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const value: AudioFeedbackContextType = {
    play: playSound,
    enable: () => setAudioEnabled(true),
    disable: () => setAudioEnabled(false),
  };

  return (
    <AudioFeedbackContext.Provider value={value}>
      {children}
    </AudioFeedbackContext.Provider>
  );
}
