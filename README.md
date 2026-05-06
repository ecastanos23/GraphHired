<!--
COMENTARIO DE ARCHIVO - GRAPHHIRED
Documentacion principal del Sprint 2. Partes: requisitos, configuracion, ejecucion con Docker, flujo de demo, agentes, endpoints y notas de alcance.
-->

# GraphHired - Sprint 2

MVP tecnico de Profile Manager con arquitectura agentica usando LangGraph, FastAPI, Next.js y PostgreSQL/pgvector.

## Requisitos

- Docker Desktop
- Docker Compose
- `OPENAI_API_KEY` para la demo completa con IA

## Configuracion

Crear un archivo `.env` en la raiz:

```env
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=graphhired
DB_HOST=db
DB_PORT=5432

BACKEND_PORT=8000
SECRET_KEY=dev-secret-key-change-me
OPENAI_API_KEY=tu_api_key
```

## Ejecucion

```bash
docker compose up -d --build
```

Servicios:

- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- Swagger: http://localhost:8000/docs
- Health: http://localhost:8000/health
- AI health: http://localhost:8000/health/ai

## Flujo de demo

1. Entrar a `/register`.
2. Subir un CV en PDF y usar "Analizar con OpenAI".
3. Revisar y corregir los campos autollenados.
4. Crear cuenta.
5. Ir al dashboard para ver recomendaciones.
6. Revisar por qué la IA eligió cada empresa: score, desglose y explicación.
7. Hacer una postulacion simulada.
8. Revisar evidencia, proximos pasos y trazabilidad por agente.
9. Agendar una entrevista.
10. Abrir el boton de Google Calendar para guardar el evento prellenado.

## Agentes

- Agente de Perfil: extrae informacion del CV, detecta vacios y prepara el perfil.
- Agente de Vacantes: genera y normaliza un dataset curado de vacantes Colombia.
- Agente de Matching: calcula recomendaciones explicables.
- Agente de Postulacion: simula la postulacion y guarda evidencia.
- Agente de Seguimiento: genera proximos pasos y enlaces de Google Calendar.

## Endpoints principales

- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/me`
- `POST /api/candidates/parse-cv-pdf`
- `GET /api/matching/candidate/{candidate_id}`
- `POST /api/matching/apply`
- `GET /api/matching/applications/candidate/{candidate_id}`
- `POST /api/applications/{application_id}/appointments`
- `GET /api/applications/{application_id}/appointments`
- `GET /api/agents/trace?candidate_id=...`

## Notas

- No se implementa OAuth de Google. El calendario usa un link prellenado de Google Calendar.
- No hay scraping en vivo. El sprint usa dataset curado y reproducible.
- La wiki se actualizara despues con el formato academico final.
