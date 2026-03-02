'use client';

import { useCallback, useRef } from 'react';

export function useFocusManagement() {
  const previousFocusRef = useRef<HTMLElement | null>(null);

  const saveFocus = useCallback(() => {
    previousFocusRef.current = document.activeElement as HTMLElement;
  }, []);

  const restoreFocus = useCallback(() => {
    if (previousFocusRef.current) {
      previousFocusRef.current.focus();
      previousFocusRef.current = null;
    }
  }, []);

  const focusElement = useCallback((selector: string) => {
    const element = document.querySelector<HTMLElement>(selector);
    element?.focus();
  }, []);

  const focusFirst = useCallback((container: HTMLElement | null) => {
    if (!container) return;
    const focusable = container.querySelector<HTMLElement>(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    focusable?.focus();
  }, []);

  return {
    saveFocus,
    restoreFocus,
    focusElement,
    focusFirst,
  };
}
