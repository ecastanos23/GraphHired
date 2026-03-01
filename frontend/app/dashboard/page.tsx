'use client';

import { useState, useEffect } from 'react';
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
}

export default function DashboardPage() {
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
        const data = await get('/api/candidates');
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
      const data = await get(`/api/matching/candidate/${candidateId}?min_score=0&limit=20`);
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

  return (
    <div className="space-y-6">
      <NotificationToast 
        show={notification.show}
        message={notification.message}
        type={notification.type}
        onClose={() => setNotification(prev => ({ ...prev, show: false }))}
      />

      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Dashboard de Vacantes</h1>
        
        {/* Candidate selector */}
        <div className="flex items-center gap-3">
          <label className="text-sm font-medium text-gray-700">Candidato:</label>
          <select
            value={selectedCandidate || ''}
            onChange={(e) => setSelectedCandidate(e.target.value ? parseInt(e.target.value) : null)}
            className="border border-gray-300 rounded-md px-3 py-2 text-sm"
          >
            <option value="">Seleccionar candidato...</option>
            {candidates.map((c) => (
              <option key={c.id} value={c.id}>
                {c.full_name} ({c.email})
              </option>
            ))}
          </select>
        </div>
      </div>

      {!selectedCandidate && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
          <p className="text-yellow-800">
            Selecciona un candidato para ver las vacantes recomendadas, o{' '}
            <a href="/upload" className="text-primary-600 underline">sube tu CV</a> primero.
          </p>
        </div>
      )}

      {selectedCandidate && loading && (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Calculando matches...</p>
        </div>
      )}

      {selectedCandidate && matches && !loading && (
        <>
          {/* Summary */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex justify-between items-center">
              <div>
                <h2 className="text-lg font-semibold">{matches.candidate_name}</h2>
                <p className="text-gray-600">
                  {matches.total_matches} vacantes encontradas
                </p>
              </div>
              <div className="text-right">
                <p className="text-sm text-gray-500">Mejor match</p>
                <p className="text-2xl font-bold text-primary-600">
                  {matches.matches[0]?.match_score.toFixed(1) || 0}%
                </p>
              </div>
            </div>
          </div>

          {/* Matches Grid */}
          {matches.matches.length > 0 ? (
            <div className="grid md:grid-cols-2 gap-6">
              {matches.matches.map((match) => (
                <MatchCard
                  key={match.vacancy_id}
                  match={match}
                  onApply={handleApply}
                  badgeClass={getScoreBadgeClass(match.match_score)}
                />
              ))}
            </div>
          ) : (
            <div className="bg-gray-50 rounded-lg p-8 text-center">
              <p className="text-gray-600">No se encontraron vacantes que coincidan con tu perfil.</p>
            </div>
          )}
        </>
      )}
    </div>
  );
}
