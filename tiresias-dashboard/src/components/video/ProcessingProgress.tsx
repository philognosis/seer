'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { CheckCircle, Loader2, AlertCircle } from 'lucide-react';
import { useLiveRegion } from '@/components/accessibility/LiveRegion';
import { api } from '@/lib/api';

interface ProcessingProgressProps {
  videoId: string;
}

const PROCESSING_STEPS = [
  'Downloading video',
  'Extracting audio',
  'Detecting scenes',
  'Extracting key frames',
  'Transcribing dialogue',
  'Finding description gaps',
  'Analyzing visual content',
  'Generating descriptions',
  'Synthesizing speech',
  'Mixing audio',
  'Creating description track',
  'Complete',
];

export function ProcessingProgress({ videoId }: ProcessingProgressProps) {
  const router = useRouter();
  const { announce } = useLiveRegion();
  const [status, setStatus] = useState('queued');
  const [progress, setProgress] = useState(0);
  const [currentStep, setCurrentStep] = useState('Queued');
  const [error, setError] = useState<string | null>(null);
  const [lastAnnounced, setLastAnnounced] = useState(0);

  useEffect(() => {
    let interval: NodeJS.Timeout;

    const pollStatus = async () => {
      try {
        const data = await api.getVideoStatus(videoId);
        setStatus(data.status);
        setProgress(data.progress);
        setCurrentStep(data.current_step || 'Processing');

        // Announce progress at 25% intervals
        const progressThreshold = Math.floor(data.progress / 25) * 25;
        if (progressThreshold > lastAnnounced && data.progress > 0) {
          announce(
            `Processing ${data.progress}% complete. ${data.current_step || ''}`
          );
          setLastAnnounced(progressThreshold);
        }

        if (data.status === 'completed') {
          announce('Processing complete! Your video is ready.', 'assertive');
          clearInterval(interval);
          // Redirect to player after a brief pause
          setTimeout(() => router.push(`/player/${videoId}`), 2000);
        }

        if (data.status === 'failed') {
          setError(data.error || 'Processing failed');
          announce('Processing failed. Please try again.', 'assertive');
          clearInterval(interval);
        }
      } catch {
        // Silently retry on poll failure
      }
    };

    // Poll every 3 seconds
    pollStatus();
    interval = setInterval(pollStatus, 3000);

    return () => clearInterval(interval);
  }, [videoId, announce, lastAnnounced, router]);

  return (
    <div className="space-y-8">
      {/* Progress bar */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold">{currentStep}</h2>
          <span
            className="text-2xl font-bold text-primary"
            aria-label={`${progress}% complete`}
          >
            {progress}%
          </span>
        </div>

        <div
          role="progressbar"
          aria-valuenow={progress}
          aria-valuemin={0}
          aria-valuemax={100}
          aria-label={`Processing progress: ${progress}%`}
          className="w-full bg-secondary rounded-full h-4 overflow-hidden"
        >
          <div
            className="bg-primary h-full rounded-full transition-all duration-500 ease-out"
            style={{ width: `${progress}%` }}
          />
        </div>

        {status === 'completed' && (
          <p className="mt-4 text-accent font-medium flex items-center gap-2">
            <CheckCircle className="w-5 h-5" aria-hidden="true" />
            Processing complete! Redirecting to player...
          </p>
        )}
      </div>

      {/* Error display */}
      {error && (
        <div
          role="alert"
          className="bg-destructive/10 border border-destructive text-destructive px-6 py-4 rounded-lg flex items-start gap-3"
        >
          <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" aria-hidden="true" />
          <div>
            <p className="font-semibold">Processing Failed</p>
            <p className="text-sm mt-1">{error}</p>
            <button
              onClick={() => window.location.reload()}
              className="btn-secondary mt-3 text-sm"
            >
              Try Again
            </button>
          </div>
        </div>
      )}

      {/* Processing steps */}
      <div className="card">
        <h3 className="text-lg font-semibold mb-4">Processing Steps</h3>
        <ol className="space-y-3" aria-label="Processing steps">
          {PROCESSING_STEPS.map((step, index) => {
            const stepProgress = (index / (PROCESSING_STEPS.length - 1)) * 100;
            const isComplete = progress > stepProgress;
            const isCurrent =
              progress >= stepProgress &&
              progress < ((index + 1) / (PROCESSING_STEPS.length - 1)) * 100;

            return (
              <li
                key={step}
                className={`flex items-center gap-3 ${
                  isComplete
                    ? 'text-accent'
                    : isCurrent
                      ? 'text-primary font-medium'
                      : 'text-foreground/40'
                }`}
              >
                {isComplete ? (
                  <CheckCircle
                    className="w-5 h-5 flex-shrink-0"
                    aria-hidden="true"
                  />
                ) : isCurrent ? (
                  <Loader2
                    className="w-5 h-5 flex-shrink-0 animate-spin"
                    aria-hidden="true"
                  />
                ) : (
                  <div
                    className="w-5 h-5 rounded-full border-2 border-current flex-shrink-0"
                    aria-hidden="true"
                  />
                )}
                <span>
                  {step}
                  {isCurrent && (
                    <span className="sr-only"> (in progress)</span>
                  )}
                  {isComplete && <span className="sr-only"> (complete)</span>}
                </span>
              </li>
            );
          })}
        </ol>
      </div>
    </div>
  );
}
