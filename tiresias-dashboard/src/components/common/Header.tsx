'use client';

import React from 'react';
import Link from 'next/link';

export function Header() {
  return (
    <header role="banner" className="border-b border-border">
      <nav
        id="navigation"
        role="navigation"
        aria-label="Main navigation"
        className="container mx-auto px-4 py-4 flex items-center justify-between"
      >
        <div>
          <Link
            href="/"
            className="text-2xl font-bold hover:text-primary focus-visible:text-primary transition-colors"
            aria-label="Tiresias - Home"
          >
            Tiresias
          </Link>
          <p className="text-sm text-foreground/70">
            AI Audio Description System
          </p>
        </div>

        <div className="flex items-center gap-4">
          <Link
            href="/upload"
            className="btn-primary text-sm px-4 py-2"
          >
            New Video
          </Link>
        </div>
      </nav>
    </header>
  );
}
