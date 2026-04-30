import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'GraphHired by Magneto - AI Job Matching',
  description: 'Profile Manager agentico by Magneto para recomendaciones laborales con IA',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="es">
      <body className="min-h-screen">
        <nav className="sticky top-0 z-40 border-b border-slate-200/70 bg-white/80 backdrop-blur-xl">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="flex flex-col gap-4 py-4 sm:flex-row sm:items-center sm:justify-between">
              <a href="/" className="inline-flex items-center gap-3 transition-all duration-300 hover:-translate-y-0.5">
                <span className="inline-flex h-10 w-10 items-center justify-center rounded-2xl bg-[linear-gradient(135deg,_#0f172a_0%,_#064e3b_100%)] text-sm font-semibold text-emerald-200 shadow-lg shadow-emerald-900/20">
                  GH
                </span>
                <span className="min-w-0">
                  <span className="block text-lg font-semibold tracking-tight text-slate-900">GraphHired</span>
                  <span className="mt-0.5 block whitespace-nowrap text-[10px] font-semibold uppercase tracking-[0.14em] text-emerald-700">
                    Buscador IA by <span className="text-slate-900">Magneto</span>
                  </span>
                </span>
              </a>

              <div className="flex gap-2 overflow-x-auto pb-1 sm:pb-0">
                <a
                  href="/"
                  className="whitespace-nowrap rounded-full border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 transition-all duration-300 hover:-translate-y-0.5 hover:border-emerald-200 hover:bg-emerald-50 hover:text-emerald-800"
                >
                  Inicio
                </a>
                <a
                  href="/register"
                  className="whitespace-nowrap rounded-full border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 transition-all duration-300 hover:-translate-y-0.5 hover:border-emerald-200 hover:bg-emerald-50 hover:text-emerald-800"
                >
                  Registro
                </a>
                <a
                  href="/login"
                  className="whitespace-nowrap rounded-full border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 transition-all duration-300 hover:-translate-y-0.5 hover:border-emerald-200 hover:bg-emerald-50 hover:text-emerald-800"
                >
                  Login
                </a>
                <a
                  href="/upload"
                  className="whitespace-nowrap rounded-full border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 transition-all duration-300 hover:-translate-y-0.5 hover:border-emerald-200 hover:bg-emerald-50 hover:text-emerald-800"
                >
                  Subir CV
                </a>
                <a
                  href="/dashboard"
                  className="whitespace-nowrap rounded-full border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 transition-all duration-300 hover:-translate-y-0.5 hover:border-emerald-200 hover:bg-emerald-50 hover:text-emerald-800"
                >
                  Dashboard
                </a>
                <a
                  href="/poc"
                  className="whitespace-nowrap rounded-full border border-emerald-200 bg-emerald-50 px-4 py-2 text-sm font-semibold text-emerald-800 transition-all duration-300 hover:-translate-y-0.5 hover:bg-emerald-100"
                >
                  PoC Test
                </a>
              </div>
            </div>
          </div>
        </nav>
        <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
          {children}
        </main>
      </body>
    </html>
  )
}
