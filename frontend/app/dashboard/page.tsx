/*
 * COMENTARIO DE ARCHIVO - GRAPHHIRED
 * Dashboard principal. Partes: seleccion de candidato, carga de matches, postulaciones, citas, Google Calendar y timeline de agentes.
 */
'use client';

import { Suspense, useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import { useApi } from '@/hooks/useApi';
import MatchCard from '@/components/MatchCard';
import NotificationToast from '@/components/NotificationToast';
import { HoverButton } from '@/components/ui/hover-glow-button';

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
  score_breakdown?: Record<string, number>;
  match_explanation?: string;
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
  expected_salary?: string | null;
  work_modality?: string | null;
  location?: string | null;
  skills?: string[];
  experience_years?: number;
}

interface Application {
  id: number;
  candidate_id: number;
  vacancy_id: number;
  match_score: string | number | null;
  status: string;
  evidence?: Record<string, any> | null;
  next_steps: string[];
  agent_reason?: string | null;
  applied_at: string;
  vacancy_title?: string | null;
  company?: string | null;
  appointments?: Appointment[];
}

interface Appointment {
  id: number;
  application_id: number;
  title: string;
  description?: string | null;
  location?: string | null;
  start_at: string;
  end_at: string;
  google_calendar_url: string;
}

interface AgentEvent {
  id: number;
  agent_name: string;
  action: string;
  reason: string;
  input_summary?: string | null;
  output_summary?: string | null;
  created_at: string;
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
  const [applications, setApplications] = useState<Application[]>([]);
  const [trace, setTrace] = useState<AgentEvent[]>([]);
  const [notification, setNotification] = useState<{show: boolean; message: string; type: 'success' | 'error'}>({
    show: false,
    message: '',
    type: 'success',
  });

  useEffect(() => {
    const fetchInitialData = async () => {
      try {
        const token = localStorage.getItem('graphhired_token');
        if (token && !candidateIdParam) {
          const me = await get<{ candidate_id: number | null }>('/api/auth/me');
          if (me?.candidate_id) {
            setSelectedCandidate(me.candidate_id);
          }
        }
      } catch (err) {
        console.error('Error fetching current user:', err);
      }

      try {
        const data = await get<Candidate[]>('/api/candidates');
        setCandidates(data || []);
      } catch (err) {
        console.error('Error fetching candidates:', err);
      }
    };
    void fetchInitialData();
  }, []);

  useEffect(() => {
    if (selectedCandidate) {
      void fetchMatches(selectedCandidate);
      void fetchProcess(selectedCandidate);
    }
  }, [selectedCandidate]);

  const fetchMatches = async (candidateId: number) => {
    try {
      // Cargar matches/recomendaciones de vacantes para el candidato
      console.log(`🔄 Cargando matches para candidato ${candidateId}`);
      const data = await get<MatchingResponse>(`/api/matching/candidate/${candidateId}?min_score=0&limit=20`);
      setMatches(data);
      console.log(`✅ Matches cargados:`, data?.matches?.length || 0);
    } catch (err) {
      console.error('❌ Error al cargar matches:', err);
      // Mostrar notificación al usuario con el error específico
      setNotification({
        show: true,
        message: `Error cargando ofertas: ${err instanceof Error ? err.message : String(err)}`,
        type: 'error',
      });
    }
  };

  const fetchProcess = async (candidateId: number) => {
    try {
      // Paso 1: Cargar aplicaciones del candidato
      console.log(`🔄 Cargando aplicaciones para candidato ${candidateId}`);
      const apps = await get<Application[]>(`/api/matching/applications/candidate/${candidateId}`);
      
      // Paso 2: Para cada aplicación, cargar sus citas
      const withAppointments = await Promise.all(
        (apps || []).map(async (application) => {
          try {
            console.log(`  📅 Cargando citas para aplicación ${application.id}`);
            const appointments = await get<Appointment[]>(`/api/applications/${application.id}/appointments`);
            return { ...application, appointments: appointments || [] };
          } catch (err) {
            // Las citas son opcionales - si fallan, continuamos sin ellas
            console.warn(`  ⚠️ No se pudieron cargar citas para aplicación ${application.id}:`, err);
            return { ...application, appointments: [] };
          }
        })
      );
      setApplications(withAppointments);
      console.log(`✅ Aplicaciones cargadas:`, withAppointments.length);
    } catch (err) {
      console.error('❌ Error al cargar aplicaciones:', err);
      // Mostrar error al usuario
      setNotification({
        show: true,
        message: `Error cargando aplicaciones: ${err instanceof Error ? err.message : String(err)}`,
        type: 'error',
      });
    }

    try {
      // Paso 3: Cargar el historial de eventos de los agentes IA
      console.log(`🔄 Cargando trace de agentes para candidato ${candidateId}`);
      const events = await get<AgentEvent[]>(`/api/agents/trace?candidate_id=${candidateId}&limit=50`);
      setTrace(events || []);
      console.log(`✅ Trace de agentes cargado:`, events?.length || 0);
    } catch (err) {
      // El trace es informativo solamente - no es crítico si falla
      console.warn('⚠️ No se pudo cargar el trace de agentes (optional):', err);
    }
  };

  const handleApply = async (vacancyId: number) => {
    if (!selectedCandidate) return;

    try {
      await post<Application>('/api/matching/apply', {
        candidate_id: selectedCandidate,
        vacancy_id: vacancyId,
      });
      setNotification({
        show: true,
        message: 'Postulacion simulada guardada con evidencia y proximos pasos.',
        type: 'success',
      });
      await fetchMatches(selectedCandidate);
      await fetchProcess(selectedCandidate);
    } catch (err: any) {
      setNotification({
        show: true,
        message: err.message || 'Error al postularse',
        type: 'error',
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
        onClose={() => setNotification((prev) => ({ ...prev, show: false }))}
      />

      <section className="overflow-hidden rounded-[2rem] border border-slate-200 bg-white shadow-[0_18px_60px_rgba(15,23,42,0.08)]">
        <div className="bg-[linear-gradient(135deg,_#0f172a_0%,_#111827_50%,_#064e3b_100%)] px-6 py-8 text-white sm:px-8">
          <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
            <div className="max-w-2xl space-y-4">
              <p className="text-xs font-semibold uppercase tracking-[0.28em] text-emerald-100">Profile Manager</p>
              <h1 className="text-3xl font-semibold tracking-tight sm:text-4xl">
                Recomendaciones, postulaciones y seguimiento
              </h1>
              <p className="text-sm leading-6 text-slate-200 sm:text-base">
                Cada recomendación muestra por qué la IA eligió esa empresa y cada acción queda trazada por agentes.
              </p>
            </div>

            <div className="w-full max-w-md rounded-3xl border border-white/15 bg-white/10 p-4 backdrop-blur-sm">
              <label className="mb-2 block text-sm font-medium text-slate-100">Candidato</label>
              <select
                value={selectedCandidate || ''}
                onChange={(event) => setSelectedCandidate(event.target.value ? parseInt(event.target.value) : null)}
                className="w-full rounded-2xl border border-white/20 bg-white/95 px-4 py-3 text-sm text-slate-900 shadow-sm outline-none transition focus:border-emerald-400 focus:ring-2 focus:ring-emerald-200"
              >
                <option value="">Seleccionar candidato...</option>
                {candidates.map((candidate) => (
                  <option key={candidate.id} value={candidate.id}>
                    {candidate.full_name} ({candidate.email})
                  </option>
                ))}
              </select>
              {selectedCandidateData && (
                <div className="mt-3 flex flex-wrap gap-2 text-xs text-slate-100/90">
                  {selectedCandidateData.work_modality && <span className="rounded-full bg-white/10 px-3 py-1">{selectedCandidateData.work_modality}</span>}
                  {selectedCandidateData.location && <span className="rounded-full bg-white/10 px-3 py-1">{selectedCandidateData.location}</span>}
                  <span className="rounded-full bg-white/10 px-3 py-1">{selectedCandidateData.experience_years || 0} anos exp.</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </section>

      {!selectedCandidate && (
        <div className="rounded-2xl border border-amber-200 bg-amber-50 p-6 text-center">
          <p className="text-amber-900">
            Selecciona un candidato o{' '}
            <a href="/register" className="font-semibold text-emerald-700 underline decoration-emerald-300 underline-offset-4">
              registrate con tu CV
            </a>
            .
          </p>
        </div>
      )}

      {selectedCandidate && loading && (
        <div className="rounded-2xl border border-slate-200 bg-white p-12 text-center shadow-sm">
          <div className="mx-auto h-12 w-12 animate-spin rounded-full border-b-2 border-emerald-600"></div>
          <p className="mt-4 text-slate-600">Procesando agentes...</p>
        </div>
      )}

      {selectedCandidate && matches && (
        <div className="space-y-8">
          <section className="grid gap-4 lg:grid-cols-4">
            <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
              <p className="text-xs uppercase tracking-wide text-slate-500">Vacantes</p>
              <p className="mt-1 text-3xl font-semibold text-slate-900">{matches.total_matches}</p>
            </div>
            <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
              <p className="text-xs uppercase tracking-wide text-slate-500">Mejor match</p>
              <p className="mt-1 text-3xl font-semibold text-emerald-700">{matches.matches[0]?.match_score.toFixed(1) || 0}%</p>
            </div>
            <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
              <p className="text-xs uppercase tracking-wide text-slate-500">Postulaciones</p>
              <p className="mt-1 text-3xl font-semibold text-slate-900">{applications.length}</p>
            </div>
            <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
              <p className="text-xs uppercase tracking-wide text-slate-500">Eventos agente</p>
              <p className="mt-1 text-3xl font-semibold text-slate-900">{trace.length}</p>
            </div>
          </section>

          <section className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
            <div className="flex items-center justify-center rounded-3xl border border-slate-200 bg-slate-50 p-12 shadow-sm">
              <div className="text-center">
                <p className="text-sm text-slate-600">Gestiona tus postulaciones en la seccion dedicada</p>
                <a
                  href="/applications"
                  className="mt-4 inline-block rounded-2xl bg-emerald-600 px-6 py-3 text-sm font-semibold text-white transition hover:bg-emerald-700"
                >
                  Ir a Postulaciones
                </a>
              </div>
            </div>
          </section>

          {matches.matches.length > 0 && (
            <section className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
              {matches.matches.map((match) => (
                <MatchCard
                  key={match.vacancy_id}
                  match={match}
                  onApply={handleApply}
                  badgeClass={getScoreBadgeClass(match.match_score)}
                />
              ))}
            </section>
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
