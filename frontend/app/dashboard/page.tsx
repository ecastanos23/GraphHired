'use client';

import { Suspense, useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import { useApi } from '@/hooks/useApi';
import MatchCard from '@/components/MatchCard';
import NotificationToast from '@/components/NotificationToast';

interface Match {
  vacancy_id: number;
  title: string;
  company: string;
  match_score: number;
  salary_range: string;
  work_modality: string | null;
  location: string | null;
  matching_skills: string[];
  missing_skills: string[];
}

interface MatchingResponse {
  candidate_id: number;
  candidate_name: string;
  total_matches: number;
  matches: Match[];
}

interface Candidate {
  id: number;
  email: string;
  full_name: string;
  phone?: string | null;
  cv_text?: string | null;
  expected_salary?: string | null;
  work_modality?: string | null;
  location?: string | null;
  skills?: string[];
  experience_years?: number;
}

function DashboardContent() {
  const searchParams = useSearchParams();
  const candidateIdParam = searchParams.get('candidateId');
  
  const { get, post, loading } = useApi();
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [selectedCandidate, setSelectedCandidate] = useState<number | null>(
    candidateIdParam ? parseInt(candidateIdParam) : null
  );
  const [matches, setMatches] = useState<MatchingResponse | null>(null);
  const [notification, setNotification] = useState<{show: boolean; message: string; type: 'success' | 'error'}>({
    show: false,
    message: '',
    type: 'success'
  });

  // Load candidates on mount
  useEffect(() => {
    const fetchCandidates = async () => {
      try {
        const data = await get<Candidate[]>('/api/candidates');
        setCandidates(data || []);
      } catch (err) {
        console.error('Error fetching candidates:', err);
      }
    };
    fetchCandidates();
  }, []);

  // Load matches when candidate is selected
  useEffect(() => {
    if (selectedCandidate) {
      fetchMatches(selectedCandidate);
    }
  }, [selectedCandidate]);

  const fetchMatches = async (candidateId: number) => {
    try {
      const data = await get<MatchingResponse>(`/api/matching/candidate/${candidateId}?min_score=0&limit=20`);
      setMatches(data);
    } catch (err) {
      console.error('Error fetching matches:', err);
    }
  };

  const handleApply = async (vacancyId: number) => {
    if (!selectedCandidate) return;

    try {
      await post('/api/matching/apply', {
        candidate_id: selectedCandidate,
        vacancy_id: vacancyId
      });
      
      setNotification({
        show: true,
        message: '¡Postulación exitosa! Tu aplicación ha sido enviada.',
        type: 'success'
      });

      // Refresh matches to update UI
      fetchMatches(selectedCandidate);
    } catch (err: any) {
      setNotification({
        show: true,
        message: err.message || 'Error al postularse',
        type: 'error'
      });
    }
  };

  const getScoreBadgeClass = (score: number): string => {
    if (score >= 80) return 'badge-excellent';
    if (score >= 60) return 'badge-good';
    if (score >= 40) return 'badge-fair';
    return 'badge-low';
  };

  const selectedCandidateData = candidates.find((candidate) => candidate.id === selectedCandidate);

  return (
    <div className="space-y-8">
      <NotificationToast 
        show={notification.show}
        message={notification.message}
        type={notification.type}
        onClose={() => setNotification(prev => ({ ...prev, show: false }))}
      />

      <section className="overflow-hidden rounded-[2rem] border border-slate-200 bg-white shadow-[0_18px_60px_rgba(15,23,42,0.08)]">
        <div className="bg-[radial-gradient(circle_at_top_left,_rgba(16,185,129,0.25),_transparent_30%),linear-gradient(135deg,_#0f172a_0%,_#111827_50%,_#064e3b_100%)] px-6 py-8 text-white sm:px-8">
          <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
            <div className="max-w-2xl space-y-4">
              <div className="inline-flex items-center rounded-full border border-white/15 bg-white/10 px-3 py-1 text-xs font-semibold uppercase tracking-[0.28em] text-emerald-100">
                GraphHired Search
              </div>
              <div className="space-y-2">
                <h1 className="text-3xl font-semibold tracking-tight sm:text-4xl">
                  Encuentra vacantes que realmente encajan con el perfil
                </h1>
                <p className="text-sm leading-6 text-slate-200 sm:text-base">
                  Explora coincidencias exactas con pgvector o aproximadas en modo local. Elige un candidato y revisa sus resultados en un formato tipo buscador profesional.
                </p>
              </div>
            </div>

            <div className="w-full max-w-md rounded-3xl border border-white/15 bg-white/10 p-4 backdrop-blur-sm">
              <label className="mb-2 block text-sm font-medium text-slate-100">Candidato</label>
              <select
                value={selectedCandidate || ''}
                onChange={(e) => setSelectedCandidate(e.target.value ? parseInt(e.target.value) : null)}
                className="w-full rounded-2xl border border-white/20 bg-white/95 px-4 py-3 text-sm text-slate-900 shadow-sm outline-none transition focus:border-emerald-400 focus:ring-2 focus:ring-emerald-200"
              >
                <option value="">Seleccionar candidato...</option>
                {candidates.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.full_name} ({c.email})
                  </option>
                ))}
              </select>
              {selectedCandidateData && (
                <div className="mt-3 flex flex-wrap gap-2 text-xs text-slate-100/90">
                  {selectedCandidateData.work_modality && (
                    <span className="rounded-full bg-white/10 px-3 py-1">{selectedCandidateData.work_modality}</span>
                  )}
                  {selectedCandidateData.location && (
                    <span className="rounded-full bg-white/10 px-3 py-1">{selectedCandidateData.location}</span>
                  )}
                  {typeof selectedCandidateData.experience_years === 'number' && (
                    <span className="rounded-full bg-white/10 px-3 py-1">
                      {selectedCandidateData.experience_years} años exp.
                    </span>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </section>

      {!selectedCandidate && (
        <div className="rounded-2xl border border-amber-200 bg-amber-50 p-6 text-center">
          <p className="text-amber-900">
            Selecciona un candidato para ver las vacantes recomendadas, o{' '}
            <a href="/upload" className="font-semibold text-emerald-700 underline decoration-emerald-300 underline-offset-4">sube tu CV</a> primero.
          </p>
        </div>
      )}

      {selectedCandidate && loading && (
        <div className="rounded-2xl border border-slate-200 bg-white p-12 text-center shadow-sm">
          <div className="mx-auto h-12 w-12 animate-spin rounded-full border-b-2 border-emerald-600"></div>
          <p className="mt-4 text-slate-600">Calculando matches...</p>
        </div>
      )}

      {selectedCandidate && matches && !loading && (
        <div className="space-y-8">
          <section className="grid gap-4 lg:grid-cols-[1.4fr_0.6fr]">
            <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
              <div className="flex flex-wrap items-start justify-between gap-4">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-[0.24em] text-emerald-700">Perfil activo</p>
                  <h2 className="mt-2 text-2xl font-semibold text-slate-900">{matches.candidate_name}</h2>
                  <p className="mt-1 text-sm text-slate-600">
                  {matches.total_matches} vacantes encontradas
                  </p>
                </div>
                <div className="rounded-2xl bg-slate-900 px-4 py-3 text-right text-white">
                  <p className="text-xs uppercase tracking-wide text-slate-300">Mejor match</p>
                  <p className="text-3xl font-semibold text-emerald-300">
                    {matches.matches[0]?.match_score.toFixed(1) || 0}%
                  </p>
                </div>
              </div>

              <div className="mt-6 grid gap-3 sm:grid-cols-3">
                <div className="rounded-2xl bg-slate-50 px-4 py-3">
                  <p className="text-xs uppercase tracking-wide text-slate-500">Vacantes</p>
                  <p className="mt-1 text-xl font-semibold text-slate-900">{matches.total_matches}</p>
                </div>
                <div className="rounded-2xl bg-slate-50 px-4 py-3">
                  <p className="text-xs uppercase tracking-wide text-slate-500">Selector</p>
                  <p className="mt-1 text-xl font-semibold text-slate-900">Activo</p>
                </div>
                <div className="rounded-2xl bg-slate-50 px-4 py-3">
                  <p className="text-xs uppercase tracking-wide text-slate-500">Modo</p>
                  <p className="mt-1 text-xl font-semibold text-slate-900">Semántico</p>
                </div>
              </div>
            </div>

            <div className="rounded-2xl border border-slate-200 bg-gradient-to-br from-emerald-50 via-white to-slate-50 p-6 shadow-sm">
              <p className="text-xs font-semibold uppercase tracking-[0.24em] text-emerald-700">Lectura rápida</p>
              <p className="mt-3 text-sm leading-6 text-slate-700">
                La búsqueda combina tu perfil con descripciones de vacantes y ordena por afinidad. El bloque semántico usa embeddings cuando están disponibles.
              </p>
            </div>
          </section>

          {matches.matches.length > 0 && (
            <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
              {matches.matches.map((match) => (
                <MatchCard
                  key={match.vacancy_id}
                  match={match}
                  onApply={handleApply}
                  badgeClass={getScoreBadgeClass(match.match_score)}
                />
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default function DashboardPage() {
  return (
    <Suspense fallback={<div className="rounded-2xl border border-slate-200 bg-white p-8 text-center text-slate-600">Cargando dashboard...</div>}>
      <DashboardContent />
    </Suspense>
  );
}
