'use client';

import { useState } from 'react';
import { VideoUpload } from '@/components/video/VideoUpload';
import { URLInput } from '@/components/video/URLInput';

export default function UploadPage() {
  const [activeTab, setActiveTab] = useState<'upload' | 'url'>('upload');

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Add a Video</h1>
      <p className="text-foreground/70 mb-8">
        Upload a video file or paste a URL from a supported platform to
        generate audio descriptions.
      </p>

      {/* Tab selection */}
      <div
        role="tablist"
        aria-label="Video input method"
        className="flex gap-2 mb-8"
      >
        <button
          role="tab"
          aria-selected={activeTab === 'upload'}
          aria-controls="upload-panel"
          id="upload-tab"
          onClick={() => setActiveTab('upload')}
          className={`btn-secondary flex-1 ${
            activeTab === 'upload'
              ? 'ring-2 ring-primary bg-primary/10'
              : ''
          }`}
        >
          Upload File
        </button>
        <button
          role="tab"
          aria-selected={activeTab === 'url'}
          aria-controls="url-panel"
          id="url-tab"
          onClick={() => setActiveTab('url')}
          className={`btn-secondary flex-1 ${
            activeTab === 'url' ? 'ring-2 ring-primary bg-primary/10' : ''
          }`}
        >
          Paste URL
        </button>
      </div>

      {/* Upload panel */}
      <div
        role="tabpanel"
        id="upload-panel"
        aria-labelledby="upload-tab"
        hidden={activeTab !== 'upload'}
      >
        <VideoUpload />
      </div>

      {/* URL panel */}
      <div
        role="tabpanel"
        id="url-panel"
        aria-labelledby="url-tab"
        hidden={activeTab !== 'url'}
      >
        <URLInput />
      </div>
    </div>
  );
}
