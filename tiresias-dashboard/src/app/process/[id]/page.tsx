'use client';

import { useParams } from 'next/navigation';
import { ProcessingProgress } from '@/components/video/ProcessingProgress';

export default function ProcessPage() {
  const params = useParams();
  const videoId = params.id as string;

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Processing Video</h1>
      <p className="text-foreground/70 mb-8">
        Your video is being processed. Audio descriptions are being generated
        automatically. This page will update with progress.
      </p>

      <ProcessingProgress videoId={videoId} />
    </div>
  );
}
