/*
 * COMENTARIO DE ARCHIVO - GRAPHHIRED
 * Pagina de registro con IA. Partes: estado de PDF/perfil, parseo del CV, formulario editable y envio a /api/auth/register.
 */
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
  contact?: { email?: string | null; phone?: string | null; location?: string | null } | null;
  education?: any;
  experience?: any;
  languages?: any;
  certifications?: string[];
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
    languages: '',
    certifications: '',
    education: '', // Texto de educación (summary)
    experience: '', // Texto de experiencia (summary)
    summary: '', // Resumen profesional
    expected_salary: '',
    work_modality: 'remote',
    location: 'Bogota',
    cv_text: '', // Se mantiene en estado pero no se muestra en formulario
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

      // Parse certifications: if array of objects, extract names; if array of strings, use directly
      let certStr = '';
      if ((response as any).certifications && Array.isArray((response as any).certifications)) {
        certStr = (response as any).certifications
          .map((cert: any) => (typeof cert === 'string' ? cert : cert.name || JSON.stringify(cert)))
          .join(', ');
      }

      // Parse languages: if array of objects with 'language' field, extract language names
      let langStr = '';
      if ((response as any).languages && Array.isArray((response as any).languages)) {
        langStr = (response as any).languages
          .map((lang: any) => (typeof lang === 'string' ? lang : lang.language || ''))
          .filter((l: string) => l)
          .join(', ');
      }

      // Parse education: if array of objects, create summary; if string, use directly
      let educationStr = '';
      if ((response as any).education && Array.isArray((response as any).education)) {
        educationStr = (response as any).education
          .map((edu: any) => {
            if (typeof edu === 'string') return edu;
            const degree = edu.degree || '';
            const institution = edu.institution || '';
            const year = edu.year || '';
            return `${degree} - ${institution} (${year})`.replace(/\s*-\s*\(/g, ' (').trim();
          })
          .filter((e: string) => e)
          .join('\n');
      }

      // Parse experience: if array of objects, create summary; if string, use directly
      let experienceStr = '';
      if ((response as any).experience && Array.isArray((response as any).experience)) {
        experienceStr = (response as any).experience
          .map((exp: any) => {
            if (typeof exp === 'string') return exp;
            const role = exp.role || '';
            const company = exp.company || '';
            const dates = exp.start_date && exp.end_date ? `(${exp.start_date} - ${exp.end_date})` : '';
            return `${role} at ${company} ${dates}`.trim();
          })
          .filter((e: string) => e)
          .join('\n');
      }

      // Extract location from contact or use provided location
      const extractedLocation = response.contact?.location || response.cv_text.split('\n').find((line: string) => line.includes('Colombia'))?.split('-')[0]?.trim() || 'Bogota';

      setParsed(response);
      setFormData((prev) => ({
        ...prev,
        email: response.email || prev.email,
        full_name: response.full_name || prev.full_name,
        phone: response.phone || prev.phone,
        cv_text: response.cv_text || prev.cv_text, // Se mantiene guardado pero oculto
        summary: response.summary || prev.summary, // Mostrar solo el resumen en formulario
        languages: langStr || prev.languages,
        certifications: certStr || prev.certifications,
        education: educationStr || prev.education,
        experience: experienceStr || prev.experience,
        location: extractedLocation || prev.location,
      }));
    } catch (err) {
      console.error('Error parsing CV PDF:', err);
    }
  };

  const handleRegister = async (event: React.FormEvent) => {
    event.preventDefault();
    try {
      const payload = {
        ...formData,
        expected_salary: formData.expected_salary ? Number(formData.expected_salary) : null,
        languages: formData.languages ? formData.languages.split(',').map((s) => ({ language: s.trim() })) : undefined,
        certifications: formData.certifications ? formData.certifications.split(',').map((s) => s.trim()) : undefined,
        // Send education and experience as text summaries (can be parsed by backend if needed)
        education: formData.education ? [{ summary: formData.education }] : undefined,
        experience: formData.experience ? [{ summary: formData.experience }] : undefined,
      };
      const response = await post<AuthResponse>('/api/auth/register', payload);
      if (!response) return;

      localStorage.setItem('graphhired_token', response.access_token);
      const candidateId = response.user.candidate_id;
      window.location.href = candidateId ? `/dashboard?candidateId=${candidateId}` : '/dashboard';
    } catch (err) {
      console.error('Error registering candidate:', err);
    }
  };

    // Texto de trazabilidad / recomendaciones generadas a partir del resultado del agente
    const aiTraceText = parsed
      ? (() => {
          const highlights = parsed.skills && parsed.skills.length ? parsed.skills.slice(0, 4).join(', ') : '—';
          const gaps = parsed.profile_gaps && parsed.profile_gaps.length ? parsed.profile_gaps.join(', ') : 'Ninguno';
          const roles = parsed.recommended_roles && parsed.recommended_roles.length ? parsed.recommended_roles.slice(0, 3).join(', ') : '—';
          return `La IA procesó ${parsed.extracted_text_length.toLocaleString()} caracteres, detectó ${parsed.skills.length} habilidades y ${parsed.experience.length} puestos de experiencia. Destacados: ${highlights}. Recomendación: completar campos faltantes: ${gaps}. Roles sugeridos: ${roles}.`;
        })()
      : '';

  return (
    <div className="space-y-8">
      <section className="overflow-hidden rounded-[2rem] border border-slate-200 bg-white shadow-[0_18px_60px_rgba(15,23,42,0.08)]">
        <div className="bg-[linear-gradient(135deg,_#0f172a_0%,_#111827_52%,_#065f46_100%)] px-6 py-9 text-white sm:px-8">
          <p className="text-xs font-semibold uppercase tracking-[0.28em] text-emerald-100">Registro con IA</p>
          <h1 className="mt-3 text-3xl font-semibold tracking-tight sm:text-4xl">Crea tu cuenta desde el CV</h1>
          <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-200">
            Sube un PDF, OpenAI extrae los datos principales y tu puedes corregirlos antes de crear el perfil.
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
              <p className="mt-3 text-sm leading-6 text-slate-700">{aiTraceText}</p>
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
            Idiomas (separados por coma)
            <input value={formData.languages} onChange={(e) => setFormData({ ...formData, languages: e.target.value })} className={fieldClass} />
          </label>

          <label className="mt-5 block text-sm font-medium text-slate-700">
            Educación
            <textarea rows={3} value={formData.education} onChange={(e) => setFormData({ ...formData, education: e.target.value })} className={`${fieldClass} resize-none`} placeholder="Grado - Institución (Año)" />
          </label>

          <label className="mt-5 block text-sm font-medium text-slate-700">
            Experiencia laboral
            <textarea rows={3} value={formData.experience} onChange={(e) => setFormData({ ...formData, experience: e.target.value })} className={`${fieldClass} resize-none`} placeholder="Cargo en Empresa (Fecha inicio - Fecha fin)" />
          </label>

          <label className="mt-5 block text-sm font-medium text-slate-700">
            Certificaciones (separadas por coma)
            <input value={formData.certifications} onChange={(e) => setFormData({ ...formData, certifications: e.target.value })} className={fieldClass} />
          </label>

          <label className="mt-5 block text-sm font-medium text-slate-700">
            Resumen Profesional (extraído del CV)
            <textarea rows={4} value={formData.summary} onChange={(e) => setFormData({ ...formData, summary: e.target.value })} className={`${fieldClass} resize-none`} placeholder="Resumen de tu perfil profesional..." />
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
