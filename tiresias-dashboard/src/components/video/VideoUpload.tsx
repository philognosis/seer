'use client';

import React, { useCallback, useRef, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Upload, X } from 'lucide-react';
import { useLiveRegion } from '@/components/accessibility/LiveRegion';
import { api } from '@/lib/api';

const ACCEPTED_TYPES = ['video/mp4', 'video/quicktime', 'video/x-msvideo', 'video/webm'];
const MAX_FILE_SIZE = 524288000; // 500MB

export function VideoUpload() {
  const router = useRouter();
  const { announce } = useLiveRegion();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [voice, setVoice] = useState('female_us');
  const [llmProvider, setLlmProvider] = useState('gemini');
  const [density, setDensity] = useState('standard');
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dragActive, setDragActive] = useState(false);

  const handleFileSelect = useCallback(
    (selectedFile: File) => {
      setError(null);

      if (!ACCEPTED_TYPES.includes(selectedFile.type)) {
        const msg = 'Unsupported file type. Please upload MP4, MOV, AVI, or WEBM.';
        setError(msg);
        announce(msg, 'assertive');
        return;
      }

      if (selectedFile.size > MAX_FILE_SIZE) {
        const msg = 'File too large. Maximum size is 500MB.';
        setError(msg);
        announce(msg, 'assertive');
        return;
      }

      setFile(selectedFile);
      announce(`File selected: ${selectedFile.name}`);
    },
    [announce]
  );

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragActive(false);
      if (e.dataTransfer.files?.[0]) {
        handleFileSelect(e.dataTransfer.files[0]);
      }
    },
    [handleFileSelect]
  );

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;

    setIsUploading(true);
    setError(null);
    announce('Uploading video. Please wait.');

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('voice', voice);
      formData.append('llm_provider', llmProvider);
      formData.append('description_density', density);

      const response = await api.uploadVideo(formData);
      announce('Video uploaded successfully. Redirecting to processing page.');
      router.push(`/process/${response.video_id}`);
    } catch (err) {
      const msg = 'Upload failed. Please try again.';
      setError(msg);
      announce(msg, 'assertive');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Drop zone */}
      <div
        className={`card border-2 border-dashed p-12 text-center cursor-pointer transition-colors ${
          dragActive ? 'border-primary bg-primary/5' : 'border-border'
        }`}
        onClick={() => fileInputRef.current?.click()}
        onDragOver={(e) => {
          e.preventDefault();
          setDragActive(true);
        }}
        onDragLeave={() => setDragActive(false)}
        onDrop={handleDrop}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            fileInputRef.current?.click();
          }
        }}
        role="button"
        tabIndex={0}
        aria-label="Drop zone. Click or drag a video file here to upload."
      >
        <input
          ref={fileInputRef}
          type="file"
          accept="video/mp4,video/quicktime,video/x-msvideo,video/webm"
          onChange={(e) => e.target.files?.[0] && handleFileSelect(e.target.files[0])}
          className="sr-only"
          aria-label="Select video file"
        />

        <Upload className="w-12 h-12 mx-auto mb-4 text-foreground/50" aria-hidden="true" />

        {file ? (
          <div>
            <p className="font-semibold">{file.name}</p>
            <p className="text-sm text-foreground/60">
              {(file.size / (1024 * 1024)).toFixed(1)} MB
            </p>
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                setFile(null);
                announce('File removed');
              }}
              className="mt-2 text-destructive hover:underline"
              aria-label={`Remove file ${file.name}`}
            >
              <X className="w-4 h-4 inline mr-1" aria-hidden="true" />
              Remove
            </button>
          </div>
        ) : (
          <div>
            <p className="font-semibold">
              Drop a video file here or click to browse
            </p>
            <p className="text-sm text-foreground/60 mt-1">
              MP4, MOV, AVI, or WEBM up to 500MB
            </p>
          </div>
        )}
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
          <label htmlFor="voice-select" className="block font-medium mb-1">
            Narration Voice
          </label>
          <select
            id="voice-select"
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
          <label htmlFor="llm-select" className="block font-medium mb-1">
            AI Model
          </label>
          <select
            id="llm-select"
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
          <label htmlFor="density-select" className="block font-medium mb-1">
            Description Density
          </label>
          <select
            id="density-select"
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
        disabled={!file || isUploading}
        className="btn-primary w-full text-lg"
        aria-busy={isUploading}
      >
        {isUploading ? 'Uploading...' : 'Generate Audio Descriptions'}
      </button>
    </form>
  );
}
