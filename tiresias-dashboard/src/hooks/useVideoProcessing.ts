'use client';

import { useCallback, useEffect, useState } from 'react';
import { api, type VideoStatusResponse } from '@/lib/api';

export function useVideoProcessing(videoId: string) {
  const [status, setStatus] = useState<VideoStatusResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStatus = useCallback(async () => {
    try {
      const data = await api.getVideoStatus(videoId);
      setStatus(data);
      setError(null);
      return data;
    } catch (err) {
      setError('Failed to fetch video status');
      return null;
    } finally {
      setIsLoading(false);
    }
  }, [videoId]);

  useEffect(() => {
    fetchStatus();

    // Poll while processing
    const interval = setInterval(async () => {
      const data = await fetchStatus();
      if (
        data &&
        (data.status === 'completed' || data.status === 'failed')
      ) {
        clearInterval(interval);
      }
    }, 3000);

    return () => clearInterval(interval);
  }, [fetchStatus]);

  return {
    status,
    isLoading,
    error,
    refetch: fetchStatus,
  };
}
