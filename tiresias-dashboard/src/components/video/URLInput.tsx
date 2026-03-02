'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Link } from 'lucide-react';
import { useLiveRegion } from '@/components/accessibility/LiveRegion';
import { api } from '@/lib/api';

export function URLInput() {
  const router = useRouter();
  const { announce } = useLiveRegion();
  const [url, setUrl] = useState('');
  const [voice, setVoice] = useState('female_us');
  const [llmProvider, setLlmProvider] = useState('gemini');
  const [density, setDensity] = useState('standard');
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim()) return;

    setIsProcessing(true);
    setError(null);
    announce('Processing video URL. Please wait.');

    try {
      const response = await api.processFromURL({
        url: url.trim(),
        options: {
          voice,
          llm_provider: llmProvider,
          description_density: density,
        },
      });
      announce('Video URL accepted. Redirecting to processing page.');
      router.push(`/process/${response.video_id}`);
    } catch (err) {
      const msg =
        'Failed to process URL. Please check the URL and try again.';
      setError(msg);
      announce(msg, 'assertive');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* URL input */}
      <div>
        <label htmlFor="video-url" className="block font-medium mb-2">
          Video URL
        </label>
        <div className="relative">
          <Link
            className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-foreground/50"
            aria-hidden="true"
          />
          <input
            id="video-url"
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://www.youtube.com/watch?v=..."
            className="input-field pl-10"
            aria-describedby="url-help"
            required
          />
        </div>
        <p id="url-help" className="text-sm text-foreground/60 mt-1">
          Supported: YouTube, Vimeo, Dailymotion
        </p>
      </div>

      {/* Error display */}
      {error && (
        <div
          role="alert"
          className="bg-destructive/10 border border-destructive text-destructive px-4 py-3 rounded-lg"
        >
          {error}
        </div>
      )}

      {/* Options */}
      <fieldset className="card space-y-4">
        <legend className="text-lg font-semibold mb-2">Options</legend>

        <div>
          <label htmlFor="url-voice-select" className="block font-medium mb-1">
            Narration Voice
          </label>
          <select
            id="url-voice-select"
            value={voice}
            onChange={(e) => setVoice(e.target.value)}
            className="input-field"
          >
            <option value="female_us">Sarah (Female, US English)</option>
            <option value="male_us">James (Male, US English)</option>
            <option value="female_uk">Emma (Female, UK English)</option>
            <option value="male_uk">William (Male, UK English)</option>
          </select>
        </div>

        <div>
          <label htmlFor="url-llm-select" className="block font-medium mb-1">
            AI Model
          </label>
          <select
            id="url-llm-select"
            value={llmProvider}
            onChange={(e) => setLlmProvider(e.target.value)}
            className="input-field"
          >
            <option value="gemini">Gemini 2.0 Flash (Default)</option>
            <option value="claude">Claude 3.5 Sonnet</option>
            <option value="openai">GPT-4 Vision</option>
          </select>
        </div>

        <div>
          <label
            htmlFor="url-density-select"
            className="block font-medium mb-1"
          >
            Description Density
          </label>
          <select
            id="url-density-select"
            value={density}
            onChange={(e) => setDensity(e.target.value)}
            className="input-field"
          >
            <option value="minimal">Minimal - Key moments only</option>
            <option value="standard">Standard - Balanced coverage</option>
            <option value="detailed">Detailed - Maximum description</option>
          </select>
        </div>
      </fieldset>

      {/* Submit */}
      <button
        type="submit"
        disabled={!url.trim() || isProcessing}
        className="btn-primary w-full text-lg"
        aria-busy={isProcessing}
      >
        {isProcessing ? 'Processing...' : 'Generate Audio Descriptions'}
      </button>
    </form>
  );
}
