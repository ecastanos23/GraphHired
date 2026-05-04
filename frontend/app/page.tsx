/*
 * COMENTARIO DE ARCHIVO - GRAPHHIRED
 * Pagina Home. Partes: hero/buscador, tarjetas de senales, features, preview de matches y explicacion del flujo.
 */
import { HoverButton } from '@/components/ui/hover-glow-button';

type FeatureCard = {
  title: string;
  description: string;
  icon: 'cv' | 'vector' | 'graph';
};

type PreviewMatch = {
  title: string;
  company: string;
  score: number;
  location: string;
  modality: string;
  tags: string[];
};

const featureCards: FeatureCard[] = [
  {
    title: 'Parsing de CVs con LangGraph',
    description:
      'Extrae habilidades, experiencia y señales de perfil con un flujo modular preparado para crecer.',
    icon: 'cv',
  },
  {
    title: 'Vectores con pgvector',
    description:
      'Clasifica vacantes por similitud semántica para mostrar coincidencias más precisas y explicables.',
    icon: 'vector',
  },
  {
    title: 'Visualización de Grafos',
    description:
      'Representa el proceso de análisis y matching como nodos claros para depuración y demo.',
    icon: 'graph',
  },
];

const previewMatches: PreviewMatch[] = [
  {
    title: 'Senior Frontend Developer',
    company: 'Studio Nexus',
    score: 96.4,
    location: 'Bogotá, Colombia',
    modality: 'Híbrido',
    tags: ['Next.js', 'TypeScript', 'UX'],
  },
  {
    title: 'AI Product Engineer',
    company: 'GraphWorks',
    score: 92.1,
    location: 'Remoto LATAM',
    modality: 'Remoto',
    tags: ['LangGraph', 'Gemini', 'pgvector'],
  },
];

function FeatureIcon({ icon }: { icon: FeatureCard['icon'] }) {
  const iconClass = 'h-6 w-6 text-emerald-700';

  if (icon === 'cv') {
    return (
      <svg className={iconClass} fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
    );
  }

  if (icon === 'vector') {
    return (
      <svg className={iconClass} fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
      </svg>
    );
  }

  return (
    <svg className={iconClass} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
    </svg>
  );
}

export default function Home() {
  return (
    <div className="space-y-8">
      <section className="overflow-hidden rounded-[2rem] border border-slate-200 bg-white shadow-[0_18px_60px_rgba(15,23,42,0.08)]">
        <div className="bg-[radial-gradient(circle_at_top_left,_rgba(16,185,129,0.22),_transparent_28%),radial-gradient(circle_at_top_right,_rgba(15,23,42,0.10),_transparent_24%),linear-gradient(135deg,_#0f172a_0%,_#111827_48%,_#064e3b_100%)] px-6 py-10 text-white sm:px-8 lg:px-12 lg:py-14">
          <div className="mx-auto flex max-w-5xl flex-col items-center gap-8 text-center">
            <div className="inline-flex items-center rounded-full border border-white/15 bg-white/10 px-4 py-1 text-xs font-semibold uppercase tracking-[0.32em] text-emerald-100">
              Buscador de IA
            </div>

            <div className="max-w-3xl space-y-4">
              <h1 className="text-4xl font-semibold tracking-tight sm:text-5xl lg:text-6xl">
                Encuentra el match semántico que mejor encaja con tu perfil
              </h1>
              <p className="mx-auto max-w-2xl text-sm leading-6 text-slate-200 sm:text-base lg:text-lg">
                GraphHired combina análisis de CV, embeddings y grafos para mostrar vacantes relevantes de forma clara, rápida y explicable.
              </p>
            </div>

            <form action="/dashboard" className="w-full max-w-4xl">
              <div className="flex flex-col gap-3 rounded-3xl border border-white/15 bg-white/10 p-3 shadow-[0_18px_50px_rgba(15,23,42,0.18)] backdrop-blur-sm sm:flex-row sm:items-center">
                <div className="flex-1">
                  <label htmlFor="home-search" className="sr-only">
                    Buscar vacantes o habilidades
                  </label>
                  <input
                    id="home-search"
                    name="q"
                    type="text"
                    placeholder="Busca vacantes, tecnologías o perfiles: React, Python, Data, IA..."
                    className="h-14 w-full rounded-2xl border border-white/20 bg-white/95 px-5 text-slate-900 outline-none transition-all duration-300 placeholder:text-slate-400 focus:border-emerald-400 focus:ring-4 focus:ring-emerald-200/60"
                  />
                </div>

                <HoverButton
                  type="submit"
                  className="h-14 rounded-2xl px-6 text-sm font-semibold shadow-lg shadow-emerald-500/20"
                  glowColor="#34d399"
                  backgroundColor="#10b981"
                  textColor="#ffffff"
                  hoverTextColor="#d1fae5"
                >
                  Encontrar Match Semántico
                </HoverButton>
              </div>
            </form>

            <div className="flex flex-wrap justify-center gap-3 text-sm text-slate-200">
              <a
                href="/upload"
                className="rounded-full border border-white/15 bg-white/10 px-4 py-2 transition-all duration-300 hover:bg-white/20 hover:-translate-y-0.5"
              >
                Subir CV
              </a>
              <a
                href="/dashboard"
                className="rounded-full border border-white/15 bg-white/10 px-4 py-2 transition-all duration-300 hover:bg-white/20 hover:-translate-y-0.5"
              >
                Ver vacantes
              </a>
            </div>
          </div>
        </div>
      </section>

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <article className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <p className="text-xs font-semibold uppercase tracking-[0.24em] text-emerald-700">Señal principal</p>
          <p className="mt-2 text-2xl font-semibold text-slate-900">AI Search</p>
          <p className="mt-2 text-sm leading-6 text-slate-600">La Home funciona como una puerta de entrada al buscador semántico.</p>
        </article>
        <article className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <p className="text-xs font-semibold uppercase tracking-[0.24em] text-emerald-700">Motor</p>
          <p className="mt-2 text-2xl font-semibold text-slate-900">pgvector</p>
          <p className="mt-2 text-sm leading-6 text-slate-600">Resultados exactos en producción y aproximados en local con el mismo lenguaje visual.</p>
        </article>
        <article className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <p className="text-xs font-semibold uppercase tracking-[0.24em] text-emerald-700">Flujo</p>
          <p className="mt-2 text-2xl font-semibold text-slate-900">CV → Grafos → Match</p>
          <p className="mt-2 text-sm leading-6 text-slate-600">El recorrido de usuario queda claro desde el primer vistazo.</p>
        </article>
        <article className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <p className="text-xs font-semibold uppercase tracking-[0.24em] text-emerald-700">Responsive</p>
          <p className="mt-2 text-2xl font-semibold text-slate-900">Mobile First</p>
          <p className="mt-2 text-sm leading-6 text-slate-600">La composición se adapta desde pantallas pequeñas sin perder jerarquía.</p>
        </article>
      </section>

      <section className="grid gap-4 md:grid-cols-3">
        {featureCards.map((feature) => (
          <article
            key={feature.title}
            className="group rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition-all duration-300 hover:-translate-y-1 hover:shadow-xl"
          >
            <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-emerald-50 ring-1 ring-emerald-100 transition-all duration-300 group-hover:bg-emerald-100">
              <FeatureIcon icon={feature.icon} />
            </div>
            <h2 className="text-lg font-semibold text-slate-900">{feature.title}</h2>
            <p className="mt-2 text-sm leading-6 text-slate-600">{feature.description}</p>
          </article>
        ))}
      </section>

      <section className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
        <article className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="flex items-center justify-between gap-4">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.24em] text-emerald-700">Preview</p>
              <h2 className="mt-2 text-2xl font-semibold text-slate-900">Vista previa de matches</h2>
              <p className="mt-2 text-sm leading-6 text-slate-600">
                Esta sección deja preparado el espacio para integrar <span className="font-semibold text-slate-900">MatchCard</span> con datos reales desde el dashboard.
              </p>
            </div>
            <a
              href="/dashboard"
              className="hidden rounded-full border border-slate-200 bg-slate-50 px-4 py-2 text-sm font-semibold text-slate-700 transition-all duration-300 hover:bg-slate-100 sm:inline-flex"
            >
              Abrir dashboard
            </a>
          </div>

          <div className="mt-6 grid gap-4 sm:grid-cols-2">
            {previewMatches.map((match) => (
              <div key={match.title} className="rounded-2xl border border-slate-200 bg-slate-50 p-4 transition-all duration-300 hover:-translate-y-0.5 hover:shadow-lg">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <h3 className="text-base font-semibold text-slate-900">{match.title}</h3>
                    <p className="mt-1 text-sm text-slate-600">{match.company}</p>
                  </div>
                  <span className="rounded-full bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-700">
                    {match.score.toFixed(1)}%
                  </span>
                </div>

                <div className="mt-4 flex flex-wrap gap-2 text-xs text-slate-600">
                  <span className="rounded-full bg-white px-3 py-1">{match.modality}</span>
                  <span className="rounded-full bg-white px-3 py-1">{match.location}</span>
                </div>

                <div className="mt-4 flex flex-wrap gap-2">
                  {match.tags.map((tag) => (
                    <span key={tag} className="rounded-full bg-white px-3 py-1 text-xs font-medium text-slate-700 ring-1 ring-slate-200">
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </article>

        <article className="rounded-3xl border border-slate-200 bg-[radial-gradient(circle_at_top,_rgba(16,185,129,0.12),_transparent_40%),linear-gradient(180deg,_#ffffff_0%,_#f8fafc_100%)] p-6 shadow-sm">
          <p className="text-xs font-semibold uppercase tracking-[0.24em] text-emerald-700">Cómo funciona</p>
          <div className="mt-5 space-y-4">
            {[
              {
                step: '01',
                title: 'Sube o registra tu CV',
                text: 'El sistema prepara la información del perfil para su análisis semántico.',
              },
              {
                step: '02',
                title: 'La IA interpreta el contexto',
                text: 'LangGraph estructura el texto y lo conecta con el flujo de matching.',
              },
              {
                step: '03',
                title: 'Exploras vacantes con precisión',
                text: 'Ves matches ordenados por afinidad y con una lectura visual clara.',
              },
            ].map((item) => (
              <div key={item.step} className="rounded-2xl border border-slate-200 bg-white p-4 transition-all duration-300 hover:border-emerald-200 hover:shadow-md">
                <div className="flex items-start gap-4">
                  <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-slate-900 text-sm font-semibold text-white">
                    {item.step}
                  </div>
                  <div>
                    <h3 className="font-semibold text-slate-900">{item.title}</h3>
                    <p className="mt-1 text-sm leading-6 text-slate-600">{item.text}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </article>
      </section>
    </div>
  )
}
