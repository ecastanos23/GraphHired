/*
 * COMENTARIO DE ARCHIVO - GRAPHHIRED
 * Pagina de login. Partes: formulario de credenciales, llamada a auth/login, guardado del token y redireccion al dashboard.
 */
'use client';

import { useState } from 'react';
import { useApi } from '@/hooks/useApi';
import { HoverButton } from '@/components/ui/hover-glow-button';

interface AuthResponse {
  access_token: string;
  user: {
    candidate_id: number | null;
  };
}

export default function LoginPage() {
  const { post, loading, error } = useApi();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = async (event: React.FormEvent) => {
    event.preventDefault();
    const response = await post<AuthResponse>('/api/auth/login', { email, password });
    if (!response) return;
    localStorage.setItem('graphhired_token', response.access_token);
    const candidateId = response.user.candidate_id;
    window.location.href = candidateId ? `/dashboard?candidateId=${candidateId}` : '/dashboard';
  };

  return (
    <div className="mx-auto max-w-xl space-y-6">
      <section className="overflow-hidden rounded-[2rem] border border-slate-200 bg-white shadow-[0_18px_60px_rgba(15,23,42,0.08)]">
        <div className="bg-[linear-gradient(135deg,_#0f172a_0%,_#111827_52%,_#065f46_100%)] px-6 py-9 text-white">
          <p className="text-xs font-semibold uppercase tracking-[0.28em] text-emerald-100">Acceso candidato</p>
          <h1 className="mt-3 text-3xl font-semibold tracking-tight">Inicia sesion</h1>
          <p className="mt-3 text-sm leading-6 text-slate-200">
            Entra para continuar tu proceso, revisar recomendaciones y agendar entrevistas.
          </p>
        </div>
      </section>

      <form onSubmit={handleLogin} className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
        {error && <div className="mb-4 rounded-2xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700">{error}</div>}
        <label className="block text-sm font-medium text-slate-700">
          Email
          <input
            required
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            className="mt-1 block w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-emerald-400 focus:ring-4 focus:ring-emerald-200/60"
          />
        </label>
        <label className="mt-5 block text-sm font-medium text-slate-700">
          Contrasena
          <input
            required
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            className="mt-1 block w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-emerald-400 focus:ring-4 focus:ring-emerald-200/60"
          />
        </label>
        <HoverButton
          type="submit"
          disabled={loading}
          className="mt-6 w-full rounded-2xl py-4 text-base font-semibold"
          glowColor="#34d399"
          backgroundColor="#10b981"
          textColor="#ffffff"
          hoverTextColor="#d1fae5"
        >
          {loading ? 'Entrando...' : 'Entrar'}
        </HoverButton>
        <p className="mt-5 text-center text-sm text-slate-600">
          Aun no tienes cuenta?{' '}
          <a href="/register" className="font-semibold text-emerald-700 underline decoration-emerald-300 underline-offset-4">
            Registrate con tu CV
          </a>
        </p>
      </form>
    </div>
  );
}
