'use client';

import { useEffect, useState } from 'react';

interface DiagnosticResult {
  endpoint: string;
  status: 'checking' | 'success' | 'failed' | 'timeout';
  statusCode?: number;
  error?: string;
  responseTime?: number;
}

export default function DiagnosticPage() {
  // Estado para almacenar resultados de diagnóstico
  const [results, setResults] = useState<DiagnosticResult[]>([]);
  // Estado para saber si estamos verificando
  const [isChecking, setIsChecking] = useState(false);
  // URL base de la API
  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  // Función para verificar un endpoint
  const checkEndpoint = async (endpoint: string): Promise<DiagnosticResult> => {
    const startTime = performance.now();
    const result: DiagnosticResult = {
      endpoint,
      status: 'checking',
    };

    try {
      // Realizar la solicitud con timeout
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 segundos de timeout

      console.log(`🔍 Verificando ${endpoint}...`);
      
      const response = await fetch(`${API_URL}${endpoint}`, {
        method: 'GET',
        signal: controller.signal,
      });

      clearTimeout(timeoutId);
      const responseTime = performance.now() - startTime;

      if (response.ok) {
        result.status = 'success';
        result.statusCode = response.status;
        result.responseTime = Math.round(responseTime);
        console.log(`✅ ${endpoint} respondió correctamente (${responseTime.toFixed(0)}ms)`);
      } else {
        result.status = 'failed';
        result.statusCode = response.status;
        result.error = `HTTP ${response.status}`;
        result.responseTime = Math.round(responseTime);
        console.log(`❌ ${endpoint} retornó HTTP ${response.status}`);
      }
    } catch (err: any) {
      const responseTime = performance.now() - startTime;

      // Diferenciar entre timeout y otros errores
      if (err.name === 'AbortError') {
        result.status = 'timeout';
        result.error = 'Timeout después de 5 segundos';
        console.log(`⏱️ ${endpoint} agotó el timeout`);
      } else {
        result.status = 'failed';
        result.error = err.message || String(err);
        console.log(`❌ ${endpoint} error: ${err.message}`);
      }
      result.responseTime = Math.round(responseTime);
    }

    return result;
  };

  // Ejecutar diagnóstico cuando el componente se monta
  useEffect(() => {
    const runDiagnostic = async () => {
      setIsChecking(true);
      // Lista de endpoints a verificar
      // NOTA: Usamos un candidate_id genérico (1) para el test de trace
      // Si no existe ese candidato, el endpoint ahora retorna lista vacía (HTTP 200) en lugar de 404
      const endpoints = [
        '/health', // Health check del servidor FastAPI
        '/api/vacancies', // Verificar que vacantes están disponibles
        '/api/agents/trace?candidate_id=999999&limit=1', // Test trace con ID que probablemente no existe (pero es OK)
      ];

      // Verificar cada endpoint
      const newResults: DiagnosticResult[] = [];
      for (const endpoint of endpoints) {
        const result = await checkEndpoint(endpoint);
        newResults.push(result);
        setResults([...newResults]); // Actualizar estado en tiempo real
      }

      setIsChecking(false);
    };

    runDiagnostic();
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 p-8">
      <div className="max-w-4xl mx-auto">
        {/* Encabezado */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">🔍 Diagnóstico de Backend</h1>
          <p className="text-slate-300">
            Verifica la disponibilidad de la API en <code className="bg-slate-800 px-2 py-1 rounded text-yellow-400">{process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}</code>
          </p>
        </div>

        {/* Información general */}
        <div className="bg-slate-800 rounded-lg p-6 mb-8 border border-slate-700">
          <h2 className="text-xl font-semibold text-white mb-4">📋 Información del Diagnóstico</h2>
          <div className="space-y-2 text-sm text-slate-300">
            <p>
              <span className="font-semibold text-white">API Base URL:</span> {API_URL}
            </p>
            <p>
              <span className="font-semibold text-white">Navegador:</span> {typeof window !== 'undefined' ? navigator.userAgent.substring(0, 60) : 'N/A'}...
            </p>
            <p>
              <span className="font-semibold text-white">Estado:</span>{' '}
              {isChecking ? (
                <span className="text-yellow-400 animate-pulse">🔄 Verificando endpoints...</span>
              ) : (
                <span className="text-green-400">✅ Verificación completada</span>
              )}
            </p>
          </div>
        </div>

        {/* Resultados de endpoints */}
        <div className="space-y-4">
          <h2 className="text-2xl font-bold text-white mb-4">📊 Resultados de Endpoints</h2>

          {results.length === 0 && !isChecking && (
            <div className="bg-slate-800 rounded-lg p-6 border border-slate-700 text-center text-slate-400">
              Haz clic en "Reintentar Diagnóstico" para verificar los endpoints
            </div>
          )}

          {/* Mostrar cada resultado */}
          {results.map((result) => (
            <div
              key={result.endpoint}
              className={`rounded-lg p-6 border-2 transition-all ${
                result.status === 'success'
                  ? 'bg-green-900 border-green-500 text-green-50'
                  : result.status === 'checking'
                  ? 'bg-yellow-900 border-yellow-500 text-yellow-50 animate-pulse'
                  : result.status === 'timeout'
                  ? 'bg-orange-900 border-orange-500 text-orange-50'
                  : 'bg-red-900 border-red-500 text-red-50'
              }`}
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-3 flex-1">
                  {/* Icono de estado */}
                  <span className="text-2xl">
                    {result.status === 'success'
                      ? '✅'
                      : result.status === 'checking'
                      ? '🔄'
                      : result.status === 'timeout'
                      ? '⏱️'
                      : '❌'}
                  </span>
                  {/* Endpoint y código de estado */}
                  <div className="flex-1">
                    <code className="text-sm font-mono break-all">{result.endpoint}</code>
                    {result.statusCode && (
                      <span className="ml-2 font-semibold text-sm">HTTP {result.statusCode}</span>
                    )}
                  </div>
                </div>

                {/* Tiempo de respuesta */}
                {result.responseTime && (
                  <span className="ml-4 text-sm font-semibold whitespace-nowrap">
                    {result.responseTime}ms
                  </span>
                )}
              </div>

              {/* Mensaje de error si hay */}
              {result.error && (
                <div className="mt-2 text-sm opacity-90 pl-11">
                  <span className="font-semibold">Error:</span> {result.error}
                </div>
              )}

              {/* Detalles del estado */}
              {result.status === 'timeout' && (
                <div className="mt-2 text-sm opacity-90 pl-11">
                  <p>
                    ⏱️ <span className="font-semibold">El backend está lento o no está respondiendo.</span>
                  </p>
                  <p className="mt-1">Soluciones:</p>
                  <ul className="list-disc list-inside mt-2 space-y-1">
                    <li>Verifica que <code className="bg-slate-700 px-1">docker compose up</code> esté ejecutándose</li>
                    <li>Revisa los logs del backend: <code className="bg-slate-700 px-1">docker compose logs backend</code></li>
                    <li>Espera unos segundos a que el backend inicie completamente</li>
                  </ul>
                </div>
              )}

              {result.status === 'failed' && !result.error?.includes('AbortError') && (
                <div className="mt-2 text-sm opacity-90 pl-11">
                  <p>
                    ❌ <span className="font-semibold">El servidor no pudo procesar la solicitud.</span>
                  </p>
                  <p className="mt-1">Posible causa: Verifica los logs del backend o si el endpoint existe</p>
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Botón para reintentar */}
        <div className="mt-8 flex gap-4">
          <button
            onClick={() => window.location.reload()}
            className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors"
            disabled={isChecking}
          >
            {isChecking ? '🔄 Verificando...' : '🔄 Reintentar Diagnóstico'}
          </button>

          <a
            href="/dashboard"
            className="px-6 py-3 bg-slate-700 hover:bg-slate-600 text-white font-semibold rounded-lg transition-colors"
          >
            ← Volver al Dashboard
          </a>
        </div>

        {/* Instrucciones */}
        <div className="mt-8 bg-slate-800 rounded-lg p-6 border border-slate-700">
          <h3 className="text-lg font-semibold text-white mb-4">📚 Cómo usar este diagnóstico</h3>
          <ol className="list-decimal list-inside space-y-2 text-slate-300 text-sm">
            <li>
              <span className="font-semibold">Si ves ✅ en todos los endpoints:</span> El backend está funcionando correctamente. Si el dashboard aún falla, el problema está en el frontend.
            </li>
            <li>
              <span className="font-semibold">Si ves ⏱️ timeout:</span> El backend está lento o iniciándose. Espera unos segundos y reintentar.
            </li>
            <li>
              <span className="font-semibold">Si ves ❌ error:</span> El backend tiene un problema. Revisa los logs con: <code className="bg-slate-700 px-2 py-1 rounded text-yellow-400">docker compose logs backend</code>
            </li>
          </ol>
        </div>

        {/* Console logs helper */}
        <div className="mt-8 bg-slate-800 rounded-lg p-6 border border-slate-700">
          <h3 className="text-lg font-semibold text-white mb-4">💡 Tip: Abre la consola del navegador</h3>
          <p className="text-slate-300 text-sm mb-4">
            Presiona <kbd className="bg-slate-700 px-2 py-1 rounded">F12</kbd> para abrir las herramientas de desarrollador y ver más detalles de las solicitudes.
          </p>
          <p className="text-slate-300 text-sm">
            En la pestaña <span className="font-semibold text-yellow-400">Console</span> verás logs detallados de cada verificación.
          </p>
        </div>
      </div>
    </div>
  );
}
