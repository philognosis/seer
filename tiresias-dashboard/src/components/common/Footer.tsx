'use client';

import React from 'react';

export function Footer() {
  return (
    <footer
      id="footer"
      role="contentinfo"
      className="border-t border-border mt-auto"
    >
      <div className="container mx-auto px-4 py-6 text-center text-sm text-foreground/70">
        <p>
          &copy; 2026 Tiresias. Built for the blind community with love.
        </p>
        <p className="mt-2">
          <a
            href="/accessibility"
            className="underline hover:text-foreground focus:text-foreground"
          >
            Accessibility Statement
          </a>
          {' \u2022 '}
          <a
            href="/keyboard-shortcuts"
            className="underline hover:text-foreground focus:text-foreground"
          >
            Keyboard Shortcuts (Alt+H)
          </a>
        </p>
      </div>
    </footer>
  );
}
