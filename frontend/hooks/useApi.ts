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
    options: RequestInit = {},
    timeoutMs: number = 30000
  ): Promise<T | null> => {
    setLoading(true);
    setError(null);

    try {
      // Obtener token JWT del localStorage
      const token = typeof window !== 'undefined' ? localStorage.getItem('graphhired_token') : null;
      const isFormData = options.body instanceof FormData;
      
      // Crear controlador de abortó con timeout automático
      const controller = new AbortController();
      const timeoutId = setTimeout(() => {
        console.warn(`⏱️ Timeout después de ${timeoutMs}ms en ${endpoint} - abortando solicitud`);
        controller.abort();
      }, timeoutMs);
      
      try {
        // Log de debug: mostrar inicio de la solicitud
        console.debug(`📤 Iniciando ${options.method || 'GET'} a ${API_URL}${endpoint}`);
        
        const response = await fetch(`${API_URL}${endpoint}`, {
          headers: {
            ...(isFormData ? {} : { 'Content-Type': 'application/json' }),
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
            ...options.headers,
          },
          ...options,
          signal: controller.signal, // Pasar la señal de abort
        });

        // Limpiar timeout si la solicitud fue exitosa
        clearTimeout(timeoutId);

        // Log de debug: mostrar código de respuesta
        console.debug(`📥 Respuesta ${response.status} desde ${endpoint}`);

        if (!response.ok) {
          // Intentar parsear el error JSON del servidor
          const errorData = await response.json().catch(() => ({}));
          const detail = typeof errorData.detail === 'string'
            ? errorData.detail
            : JSON.stringify(errorData.detail || errorData);
          
          const errorMsg = detail || `HTTP error ${response.status}`;
          console.error(`❌ Error HTTP ${response.status}: ${errorMsg}`);
          throw new Error(errorMsg);
        }

        const data = await response.json();
        console.debug(`✅ Datos recibidos exitosamente de ${endpoint}`);
        return data as T;
      } catch (fetchErr: any) {
        clearTimeout(timeoutId);
        
        // Diferenciar entre timeout y otros errores
        if (fetchErr.name === 'AbortError') {
          const msg = `⏱️ La solicitud a ${endpoint} tardó más de ${timeoutMs}ms`;
          console.error(msg);
          throw new Error(msg);
        }
        
        // Otros errores de fetch (CORS, conexión rechazada, etc)
        console.error(`🔴 Error en fetch para ${endpoint}:`, fetchErr.message);
        throw fetchErr;
      }
    } catch (err: any) {
      const message = err.message || 'An error occurred';
      console.error(`API Error en ${options.method || 'GET'} ${endpoint}:`, message);
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

  const del = useCallback((endpoint: string): Promise<boolean> => {
    return handleRequest<boolean>(endpoint, { method: 'DELETE' }).then(
      (res) => !!res
    );
  }, []);

  return { loading, error, get, post, postForm, put, del };
}
