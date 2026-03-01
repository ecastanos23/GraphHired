'use client';

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

interface MatchCardProps {
  match: Match;
  onApply: (vacancyId: number) => void;
  badgeClass: string;
}

export default function MatchCard({ match, onApply, badgeClass }: MatchCardProps) {
  const modalityLabels: Record<string, string> = {
    remote: '🏠 Remoto',
    hybrid: '🔄 Híbrido',
    onsite: '🏢 Presencial',
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">{match.title}</h3>
          <p className="text-gray-600">{match.company}</p>
        </div>
        <span className={`px-3 py-1 rounded-full text-sm font-semibold ${badgeClass}`}>
          {match.match_score.toFixed(1)}%
        </span>
      </div>

      <div className="space-y-2 text-sm text-gray-600 mb-4">
        <p>💰 {match.salary_range}</p>
        {match.work_modality && (
          <p>{modalityLabels[match.work_modality] || match.work_modality}</p>
        )}
        {match.location && <p>📍 {match.location}</p>}
      </div>

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
                  ✓ {skill}
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

      <button
        onClick={() => onApply(match.vacancy_id)}
        className="w-full btn-primary"
      >
        Postularme
      </button>
    </div>
  );
}
