'use client';

import Link from 'next/link';
import { Upload, Link as LinkIcon, Mic, Shield } from 'lucide-react';

export default function HomePage() {
  return (
    <div className="max-w-4xl mx-auto">
      {/* Hero Section */}
      <section aria-labelledby="hero-heading" className="text-center py-12">
        <h1 id="hero-heading" className="text-3xl font-bold mb-4">
          AI-Powered Audio Descriptions
        </h1>
        <p className="text-lg text-foreground/80 mb-8 max-w-2xl mx-auto">
          Experience visual media with accurate, timely audio descriptions.
          Tiresias uses AI to generate professional-quality descriptions that
          never interrupt dialogue.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            href="/upload"
            className="btn-primary text-lg px-8 py-4"
            aria-label="Upload a video for audio description"
          >
            <Upload className="w-5 h-5 mr-2" aria-hidden="true" />
            Get Started
          </Link>
        </div>
      </section>

      {/* Features Section */}
      <section aria-labelledby="features-heading" className="py-12">
        <h2 id="features-heading" className="text-2xl font-bold mb-8 text-center">
          How It Works
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="card" role="article">
            <div className="flex items-start gap-4">
              <Upload className="w-8 h-8 text-primary flex-shrink-0" aria-hidden="true" />
              <div>
                <h3 className="text-lg font-semibold mb-2">Upload or Link</h3>
                <p className="text-foreground/70">
                  Upload a video file or paste a URL from YouTube, Vimeo, or
                  Dailymotion. We support MP4, MOV, AVI, and WEBM formats.
                </p>
              </div>
            </div>
          </div>

          <div className="card" role="article">
            <div className="flex items-start gap-4">
              <LinkIcon className="w-8 h-8 text-primary flex-shrink-0" aria-hidden="true" />
              <div>
                <h3 className="text-lg font-semibold mb-2">AI Analysis</h3>
                <p className="text-foreground/70">
                  Our AI analyzes every scene, detects dialogue gaps, and
                  generates descriptions that fit perfectly without
                  interrupting speech.
                </p>
              </div>
            </div>
          </div>

          <div className="card" role="article">
            <div className="flex items-start gap-4">
              <Mic className="w-8 h-8 text-primary flex-shrink-0" aria-hidden="true" />
              <div>
                <h3 className="text-lg font-semibold mb-2">Natural Voices</h3>
                <p className="text-foreground/70">
                  Choose from 4+ natural-sounding voices with adjustable speed.
                  Descriptions are mixed seamlessly with the original audio.
                </p>
              </div>
            </div>
          </div>

          <div className="card" role="article">
            <div className="flex items-start gap-4">
              <Shield className="w-8 h-8 text-primary flex-shrink-0" aria-hidden="true" />
              <div>
                <h3 className="text-lg font-semibold mb-2">Zero Interruptions</h3>
                <p className="text-foreground/70">
                  Our absolute commitment: descriptions never overlap with
                  dialogue. Audio ducking ensures you hear everything clearly.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Supported Platforms */}
      <section aria-labelledby="platforms-heading" className="py-12">
        <h2 id="platforms-heading" className="text-2xl font-bold mb-6 text-center">
          Supported Platforms
        </h2>
        <div className="flex flex-wrap justify-center gap-6">
          {['YouTube', 'Vimeo', 'Dailymotion', 'File Upload'].map(
            (platform) => (
              <span
                key={platform}
                className="card px-6 py-3 text-center font-medium"
              >
                {platform}
              </span>
            )
          )}
        </div>
      </section>

      {/* Keyboard Shortcuts Info */}
      <section aria-labelledby="shortcuts-heading" className="py-8 text-center">
        <h2 id="shortcuts-heading" className="sr-only">
          Keyboard Navigation
        </h2>
        <p className="text-foreground/60">
          Full keyboard navigation available. Press{' '}
          <kbd className="px-2 py-1 bg-secondary rounded text-sm font-mono">
            Alt+H
          </kbd>{' '}
          for keyboard shortcuts.
        </p>
      </section>
    </div>
  );
}
