'use client';

import { useParams } from 'next/navigation';
import { VideoPlayer } from '@/components/video/VideoPlayer';

export default function PlayerPage() {
  const params = useParams();
  const videoId = params.id as string;

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Video Player</h1>

      <VideoPlayer videoId={videoId} />

      {/* Download options */}
      <section aria-labelledby="downloads-heading" className="mt-8">
        <h2 id="downloads-heading" className="text-xl font-semibold mb-4">
          Download Options
        </h2>
        <div className="flex flex-col sm:flex-row gap-4">
          <a
            href={`/api/v1/videos/${videoId}/download?track=combined`}
            className="btn-primary"
            download
          >
            Video with Descriptions
          </a>
          <a
            href={`/api/v1/videos/${videoId}/download?track=description_only`}
            className="btn-secondary"
            download
          >
            Description Audio Only
          </a>
          <a
            href={`/api/v1/videos/${videoId}/download?track=transcript`}
            className="btn-secondary"
            download
          >
            Text Transcript
          </a>
        </div>
      </section>
    </div>
  );
}
