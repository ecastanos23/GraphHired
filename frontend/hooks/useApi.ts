'use client';

import { useState, useCallback } from 'react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface UseApiReturn {
  loading: boolean;
  error: string | null;
  get: <T>(endpoint: string) => Promise<T | null>;
  post: <T>(endpoint: string, data: any) => Promise<T | null>;
  put: <T>(endpoint: string, data: any) => Promise<T | null>;
  del: (endpoint: string) => Promise<boolean>;
}

export function useApi(): UseApiReturn {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleRequest = async <T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T | null> => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_URL}${endpoint}`, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error ${response.status}`);
      }

      const data = await response.json();
      return data as T;
    } catch (err: any) {
      const message = err.message || 'An error occurred';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const get = useCallback(<T>(endpoint: string): Promise<T | null> => {
    return handleRequest<T>(endpoint, { method: 'GET' });
  }, []);

  const post = useCallback(<T>(endpoint: string, data: any): Promise<T | null> => {
    return handleRequest<T>(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }, []);

  const put = useCallback(<T>(endpoint: string, data: any): Promise<T | null> => {
    return handleRequest<T>(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }, []);

  const del = useCallback(async (endpoint: string): Promise<boolean> => {
    await handleRequest(endpoint, { method: 'DELETE' });
    return true;
  }, []);

  return { loading, error, get, post, put, del };
}
