/*
 * COMENTARIO DE ARCHIVO - GRAPHHIRED
 * Pagina de carga manual de CV. Partes: formulario de perfil, validaciones, envio al backend y navegacion hacia resultados.
 */
'use client';

import { useState } from 'react';
import { useApi } from '@/hooks/useApi';
import { HoverButton } from '@/components/ui/hover-glow-button';

interface FormData {
  email: string;
  full_name: string;
  cv_text: string;
  expected_salary: string;
  work_modality: string;
  location: string;
}

interface FormErrors {
  [key: string]: boolean;
}

interface CandidateResponse {
  id: number;
  email: string;
  full_name: string;
}

const benefitItems = [
  {
    title: 'Parsing con LangGraph',
    description: 'Estructura tu CV y extrae señales útiles para el matching semántico.',
  },
  {
    title: 'Embeddings con Gemini',
    description: 'Convierte tu perfil en vectores para encontrar vacantes más precisas.',
  },
  {
    title: 'Dashboard listo',
    description: 'Después de subir tu perfil, explora resultados en una interfaz clara y responsive.',
  },
];

const modalityOptions = [
  { value: 'remote', label: 'Remoto' },
  { value: 'hybrid', label: 'Híbrido' },
  { value: 'onsite', label: 'Presencial' },
];

export default function UploadPage() {
  const { post, loading, error } = useApi();
  const [formData, setFormData] = useState<FormData>({
    email: '',
    full_name: '',
    cv_text: '',
    expected_salary: '',
    work_modality: '',
    location: ''
  });
  const [formErrors, setFormErrors] = useState<FormErrors>({});
  const [success, setSuccess] = useState(false);
  const [candidateId, setCandidateId] = useState<number | null>(null);

  const fieldClassName = (hasError?: boolean): string => {
    return [
      'mt-1 block w-full rounded-2xl border bg-white px-4 py-3 text-sm text-slate-900 outline-none transition-all duration-300 placeholder:text-slate-400 focus:ring-4 focus:ring-emerald-200/60',
      hasError
        ? 'border-rose-300 ring-1 ring-rose-200 focus:border-rose-400'
        : 'border-slate-200 focus:border-emerald-400',
    ].join(' ');
  };

  const validateForm = (): boolean => {
    const errors: FormErrors = {};
    
    if (!formData.email) errors.email = true;
    if (!formData.full_name || formData.full_name.length < 2) errors.full_name = true;
    if (!formData.cv_text || formData.cv_text.length < 10) errors.cv_text = true;
    if (!formData.expected_salary || parseFloat(formData.expected_salary) < 0) errors.expected_salary = true;
    if (!formData.work_modality) errors.work_modality = true;
    if (!formData.location) errors.location = true;
    
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSuccess(false);
    
    if (!validateForm()) {
      return;
    }

    try {
      const response = await post<CandidateResponse>('/api/candidates/upload-cv', {
        ...formData,
        expected_salary: parseFloat(formData.expected_salary)
      });
      
      if (response) {
        setSuccess(true);
        setCandidateId(response.id);
      }
    } catch (err) {
      console.error('Error uploading CV:', err);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    // Clear error when user starts typing
    if (formErrors[name]) {
      setFormErrors(prev => ({ ...prev, [name]: false }));
    }
  };

  return (
    <div className="space-y-8">
      <section className="overflow-hidden rounded-[2rem] border border-slate-200 bg-white shadow-[0_18px_60px_rgba(15,23,42,0.08)]">
        <div className="bg-[radial-gradient(circle_at_top_left,_rgba(16,185,129,0.18),_transparent_30%),radial-gradient(circle_at_top_right,_rgba(15,23,42,0.10),_transparent_24%),linear-gradient(135deg,_#0f172a_0%,_#111827_50%,_#064e3b_100%)] px-6 py-8 text-white sm:px-8 lg:px-10">
          <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
            <div className="max-w-2xl space-y-4">
              <div className="inline-flex items-center rounded-full border border-white/15 bg-white/10 px-3 py-1 text-xs font-semibold uppercase tracking-[0.28em] text-emerald-100">
                Onboarding IA
              </div>
              <div className="space-y-2">
                <h1 className="text-3xl font-semibold tracking-tight sm:text-4xl lg:text-5xl">
                  Sube tu CV y activa el buscador semántico
                </h1>
                <p className="max-w-2xl text-sm leading-6 text-slate-200 sm:text-base">
                  GraphHired convierte tu perfil en un flujo de análisis con LangGraph, embeddings y dashboards claros para encontrar mejores vacantes.
                </p>
              </div>
            </div>

            <div className="grid gap-3 sm:grid-cols-3 lg:max-w-xl lg:grid-cols-1 xl:grid-cols-3">
              {benefitItems.map((item, index) => (
                <div key={item.title} className="rounded-2xl border border-white/15 bg-white/10 p-4 backdrop-blur-sm transition-all duration-300 hover:bg-white/15 hover:-translate-y-0.5">
                  <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-emerald-400/20 text-sm font-semibold text-emerald-100 ring-1 ring-inset ring-emerald-300/30">
                      0{index + 1}
                    </div>
                    <div>
                      <p className="text-sm font-semibold text-white">{item.title}</p>
                      <p className="text-xs leading-5 text-slate-200">{item.description}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
        <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.24em] text-emerald-700">Perfil del candidato</p>
              <h2 className="mt-2 text-2xl font-semibold text-slate-900">Completa los datos para generar matches</h2>
              <p className="mt-2 text-sm leading-6 text-slate-600">
                Los campos obligatorios ayudan a construir un perfil consistente antes de enviarlo al pipeline de análisis.
              </p>
            </div>
          </div>

          {success && (
            <div className="mt-6 rounded-2xl border border-emerald-200 bg-emerald-50 p-4">
              <p className="font-medium text-emerald-800">CV registrado exitosamente</p>
              <p className="mt-1 text-sm text-emerald-700">
                Tu perfil fue analizado.{' '}
                <a href={`/dashboard?candidateId=${candidateId}`} className="font-semibold underline decoration-emerald-300 underline-offset-4 transition-colors hover:text-emerald-900">
                  Ver vacantes recomendadas
                </a>
              </p>
            </div>
          )}

          {error && (
            <div className="mt-6 rounded-2xl border border-rose-200 bg-rose-50 p-4">
              <p className="text-rose-800">Error: {error}</p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="mt-6 space-y-5">
            <div className="grid gap-5 md:grid-cols-2">
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-slate-700">
                  Email <span className="text-rose-500">*</span>
                </label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  className={fieldClassName(formErrors.email)}
                  placeholder="tu@email.com"
                />
                {formErrors.email && <p className="mt-1 text-sm text-rose-600">Email es requerido</p>}
              </div>

              <div>
                <label htmlFor="full_name" className="block text-sm font-medium text-slate-700">
                  Nombre completo <span className="text-rose-500">*</span>
                </label>
                <input
                  type="text"
                  id="full_name"
                  name="full_name"
                  value={formData.full_name}
                  onChange={handleChange}
                  className={fieldClassName(formErrors.full_name)}
                  placeholder="Juan Pérez"
                />
                {formErrors.full_name && <p className="mt-1 text-sm text-rose-600">Nombre completo es requerido</p>}
              </div>
            </div>

            <div>
              <label htmlFor="cv_text" className="block text-sm font-medium text-slate-700">
                Contenido del CV <span className="text-rose-500">*</span>
              </label>
              <textarea
                id="cv_text"
                name="cv_text"
                rows={10}
                value={formData.cv_text}
                onChange={handleChange}
                className={`${fieldClassName(formErrors.cv_text)} resize-none`}
                placeholder="Pega aquí el contenido de tu CV o escribe un resumen de tu experiencia, habilidades y formación..."
              />
              {formErrors.cv_text && <p className="mt-1 text-sm text-rose-600">CV es requerido (mínimo 10 caracteres)</p>}
            </div>

            <div className="grid gap-5 md:grid-cols-2">
              <div>
                <label htmlFor="expected_salary" className="block text-sm font-medium text-slate-700">
                  Salario esperado (USD anual) <span className="text-rose-500">*</span>
                </label>
                <input
                  type="number"
                  id="expected_salary"
                  name="expected_salary"
                  value={formData.expected_salary}
                  onChange={handleChange}
                  className={fieldClassName(formErrors.expected_salary)}
                  placeholder="60000"
                  min="0"
                />
                {formErrors.expected_salary && <p className="mt-1 text-sm text-rose-600">Salario esperado es requerido</p>}
              </div>

              <div>
                <label htmlFor="work_modality" className="block text-sm font-medium text-slate-700">
                  Modalidad de trabajo <span className="text-rose-500">*</span>
                </label>
                <select
                  id="work_modality"
                  name="work_modality"
                  value={formData.work_modality}
                  onChange={handleChange}
                  className={fieldClassName(formErrors.work_modality)}
                >
                  <option value="">Seleccionar...</option>
                  {modalityOptions.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
                {formErrors.work_modality && <p className="mt-1 text-sm text-rose-600">Modalidad es requerida</p>}
              </div>
            </div>

            <div>
              <label htmlFor="location" className="block text-sm font-medium text-slate-700">
                Ubicación <span className="text-rose-500">*</span>
              </label>
              <input
                type="text"
                id="location"
                name="location"
                value={formData.location}
                onChange={handleChange}
                className={fieldClassName(formErrors.location)}
                placeholder="Bogotá, Colombia"
              />
              {formErrors.location && <p className="mt-1 text-sm text-rose-600">Ubicación es requerida</p>}
            </div>

            <div className="pt-2">
              <HoverButton
                type="submit"
                disabled={loading}
                className="w-full rounded-2xl py-4 text-base font-semibold shadow-lg shadow-emerald-500/20"
                glowColor="#34d399"
                backgroundColor="#10b981"
                textColor="#ffffff"
                hoverTextColor="#d1fae5"
              >
                {loading ? 'Procesando...' : 'Subir CV y Analizar'}
              </HoverButton>
            </div>
          </form>
        </div>

        <aside className="space-y-6">
          <div className="rounded-3xl border border-slate-200 bg-[radial-gradient(circle_at_top,_rgba(16,185,129,0.12),_transparent_35%),linear-gradient(180deg,_#ffffff_0%,_#f8fafc_100%)] p-6 shadow-sm">
            <p className="text-xs font-semibold uppercase tracking-[0.24em] text-emerald-700">Antes de subir</p>
            <h3 className="mt-2 text-xl font-semibold text-slate-900">Recomendaciones rápidas</h3>
            <ul className="mt-4 space-y-3 text-sm leading-6 text-slate-600">
              <li className="rounded-2xl border border-slate-200 bg-white p-4 transition-all duration-300 hover:border-emerald-200 hover:shadow-md">
                Usa un texto claro con roles, tecnologías y años de experiencia.
              </li>
              <li className="rounded-2xl border border-slate-200 bg-white p-4 transition-all duration-300 hover:border-emerald-200 hover:shadow-md">
                Indica modalidad y ubicación reales para mejorar la calidad del match.
              </li>
              <li className="rounded-2xl border border-slate-200 bg-white p-4 transition-all duration-300 hover:border-emerald-200 hover:shadow-md">
                Después podrás ver el resultado en el Dashboard con el motor usado.
              </li>
            </ul>
          </div>
        </aside>
      </section>
    </div>
  );
}
