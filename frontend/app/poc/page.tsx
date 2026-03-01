'use client';

import { useState } from 'react';
import { useApi } from '@/hooks/useApi';

interface LogEntry {
  id: number;
  input_text: string;
  output_text: string;
  created_at: string;
}

export default function PoCPage() {
  const { post, get, loading, error } = useApi();
  const [inputText, setInputText] = useState('');
  const [result, setResult] = useState<LogEntry | null>(null);
  const [logs, setLogs] = useState<LogEntry[]>([]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim()) return;

    try {
      const response = await post<LogEntry>('/api/logs/process', { input_text: inputText });
      setResult(response);
      setInputText('');
      // Refresh logs
      fetchLogs();
    } catch (err) {
      console.error('Error processing text:', err);
    }
  };

  const fetchLogs = async () => {
    try {
      const data = await get<LogEntry[]>('/api/logs?limit=10');
      setLogs(data || []);
    } catch (err) {
      console.error('Error fetching logs:', err);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div className="bg-white rounded-xl shadow-md p-8">
        <h1 className="text-2xl font-bold mb-2">PoC - Hello World Tecnológico</h1>
        <p className="text-gray-600 mb-6">
          Prueba de conectividad vertical: FastAPI → LangGraph → PostgreSQL
        </p>

        {/* Test Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="input" className="form-label">
              Texto de entrada
            </label>
            <input
              type="text"
              id="input"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              className="form-input border border-gray-300"
              placeholder="Escribe algo para transformar a mayúsculas..."
            />
          </div>
          <button
            type="submit"
            disabled={loading || !inputText.trim()}
            className="btn-primary disabled:opacity-50"
          >
            {loading ? 'Procesando...' : 'Procesar con LangGraph'}
          </button>
        </form>

        {error && (
          <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-800">Error: {error}</p>
          </div>
        )}

        {/* Result */}
        {result && (
          <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg">
            <h3 className="font-semibold text-green-800 mb-2">✓ Resultado guardado en DB</h3>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-gray-600">Entrada:</span>
                <p className="font-mono bg-white p-2 rounded mt-1">{result.input_text}</p>
              </div>
              <div>
                <span className="text-gray-600">Salida (LangGraph):</span>
                <p className="font-mono bg-white p-2 rounded mt-1 text-primary-600 font-bold">
                  {result.output_text}
                </p>
              </div>
            </div>
            <p className="text-xs text-gray-500 mt-2">
              ID: {result.id} | Guardado: {new Date(result.created_at).toLocaleString()}
            </p>
          </div>
        )}
      </div>

      {/* Logs Table */}
      <div className="bg-white rounded-xl shadow-md p-8">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">Registros en Base de Datos</h2>
          <button onClick={fetchLogs} className="btn-secondary text-sm">
            Actualizar
          </button>
        </div>

        {logs.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-2 text-left">ID</th>
                  <th className="px-4 py-2 text-left">Entrada</th>
                  <th className="px-4 py-2 text-left">Salida</th>
                  <th className="px-4 py-2 text-left">Fecha</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {logs.map((log) => (
                  <tr key={log.id}>
                    <td className="px-4 py-2 font-mono">{log.id}</td>
                    <td className="px-4 py-2">{log.input_text}</td>
                    <td className="px-4 py-2 font-bold text-primary-600">{log.output_text}</td>
                    <td className="px-4 py-2 text-gray-500">
                      {new Date(log.created_at).toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-gray-500 text-center py-4">
            No hay registros. Procesa un texto para empezar.
          </p>
        )}
      </div>

      {/* Architecture Info */}
      <div className="bg-gray-800 text-white rounded-xl p-6">
        <h3 className="font-semibold mb-3">📐 Flujo de Datos</h3>
        <div className="flex items-center justify-center gap-4 text-sm">
          <span className="bg-blue-600 px-3 py-1 rounded">Next.js UI</span>
          <span>→</span>
          <span className="bg-green-600 px-3 py-1 rounded">FastAPI</span>
          <span>→</span>
          <span className="bg-purple-600 px-3 py-1 rounded">LangGraph Node</span>
          <span>→</span>
          <span className="bg-orange-600 px-3 py-1 rounded">PostgreSQL</span>
        </div>
        <p className="text-gray-400 text-xs mt-4 text-center">
          El texto pasa por un nodo de LangGraph que lo transforma a mayúsculas y se guarda en la tabla "logs"
        </p>
      </div>
    </div>
  );
}
