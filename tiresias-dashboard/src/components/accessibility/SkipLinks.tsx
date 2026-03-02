'use client';

import React from 'react';

const links = [
  { href: '#main-content', label: 'Skip to main content' },
  { href: '#navigation', label: 'Skip to navigation' },
  { href: '#footer', label: 'Skip to footer' },
];

export function SkipLinks() {
  return (
    <div className="skip-links">
      {links.map((link) => (
        <a
          key={link.href}
          href={link.href}
          className="skip-link"
        >
          {link.label}
        </a>
      ))}
    </div>
  );
}
