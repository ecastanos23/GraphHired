export default function Home() {
  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="text-center py-12 bg-gradient-to-r from-primary-600 to-primary-800 rounded-2xl text-white">
        <h1 className="text-4xl font-bold mb-4">
          Encuentra tu trabajo ideal con IA
        </h1>
        <p className="text-xl text-primary-100 mb-8 max-w-2xl mx-auto">
          GraphHired utiliza inteligencia artificial para analizar tu CV y 
          conectarte con las mejores oportunidades laborales.
        </p>
        <div className="flex justify-center gap-4">
          <a 
            href="/upload" 
            className="bg-white text-primary-700 px-8 py-3 rounded-lg font-semibold hover:bg-primary-50 transition-colors"
          >
            Subir mi CV
          </a>
          <a 
            href="/dashboard" 
            className="border-2 border-white text-white px-8 py-3 rounded-lg font-semibold hover:bg-white/10 transition-colors"
          >
            Ver vacantes
          </a>
        </div>
      </div>

      {/* Features */}
      <div className="grid md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-xl shadow-md">
          <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mb-4">
            <svg className="w-6 h-6 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <h3 className="text-lg font-semibold mb-2">Análisis de CV</h3>
          <p className="text-gray-600">
            Nuestra IA extrae automáticamente tus habilidades y experiencia de tu CV.
          </p>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-md">
          <div className="w-12 h-12 bg-success-500/20 rounded-lg flex items-center justify-center mb-4">
            <svg className="w-6 h-6 text-success-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
          <h3 className="text-lg font-semibold mb-2">Matching Inteligente</h3>
          <p className="text-gray-600">
            Comparamos tu perfil con vacantes usando algoritmos de matching semántico.
          </p>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-md">
          <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
            <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <h3 className="text-lg font-semibold mb-2">Autopostulación</h3>
          <p className="text-gray-600">
            Postúlate con un solo clic a las vacantes que mejor coinciden contigo.
          </p>
        </div>
      </div>

      {/* How it works */}
      <div className="bg-white rounded-xl shadow-md p-8">
        <h2 className="text-2xl font-bold text-center mb-8">¿Cómo funciona?</h2>
        <div className="grid md:grid-cols-4 gap-6">
          <div className="text-center">
            <div className="w-10 h-10 bg-primary-600 text-white rounded-full flex items-center justify-center mx-auto mb-3 font-bold">1</div>
            <h4 className="font-semibold mb-1">Sube tu CV</h4>
            <p className="text-sm text-gray-600">Carga tu hoja de vida en PDF o texto</p>
          </div>
          <div className="text-center">
            <div className="w-10 h-10 bg-primary-600 text-white rounded-full flex items-center justify-center mx-auto mb-3 font-bold">2</div>
            <h4 className="font-semibold mb-1">Indica preferencias</h4>
            <p className="text-sm text-gray-600">Salario esperado, modalidad y ubicación</p>
          </div>
          <div className="text-center">
            <div className="w-10 h-10 bg-primary-600 text-white rounded-full flex items-center justify-center mx-auto mb-3 font-bold">3</div>
            <h4 className="font-semibold mb-1">IA analiza</h4>
            <p className="text-sm text-gray-600">Extraemos skills y calculamos matches</p>
          </div>
          <div className="text-center">
            <div className="w-10 h-10 bg-primary-600 text-white rounded-full flex items-center justify-center mx-auto mb-3 font-bold">4</div>
            <h4 className="font-semibold mb-1">Postúlate</h4>
            <p className="text-sm text-gray-600">Aplica a las mejores vacantes para ti</p>
          </div>
        </div>
      </div>
    </div>
  )
}
