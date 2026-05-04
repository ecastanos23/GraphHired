/*
 * COMENTARIO DE ARCHIVO - GRAPHHIRED
 * Configuracion Next.js. Partes: opciones del framework para compilar y servir el frontend.
 */
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },
}

module.exports = nextConfig
