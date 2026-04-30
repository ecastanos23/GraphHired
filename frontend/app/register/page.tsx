'use client';

import { useState } from 'react';
import { useApi } from '@/hooks/useApi';
import { HoverButton } from '@/components/ui/hover-glow-button';

interface ParsedCV {
  full_name?: string | null;
  email?: string | null;
  phone?: string | null;
  skills: string[];
  experience_years: number;
  education?: string | null;
  summary: string;
  profile_gaps: string[];
  recommended_roles: string[];
  cv_text: string;
  extracted_text_length: number;
}

interface AuthResponse {
  access_token: string;
  user: {
    candidate_id: number | null;
  };
}

const modalityOptions = [
  { value: 'remote', label: 'Remoto' },
  { value: 'hybrid', label: 'Hibrido' },
  { value: 'onsite', label: 'Presencial' },
];

export default function RegisterPage() {
  const { post, postForm, loading, error } = useApi();
  const [pdfFile, setPdfFile] = useState<File | null>(null);
  const [parsed, setParsed] = useState<ParsedCV | null>(null);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    full_name: '',
    phone: '',
    expected_salary: '',
    work_modality: 'remote',
    location: 'Bogota',
    cv_text: '',
  });

  const fieldClass =
    'mt-1 block w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-emerald-400 focus:ring-4 focus:ring-emerald-200/60';

  const handleParsePdf = async () => {
    if (!pdfFile) return;
    const payload = new FormData();
    payload.append('file', pdfFile);
    try {
      const response = await postForm<ParsedCV>('/api/candidates/parse-cv-pdf', payload);
      if (!response) return;

      setParsed(response);
      setFormData((prev) => ({
        ...prev,
        email: response.email || prev.email,
        full_name: response.full_name || prev.full_name,
        phone: response.phone || prev.phone,
        cv_text: response.cv_text || prev.cv_text,
      }));
    } catch (err) {
      console.error('Error parsing CV PDF:', err);
    }
  };

  const handleRegister = async (event: React.FormEvent) => {
    event.preventDefault();
    try {
      const response = await post<AuthResponse>('/api/auth/register', {
        ...formData,
        expected_salary: formData.expected_salary ? Number(formData.expected_salary) : null,
      });
      if (!response) return;

      localStorage.setItem('graphhired_token', response.access_token);
      const candidateId = response.user.candidate_id;
      window.location.href = candidateId ? `/dashboard?candidateId=${candidateId}` : '/dashboard';
    } catch (err) {
      console.error('Error registering candidate:', err);
    }
  };

  return (
    <div className="space-y-8">
      <section className="overflow-hidden rounded-[2rem] border border-slate-200 bg-white shadow-[0_18px_60px_rgba(15,23,42,0.08)]">
        <div className="bg-[linear-gradient(135deg,_#0f172a_0%,_#111827_52%,_#065f46_100%)] px-6 py-9 text-white sm:px-8">
          <p className="text-xs font-semibold uppercase tracking-[0.28em] text-emerald-100">Registro con IA</p>
          <h1 className="mt-3 text-3xl font-semibold tracking-tight sm:text-4xl">Crea tu cuenta desde el CV</h1>
          <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-200">
            Sube un PDF, Gemini extrae los datos principales y tu puedes corregirlos antes de crear el perfil.
          </p>
        </div>
      </section>

      <section className="grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
        <aside className="space-y-6">
          <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
            <p className="text-xs font-semibold uppercase tracking-[0.24em] text-emerald-700">Paso 1</p>
            <h2 className="mt-2 text-xl font-semibold text-slate-900">Analizar PDF</h2>
            <input
              type="file"
              accept="application/pdf"
              onChange={(event) => setPdfFile(event.target.files?.[0] || null)}
              className="mt-5 block w-full rounded-2xl border border-dashed border-slate-300 bg-slate-50 px-4 py-5 text-sm text-slate-700"
            />
            <HoverButton
              onClick={handleParsePdf}
              disabled={!pdfFile || loading}
              className="mt-4 w-full rounded-2xl py-3 text-sm font-semibold"
              glowColor="#34d399"
              backgroundColor="#10b981"
              textColor="#ffffff"
              hoverTextColor="#d1fae5"
            >
              {loading ? 'Analizando...' : 'Analizar'}
            </HoverButton>
          </div>

          {parsed && (
            <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
              <p className="text-xs font-semibold uppercase tracking-[0.24em] text-emerald-700">Resultado IA</p>
              <p className="mt-3 text-sm leading-6 text-slate-700">{parsed.summary || 'Perfil extraido.'}</p>
              <div className="mt-4 flex flex-wrap gap-2">
                {parsed.skills.slice(0, 10).map((skill) => (
                  <span key={skill} className="rounded-full bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-700">
                    {skill}
                  </span>
                ))}
              </div>
              {parsed.profile_gaps.length > 0 && (
                <div className="mt-5 rounded-2xl border border-amber-200 bg-amber-50 p-4">
                  <p className="text-sm font-semibold text-amber-900">Vacios detectados</p>
                  <ul className="mt-2 space-y-1 text-sm text-amber-800">
                    {parsed.profile_gaps.map((gap) => (
                      <li key={gap}>{gap}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </aside>

        <form onSubmit={handleRegister} className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
          <p className="text-xs font-semibold uppercase tracking-[0.24em] text-emerald-700">Paso 2</p>
          <h2 className="mt-2 text-2xl font-semibold text-slate-900">Confirma tus datos</h2>
          {error && <div className="mt-4 rounded-2xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700">{error}</div>}

          <div className="mt-6 grid gap-5 md:grid-cols-2">
            <label className="block text-sm font-medium text-slate-700">
              Email
              <input required type="email" value={formData.email} onChange={(e) => setFormData({ ...formData, email: e.target.value })} className={fieldClass} />
            </label>
            <label className="block text-sm font-medium text-slate-700">
              Contrasena
              <input required minLength={6} type="password" value={formData.password} onChange={(e) => setFormData({ ...formData, password: e.target.value })} className={fieldClass} />
            </label>
            <label className="block text-sm font-medium text-slate-700">
              Nombre completo
              <input required value={formData.full_name} onChange={(e) => setFormData({ ...formData, full_name: e.target.value })} className={fieldClass} />
            </label>
            <label className="block text-sm font-medium text-slate-700">
              Telefono
              <input value={formData.phone} onChange={(e) => setFormData({ ...formData, phone: e.target.value })} className={fieldClass} />
            </label>
            <label className="block text-sm font-medium text-slate-700">
              Salario esperado
              <input type="number" min="0" value={formData.expected_salary} onChange={(e) => setFormData({ ...formData, expected_salary: e.target.value })} className={fieldClass} />
            </label>
            <label className="block text-sm font-medium text-slate-700">
              Modalidad
              <select value={formData.work_modality} onChange={(e) => setFormData({ ...formData, work_modality: e.target.value })} className={fieldClass}>
                {modalityOptions.map((option) => (
                  <option key={option.value} value={option.value}>{option.label}</option>
                ))}
              </select>
            </label>
          </div>

          <label className="mt-5 block text-sm font-medium text-slate-700">
            Ubicacion
            <input required value={formData.location} onChange={(e) => setFormData({ ...formData, location: e.target.value })} className={fieldClass} />
          </label>

          <label className="mt-5 block text-sm font-medium text-slate-700">
            Texto extraido del CV
            <textarea required rows={8} value={formData.cv_text} onChange={(e) => setFormData({ ...formData, cv_text: e.target.value })} className={`${fieldClass} resize-none`} />
          </label>

          <HoverButton
            type="submit"
            disabled={loading}
            className="mt-6 w-full rounded-2xl py-4 text-base font-semibold"
            glowColor="#38bdf8"
            backgroundColor="#061638"
            textColor="#ffffff"
            hoverTextColor="#bfdbfe"
          >
            {loading ? 'Creando cuenta...' : 'Crear cuenta y ver matches'}
          </HoverButton>
        </form>
      </section>
    </div>
  );
}
