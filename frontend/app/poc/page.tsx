/*
 * COMENTARIO DE ARCHIVO - GRAPHHIRED
 * Pagina PoC tecnica. Partes: formulario de texto, llamada a logs/process, refresco de logs y visualizacion del flujo UI-API-DB.
 */
'use client';

import { useState } from 'react';
import { useApi } from '@/hooks/useApi';
import { HoverButton } from '@/components/ui/hover-glow-button';

interface LogEntry {
  id: number;
  input_text: string;
  output_text: string;
  created_at: string;
}

const pipelineSteps = [
  {
    title: 'Next.js UI',
    description: 'Captura la entrada y muestra el estado del proceso con una interfaz clara.',
  },
  {
    title: 'FastAPI',
    description: 'Recibe el payload y coordina el flujo del backend sin mezclar responsabilidades.',
  },
  {
    title: 'LangGraph + DB',
    description: 'Transforma el texto y lo persiste en logs para verificar el recorrido completo.',
  },
];

export default function PoCPage() {
  const { post, get, loading, error } = useApi();
  const [inputText, setInputText] = useState('');
  const [result, setResult] = useState<LogEntry | null>(null);
  const [logs, setLogs] = useState<LogEntry[]>([]);

  const cardClassName = 'rounded-3xl border border-slate-200 bg-white p-6 shadow-sm transition-all duration-300 hover:-translate-y-0.5 hover:shadow-xl';

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
    <div className="space-y-8">
      <section className="overflow-hidden rounded-[2rem] border border-slate-200 bg-white shadow-[0_18px_60px_rgba(15,23,42,0.08)]">
        <div className="bg-[radial-gradient(circle_at_top_left,_rgba(16,185,129,0.20),_transparent_30%),radial-gradient(circle_at_top_right,_rgba(15,23,42,0.12),_transparent_24%),linear-gradient(135deg,_#0f172a_0%,_#111827_50%,_#064e3b_100%)] px-6 py-8 text-white sm:px-8 lg:px-10">
          <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
            <div className="max-w-2xl space-y-4">
              <div className="inline-flex items-center rounded-full border border-white/15 bg-white/10 px-3 py-1 text-xs font-semibold uppercase tracking-[0.28em] text-emerald-100">
                PoC técnica
              </div>
              <div className="space-y-2">
                <h1 className="text-3xl font-semibold tracking-tight sm:text-4xl lg:text-5xl">
                  Prueba vertical del flujo de IA
                </h1>
                <p className="max-w-2xl text-sm leading-6 text-slate-200 sm:text-base">
                  Valida la ruta completa desde la interfaz hasta el almacenamiento, con el mismo lenguaje visual del resto de GraphHired.
                </p>
              </div>
            </div>

            <div className="grid gap-3 sm:grid-cols-3 lg:max-w-xl lg:grid-cols-1 xl:grid-cols-3">
              {pipelineSteps.map((step, index) => (
                <div key={step.title} className="rounded-2xl border border-white/15 bg-white/10 p-4 backdrop-blur-sm transition-all duration-300 hover:bg-white/15 hover:-translate-y-0.5">
                  <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-emerald-400/20 text-sm font-semibold text-emerald-100 ring-1 ring-inset ring-emerald-300/30">
                      0{index + 1}
                    </div>
                    <div>
                      <p className="text-sm font-semibold text-white">{step.title}</p>
                      <p className="text-xs leading-5 text-slate-200">{step.description}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className="grid gap-6 lg:grid-cols-[1.05fr_0.95fr]">
        <div className={cardClassName}>
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.24em] text-emerald-700">Procesador</p>
              <h2 className="mt-2 text-2xl font-semibold text-slate-900">Escribe una entrada de prueba</h2>
              <p className="mt-2 text-sm leading-6 text-slate-600">
                Este panel te permite confirmar la conectividad entre la UI, el backend y la persistencia de logs.
              </p>
            </div>

            <HoverButton
              onClick={fetchLogs}
              className="rounded-full px-4 py-2 text-sm font-semibold"
              glowColor="#67e8f9"
              backgroundColor="#0f172a"
              textColor="#e2e8f0"
              hoverTextColor="#67e8f9"
            >
              Actualizar logs
            </HoverButton>
          </div>

          <form onSubmit={handleSubmit} className="mt-6 space-y-5">
            <div>
              <label htmlFor="input" className="block text-sm font-medium text-slate-700">
                Texto de entrada
              </label>
              <input
                type="text"
                id="input"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                className="mt-1 block w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition-all duration-300 placeholder:text-slate-400 focus:border-emerald-400 focus:ring-4 focus:ring-emerald-200/60"
                placeholder="Escribe algo para transformar a mayúsculas..."
              />
            </div>

            <HoverButton
              type="submit"
              disabled={loading || !inputText.trim()}
              className="w-full rounded-2xl py-4 text-base font-semibold shadow-lg shadow-emerald-500/20"
              glowColor="#34d399"
              backgroundColor="#10b981"
              textColor="#ffffff"
              hoverTextColor="#d1fae5"
            >
              {loading ? 'Procesando...' : 'Procesar'}
            </HoverButton>
          </form>

          {error && (
            <div className="mt-6 rounded-2xl border border-rose-200 bg-rose-50 p-4">
              <p className="text-rose-800">Error: {error}</p>
            </div>
          )}

          {result && (
            <div className="mt-6 rounded-2xl border border-emerald-200 bg-emerald-50 p-4">
              <h3 className="font-semibold text-emerald-800">Resultado guardado en DB</h3>
              <div className="mt-4 grid gap-4 md:grid-cols-2 text-sm">
                <div className="rounded-2xl border border-white bg-white p-3">
                  <span className="text-slate-500">Entrada</span>
                  <p className="mt-1 rounded-xl bg-slate-50 p-3 font-mono text-slate-800">{result.input_text}</p>
                </div>
                <div className="rounded-2xl border border-white bg-white p-3">
                  <span className="text-slate-500">Salida (LangGraph)</span>
                  <p className="mt-1 rounded-xl bg-slate-50 p-3 font-mono font-bold text-emerald-700">
                    {result.output_text}
                  </p>
                </div>
              </div>
              <p className="mt-3 text-xs text-slate-500">
                ID: {result.id} | Guardado: {new Date(result.created_at).toLocaleString()}
              </p>
            </div>
          )}
        </div>

        <div className="space-y-6">
          <div className={cardClassName}>
            <div className="flex items-center justify-between gap-4">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.24em] text-emerald-700">Logs</p>
                <h2 className="mt-2 text-2xl font-semibold text-slate-900">Registros recientes</h2>
              </div>
              <HoverButton
                onClick={fetchLogs}
                className="rounded-full px-4 py-2 text-sm font-semibold"
                glowColor="#67e8f9"
                backgroundColor="#0f172a"
                textColor="#e2e8f0"
                hoverTextColor="#67e8f9"
              >
                Refrescar
              </HoverButton>
            </div>

            {logs.length > 0 ? (
              <div className="mt-6 overflow-hidden rounded-2xl border border-slate-200">
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead className="bg-slate-50 text-slate-600">
                      <tr>
                        <th className="px-4 py-3 text-left font-medium">ID</th>
                        <th className="px-4 py-3 text-left font-medium">Entrada</th>
                        <th className="px-4 py-3 text-left font-medium">Salida</th>
                        <th className="px-4 py-3 text-left font-medium">Fecha</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-200 bg-white">
                      {logs.map((log) => (
                        <tr key={log.id} className="transition-colors hover:bg-slate-50">
                          <td className="px-4 py-3 font-mono text-slate-700">{log.id}</td>
                          <td className="px-4 py-3 text-slate-700">{log.input_text}</td>
                          <td className="px-4 py-3 font-semibold text-emerald-700">{log.output_text}</td>
                          <td className="px-4 py-3 text-slate-500">
                            {new Date(log.created_at).toLocaleString()}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            ) : (
              <div className="mt-6 rounded-2xl border border-dashed border-slate-300 bg-slate-50 px-4 py-8 text-center text-slate-600">
                No hay registros. Procesa un texto para empezar.
              </div>
            )}
          </div>

          <div className="rounded-3xl border border-slate-200 bg-[radial-gradient(circle_at_top,_rgba(16,185,129,0.12),_transparent_35%),linear-gradient(180deg,_#ffffff_0%,_#f8fafc_100%)] p-6 shadow-sm">
            <p className="text-xs font-semibold uppercase tracking-[0.24em] text-emerald-700">Flujo de datos</p>
            <div className="mt-4 flex flex-wrap items-center gap-2 text-sm">
              <span className="rounded-full bg-slate-900 px-3 py-1 text-white">Next.js UI</span>
              <span className="text-slate-400">→</span>
              <span className="rounded-full bg-emerald-500 px-3 py-1 text-white">FastAPI</span>
              <span className="text-slate-400">→</span>
              <span className="rounded-full bg-slate-700 px-3 py-1 text-white">LangGraph Node</span>
              <span className="text-slate-400">→</span>
              <span className="rounded-full bg-slate-500 px-3 py-1 text-white">PostgreSQL</span>
            </div>
            <p className="mt-4 text-sm leading-6 text-slate-600">
              El texto pasa por un nodo de LangGraph que lo transforma a mayúsculas y se guarda en la tabla "logs".
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
