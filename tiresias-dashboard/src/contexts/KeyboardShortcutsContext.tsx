'use client';

import React, { createContext, useContext } from 'react';
import { useGlobalShortcuts } from '@/hooks/useKeyboardShortcuts';

const KeyboardShortcutsContext = createContext<null>(null);

export function KeyboardShortcutsProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  useGlobalShortcuts();

  return (
    <KeyboardShortcutsContext.Provider value={null}>
      {children}
    </KeyboardShortcutsContext.Provider>
  );
}
