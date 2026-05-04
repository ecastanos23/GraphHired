/*
 * COMENTARIO DE ARCHIVO - GRAPHHIRED
 * Hook cliente API. Partes: URL base, loading/error, manejo de token JWT, GET/POST/FormData/PUT/DELETE y errores HTTP.
 */
'use client';

import { useState, useCallback } from 'react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface UseApiReturn {
  loading: boolean;
  error: string | null;
  get: <T>(endpoint: string) => Promise<T | null>;
  post: <T>(endpoint: string, data: any) => Promise<T | null>;
  postForm: <T>(endpoint: string, data: FormData) => Promise<T | null>;
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
      const token = typeof window !== 'undefined' ? localStorage.getItem('graphhired_token') : null;
      const isFormData = options.body instanceof FormData;
      const response = await fetch(`${API_URL}${endpoint}`, {
        headers: {
          ...(isFormData ? {} : { 'Content-Type': 'application/json' }),
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
          ...options.headers,
        },
        ...options,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        const detail = typeof errorData.detail === 'string'
          ? errorData.detail
          : JSON.stringify(errorData.detail || errorData);
        throw new Error(detail || `HTTP error ${response.status}`);
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

  const postForm = useCallback(<T>(endpoint: string, data: FormData): Promise<T | null> => {
    return handleRequest<T>(endpoint, {
      method: 'POST',
      body: data,
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

  return { loading, error, get, post, postForm, put, del };
}
