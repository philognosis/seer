'use client';

import { useCallback } from 'react';
import { useLiveRegion } from '@/components/accessibility/LiveRegion';
import { type SoundEffect, playSound } from '@/lib/audio';

export function useAudioFeedback() {
  const { announce } = useLiveRegion();

  const speak = useCallback(
    (message: string, priority: 'polite' | 'assertive' = 'polite') => {
      announce(message, priority);
    },
    [announce]
  );

  const announceAction = useCallback(
    async (action: string, sound?: SoundEffect) => {
      if (sound) {
        await playSound(sound);
      }
      speak(action);
    },
    [speak]
  );

  return {
    playSound,
    speak,
    announceAction,
  };
}
