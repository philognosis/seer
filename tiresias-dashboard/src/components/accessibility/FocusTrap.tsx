'use client';

import React, { useEffect, useRef } from 'react';

interface FocusTrapProps {
  children: React.ReactNode;
  active?: boolean;
}

export function FocusTrap({ children, active = true }: FocusTrapProps) {
  const trapRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!active || !trapRef.current) return;

    const trap = trapRef.current;
    const focusableElements = trap.querySelectorAll<HTMLElement>(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );

    if (focusableElements.length === 0) return;

    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];

    function handleKeyDown(e: KeyboardEvent) {
      if (e.key !== 'Tab') return;

      if (e.shiftKey) {
        if (document.activeElement === firstElement) {
          e.preventDefault();
          lastElement.focus();
        }
      } else {
        if (document.activeElement === lastElement) {
          e.preventDefault();
          firstElement.focus();
        }
      }
    }

    trap.addEventListener('keydown', handleKeyDown);
    firstElement.focus();

    return () => trap.removeEventListener('keydown', handleKeyDown);
  }, [active]);

  return <div ref={trapRef}>{children}</div>;
}
