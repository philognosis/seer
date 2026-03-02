'use client';

import { useCallback, useEffect, useState } from 'react';

interface UserPreferences {
  primaryVoice: string;
  voiceSpeed: number;
  descriptionDensity: string;
  duckingLevel: number;
  keyboardShortcutsEnabled: boolean;
  audioFeedbackEnabled: boolean;
  highContrastMode: boolean;
}

const DEFAULT_PREFERENCES: UserPreferences = {
  primaryVoice: 'female_us',
  voiceSpeed: 1.0,
  descriptionDensity: 'standard',
  duckingLevel: -8.0,
  keyboardShortcutsEnabled: true,
  audioFeedbackEnabled: true,
  highContrastMode: true,
};

const STORAGE_KEY = 'tiresias_preferences';

export function useUserPreferences() {
  const [preferences, setPreferences] =
    useState<UserPreferences>(DEFAULT_PREFERENCES);

  useEffect(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        setPreferences({ ...DEFAULT_PREFERENCES, ...JSON.parse(saved) });
      }
    } catch {
      // Use defaults if localStorage unavailable
    }
  }, []);

  const updatePreferences = useCallback(
    (updates: Partial<UserPreferences>) => {
      setPreferences((prev) => {
        const next = { ...prev, ...updates };
        try {
          localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
        } catch {
          // Ignore storage errors
        }
        return next;
      });
    },
    []
  );

  const resetPreferences = useCallback(() => {
    setPreferences(DEFAULT_PREFERENCES);
    try {
      localStorage.removeItem(STORAGE_KEY);
    } catch {
      // Ignore
    }
  }, []);

  return {
    preferences,
    updatePreferences,
    resetPreferences,
  };
}
