'use client';

import { useCallback, useEffect } from 'react';

export function useKeyboardShortcuts(
  shortcuts: Record<string, () => void>
) {
  const handleKeyPress = useCallback(
    (event: KeyboardEvent) => {
      let combo = '';
      if (event.ctrlKey) combo += 'Ctrl+';
      if (event.altKey) combo += 'Alt+';
      if (event.shiftKey) combo += 'Shift+';
      combo += event.key;

      if (shortcuts[combo]) {
        event.preventDefault();
        shortcuts[combo]();
      }
    },
    [shortcuts]
  );

  useEffect(() => {
    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [handleKeyPress]);
}

export function useGlobalShortcuts() {
  const shortcuts: Record<string, () => void> = {
    'Alt+h': () => {
      const helpButton = document.querySelector(
        '[data-help-button]'
      ) as HTMLElement;
      helpButton?.click();
    },
    'Alt+m': () => {
      const mainContent = document.getElementById('main-content');
      mainContent?.focus();
    },
  };

  useKeyboardShortcuts(shortcuts);
}
