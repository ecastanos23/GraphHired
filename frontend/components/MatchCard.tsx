'use client';

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

interface MatchCardProps {
  match: Match;
  onApply: (vacancyId: number) => void;
  badgeClass: string;
}

export default function MatchCard({ match, onApply, badgeClass }: MatchCardProps) {
  const modalityLabels: Record<string, string> = {
    remote: 'Remoto',
    hybrid: 'Hibrido',
    onsite: 'Presencial',
  };

  return (
    <div className="group rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition hover:-translate-y-0.5 hover:shadow-xl" id={`vacancy-card-${match.vacancy_id}`}>
      <div className="mb-4 flex items-start justify-between gap-3">
        <div>
          <h3 className="text-lg font-semibold text-slate-900 group-hover:text-emerald-700">{match.title}</h3>
          <p className="mt-1 text-sm text-slate-600">{match.company}</p>
        </div>
        <span className={`rounded-full px-3 py-1 text-sm font-semibold ${badgeClass}`}>
          {match.match_score.toFixed(1)}%
        </span>
      </div>

      <div className="mb-4 space-y-2 text-sm text-slate-600">
        <p>Salario: {match.salary_range}</p>
        {match.work_modality && (
          <p>{modalityLabels[match.work_modality] || match.work_modality}</p>
        )}
        {match.location && <p>Ubicacion: {match.location}</p>}
      </div>

      {match.match_explanation && (
        <div className="mb-4 rounded-2xl border border-emerald-100 bg-emerald-50 p-4 text-sm leading-6 text-emerald-900">
          <p className="font-semibold">Por que la IA eligio esta empresa</p>
          <p className="mt-1">{match.match_explanation}</p>
        </div>
      )}

      {match.score_breakdown && (
        <div className="mb-4 grid grid-cols-2 gap-2 text-xs">
          {Object.entries(match.score_breakdown).map(([key, value]) => (
            <div key={key} className="rounded-xl bg-slate-50 px-3 py-2">
              <p className="capitalize text-slate-500">{key}</p>
              <p className="text-base font-semibold text-slate-900">{Number(value).toFixed(0)}%</p>
            </div>
          ))}
        </div>
      )}

      {/* Skills */}
      <div className="mb-4">
        {match.matching_skills.length > 0 && (
          <div className="mb-2">
            <span className="text-xs text-gray-500">Skills que tienes:</span>
            <div className="flex flex-wrap gap-1 mt-1">
              {match.matching_skills.map((skill) => (
                <span
                  key={skill}
                  className="bg-green-100 text-green-700 px-2 py-0.5 rounded text-xs"
                >
                  {skill}
                </span>
              ))}
            </div>
          </div>
        )}
        {match.missing_skills.length > 0 && (
          <div>
            <span className="text-xs text-gray-500">Skills por desarrollar:</span>
            <div className="flex flex-wrap gap-1 mt-1">
              {match.missing_skills.slice(0, 3).map((skill) => (
                <span
                  key={skill}
                  className="bg-gray-100 text-gray-600 px-2 py-0.5 rounded text-xs"
                >
                  {skill}
                </span>
              ))}
              {match.missing_skills.length > 3 && (
                <span className="text-gray-400 text-xs">
                  +{match.missing_skills.length - 3} más
                </span>
              )}
            </div>
          </div>
        )}
      </div>

      <HoverButton
        onClick={() => onApply(match.vacancy_id)}
        className="w-full rounded-xl py-3 text-lg"
        glowColor="#38bdf8"
        backgroundColor="#061638"
        textColor="#ffffff"
        hoverTextColor="#bfdbfe"
      >
        Postularme
      </HoverButton>
    </div>
  );
}
