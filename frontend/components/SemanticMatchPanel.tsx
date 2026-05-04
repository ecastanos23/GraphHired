/*
 * COMENTARIO DE ARCHIVO - GRAPHHIRED
 * Panel de matching semantico. Partes: normalizacion de respuesta API, carga de resultados y render de vacantes por similitud.
 */
'use client';

import { useEffect, useState } from 'react';
import axios from 'axios';
import { HoverButton } from '@/components/ui/hover-glow-button';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface SemanticMatchItem {
  vacancy_id: number;
  title: string;
  company: string;
  similarity_score: number;
  work_modality: string | null;
  location: string | null;
}

interface SemanticMatchingResponse {
  status: string;
  engine: string | null;
  candidate_id: number;
  total_matches: number;
  matches: SemanticMatchItem[];
}

type SemanticMatchingApiResponse = {
  status?: string;
  engine?: string | null;
  candidate_id?: number;
  total_matches?: number;
  matches?: SemanticMatchItem[];
  data?: SemanticMatchItem[];
};

function normalizeSemanticResponse(
  payload: SemanticMatchingApiResponse,
  candidateId: number
): SemanticMatchingResponse {
  const fromMatches = Array.isArray(payload.matches) ? payload.matches : [];
  const fromData = Array.isArray(payload.data) ? payload.data : [];
  const matches = fromMatches.length > 0 ? fromMatches : fromData;

  return {
    status: payload.status || 'success',
    engine: payload.engine || 'sqlite',
    candidate_id: payload.candidate_id ?? candidateId,
    total_matches: payload.total_matches ?? matches.length,
    matches,
  };
}

interface SemanticMatchPanelProps {
  candidateId: number | null;
}

export default function SemanticMatchPanel({ candidateId }: SemanticMatchPanelProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [matchingInfo, setMatchingInfo] = useState<SemanticMatchingResponse | null>(null);

  const handleVacancyClick = (vacancyId: number) => {
    const cardId = `vacancy-card-${vacancyId}`;
    const element = document.getElementById(cardId);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'center' });
      element.classList.add('ring-2', 'ring-emerald-400', 'ring-offset-2');
      setTimeout(() => {
        element.classList.remove('ring-2', 'ring-emerald-400', 'ring-offset-2');
      }, 2500);
    }
  };

  const fetchSemanticMatch = async (currentCandidateId: number): Promise<void> => {
    const requestAt = Date.now();

    setLoading(true);
    setError(null);

    try {
      const response = await axios.get<SemanticMatchingApiResponse>(
        `${API_URL}/api/matching/semantic-match/${currentCandidateId}`,
        {
          params: {
            limit: 5,
            _ts: requestAt,
          },
          headers: {
            'Cache-Control': 'no-cache, no-store, max-age=0',
            Pragma: 'no-cache',
          },
        }
      );
      setMatchingInfo(normalizeSemanticResponse(response.data, currentCandidateId));
    } catch (err: any) {
      const detail = err?.response?.data?.detail;
      setError(detail || 'No se pudo ejecutar el matching semantico');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (candidateId) {
      void fetchSemanticMatch(candidateId);
      return;
    }

    setMatchingInfo(null);
    setError(null);
  }, [candidateId]);

  const engine = matchingInfo?.engine || 'sqlite';
  const safeMatches = matchingInfo?.matches || [];

  return (
    <section className="overflow-hidden rounded-3xl border border-slate-200/80 bg-white/90 shadow-[0_20px_70px_rgba(15,23,42,0.08)] backdrop-blur">
      <div className="bg-gradient-to-r from-slate-900 via-slate-800 to-emerald-800 px-6 py-5 text-white">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div className="space-y-1">
            <p className="text-xs uppercase tracking-[0.3em] text-emerald-200">Semantic search</p>
            <h3 className="text-xl font-semibold">Vacantes alineadas con el perfil</h3>
            <p className="text-sm text-slate-200 max-w-2xl">
              Ejecuta la búsqueda semántica sobre embeddings o, en modo local, una aproximación por texto.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <span
              className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-wide ${
                engine === 'pgvector'
                  ? 'bg-emerald-100 text-emerald-800'
                  : 'bg-amber-100 text-amber-800'
              }`}
            >
              Engine: {engine.toUpperCase()}
            </span>
            <HoverButton
              onClick={() => candidateId && void fetchSemanticMatch(candidateId)}
              disabled={!candidateId || loading}
              className="rounded-full px-4 py-2 text-sm font-semibold shadow-lg shadow-cyan-500/15"
              glowColor="#67e8f9"
              backgroundColor="#0f172a"
              textColor="#ffffff"
              hoverTextColor="#67e8f9"
            >
              {loading ? 'Actualizando...' : 'Actualizar matches'}
            </HoverButton>
          </div>
        </div>
      </div>

      <div className="space-y-4 p-6">
        {error && (
          <div className="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
            {error}
          </div>
        )}

        {loading && !matchingInfo && (
          <div className="flex items-center gap-3 rounded-2xl border border-slate-200 bg-slate-50 px-4 py-4 text-sm text-slate-600">
            <span className="h-3 w-3 animate-pulse rounded-full bg-emerald-500" />
            Calculando coincidencias semánticas...
          </div>
        )}

        {matchingInfo && (
          <div className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
              {safeMatches.map((item) => (
                <article
                  key={item.vacancy_id}
                  onClick={() => handleVacancyClick(item.vacancy_id)}
                  className="group cursor-pointer rounded-2xl border border-slate-200 bg-white p-4 shadow-sm transition hover:-translate-y-0.5 hover:shadow-lg hover:border-emerald-300"
                  style={{ cursor: 'pointer' }}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <h4 className="text-base font-semibold text-slate-900 group-hover:text-emerald-700">
                        {item.title}
                      </h4>
                      <p className="mt-1 text-sm text-slate-600">{item.company}</p>
                    </div>
                    <span className="rounded-full bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-700">
                      {item.similarity_score.toFixed(2)}%
                    </span>
                  </div>

                  <div className="mt-4 flex flex-wrap gap-2 text-xs text-slate-600">
                    <span className="rounded-full bg-slate-100 px-3 py-1">{item.work_modality || 'N/A'}</span>
                    <span className="rounded-full bg-slate-100 px-3 py-1">{item.location || 'N/A'}</span>
                  </div>
                </article>
              ))}
            </div>
          </div>
        )}

        {!matchingInfo && !loading && !error && candidateId && (
          <div className="rounded-2xl border border-dashed border-slate-300 bg-slate-50 px-4 py-6 text-sm text-slate-600">
            Selecciona un candidato para cargar sus coincidencias semánticas.
          </div>
        )}
      </div>
    </section>
  );
}
