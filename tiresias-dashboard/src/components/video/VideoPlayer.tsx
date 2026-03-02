'use client';

import React, { useCallback, useEffect, useRef, useState } from 'react';
import {
  Play,
  Pause,
  Volume2,
  VolumeX,
  SkipBack,
  SkipForward,
  Download,
} from 'lucide-react';
import { useLiveRegion } from '@/components/accessibility/LiveRegion';

interface VideoPlayerProps {
  videoId: string;
}

export function VideoPlayer({ videoId }: VideoPlayerProps) {
  const { announce } = useLiveRegion();
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);

  const videoSrc = `/api/v1/videos/${videoId}/download?track=combined`;

  const togglePlay = useCallback(() => {
    const video = videoRef.current;
    if (!video) return;

    if (video.paused) {
      video.play();
      setIsPlaying(true);
      announce('Playing');
    } else {
      video.pause();
      setIsPlaying(false);
      announce('Paused');
    }
  }, [announce]);

  const toggleMute = useCallback(() => {
    const video = videoRef.current;
    if (!video) return;

    video.muted = !video.muted;
    setIsMuted(video.muted);
    announce(video.muted ? 'Muted' : 'Unmuted');
  }, [announce]);

  const seek = useCallback(
    (seconds: number) => {
      const video = videoRef.current;
      if (!video) return;

      video.currentTime = Math.max(
        0,
        Math.min(video.duration, video.currentTime + seconds)
      );
      announce(`Seeked to ${formatTime(video.currentTime)}`);
    },
    [announce]
  );

  const changeVolume = useCallback(
    (delta: number) => {
      const video = videoRef.current;
      if (!video) return;

      const newVolume = Math.max(0, Math.min(1, video.volume + delta));
      video.volume = newVolume;
      setVolume(newVolume);
      announce(`Volume ${Math.round(newVolume * 100)}%`);
    },
    [announce]
  );

  // Keyboard controls
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      const target = e.target as HTMLElement;
      if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA') return;

      switch (e.key) {
        case ' ':
          e.preventDefault();
          togglePlay();
          break;
        case 'ArrowRight':
          e.preventDefault();
          seek(e.shiftKey ? 30 : 5);
          break;
        case 'ArrowLeft':
          e.preventDefault();
          seek(e.shiftKey ? -30 : -5);
          break;
        case 'ArrowUp':
          e.preventDefault();
          changeVolume(0.1);
          break;
        case 'ArrowDown':
          e.preventDefault();
          changeVolume(-0.1);
          break;
        case 'm':
        case 'M':
          toggleMute();
          break;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [togglePlay, seek, changeVolume, toggleMute]);

  return (
    <div className="space-y-4">
      {/* Video element */}
      <div className="relative bg-black rounded-xl overflow-hidden">
        <video
          ref={videoRef}
          src={videoSrc}
          className="w-full aspect-video"
          onTimeUpdate={() =>
            setCurrentTime(videoRef.current?.currentTime || 0)
          }
          onLoadedMetadata={() =>
            setDuration(videoRef.current?.duration || 0)
          }
          onEnded={() => {
            setIsPlaying(false);
            announce('Video ended');
          }}
          aria-label="Video player with audio descriptions"
        >
          Your browser does not support the video element.
        </video>
      </div>

      {/* Controls */}
      <div
        className="card flex flex-wrap items-center gap-4"
        role="group"
        aria-label="Video controls"
      >
        {/* Skip back */}
        <button
          onClick={() => seek(-5)}
          className="btn-secondary p-3"
          aria-label="Skip back 5 seconds"
          title="Skip back 5 seconds"
        >
          <SkipBack className="w-5 h-5" aria-hidden="true" />
        </button>

        {/* Play/Pause */}
        <button
          onClick={togglePlay}
          className="btn-primary p-3"
          aria-label={isPlaying ? 'Pause' : 'Play'}
          title={isPlaying ? 'Pause (Space)' : 'Play (Space)'}
        >
          {isPlaying ? (
            <Pause className="w-6 h-6" aria-hidden="true" />
          ) : (
            <Play className="w-6 h-6" aria-hidden="true" />
          )}
        </button>

        {/* Skip forward */}
        <button
          onClick={() => seek(5)}
          className="btn-secondary p-3"
          aria-label="Skip forward 5 seconds"
          title="Skip forward 5 seconds"
        >
          <SkipForward className="w-5 h-5" aria-hidden="true" />
        </button>

        {/* Time display */}
        <span className="text-sm font-mono" aria-live="off">
          {formatTime(currentTime)} / {formatTime(duration)}
        </span>

        {/* Spacer */}
        <div className="flex-1" />

        {/* Volume */}
        <button
          onClick={toggleMute}
          className="btn-secondary p-3"
          aria-label={isMuted ? 'Unmute (M)' : 'Mute (M)'}
          title={isMuted ? 'Unmute (M)' : 'Mute (M)'}
        >
          {isMuted ? (
            <VolumeX className="w-5 h-5" aria-hidden="true" />
          ) : (
            <Volume2 className="w-5 h-5" aria-hidden="true" />
          )}
        </button>

        <input
          type="range"
          min="0"
          max="1"
          step="0.05"
          value={volume}
          onChange={(e) => {
            const newVolume = parseFloat(e.target.value);
            if (videoRef.current) videoRef.current.volume = newVolume;
            setVolume(newVolume);
          }}
          className="w-24"
          aria-label={`Volume: ${Math.round(volume * 100)}%`}
        />
      </div>

      {/* Keyboard shortcuts help */}
      <details className="card text-sm">
        <summary className="cursor-pointer font-medium">
          Keyboard Shortcuts
        </summary>
        <dl className="mt-3 space-y-2">
          <div className="flex gap-4">
            <dt className="font-mono bg-secondary px-2 py-1 rounded min-w-[80px] text-center">
              Space
            </dt>
            <dd>Play / Pause</dd>
          </div>
          <div className="flex gap-4">
            <dt className="font-mono bg-secondary px-2 py-1 rounded min-w-[80px] text-center">
              &larr; / &rarr;
            </dt>
            <dd>Seek 5 seconds</dd>
          </div>
          <div className="flex gap-4">
            <dt className="font-mono bg-secondary px-2 py-1 rounded min-w-[80px] text-center">
              Shift+&larr;/&rarr;
            </dt>
            <dd>Seek 30 seconds</dd>
          </div>
          <div className="flex gap-4">
            <dt className="font-mono bg-secondary px-2 py-1 rounded min-w-[80px] text-center">
              &uarr; / &darr;
            </dt>
            <dd>Adjust volume</dd>
          </div>
          <div className="flex gap-4">
            <dt className="font-mono bg-secondary px-2 py-1 rounded min-w-[80px] text-center">
              M
            </dt>
            <dd>Mute / Unmute</dd>
          </div>
        </dl>
      </details>
    </div>
  );
}

function formatTime(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins.toString().padStart(2, '0')}:${secs
    .toString()
    .padStart(2, '0')}`;
}
