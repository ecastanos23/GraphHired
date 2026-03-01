import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'GraphHired - AI Job Matching',
  description: 'Find your perfect job match with AI-powered recommendations',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="es">
      <body className="bg-gray-50 min-h-screen">
        <nav className="bg-primary-700 text-white shadow-lg">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex items-center">
                <a href="/" className="text-2xl font-bold">
                  GraphHired
                </a>
              </div>
              <div className="flex items-center space-x-4">
                <a href="/" className="hover:bg-primary-600 px-3 py-2 rounded-md">
                  Inicio
                </a>
                <a href="/upload" className="hover:bg-primary-600 px-3 py-2 rounded-md">
                  Subir CV
                </a>
                <a href="/dashboard" className="hover:bg-primary-600 px-3 py-2 rounded-md">
                  Dashboard
                </a>
                <a href="/poc" className="hover:bg-primary-600 px-3 py-2 rounded-md text-sm bg-primary-800">
                  PoC Test
                </a>
              </div>
            </div>
          </div>
        </nav>
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {children}
        </main>
      </body>
    </html>
  )
}
