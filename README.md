# GraphHired

## Description
GraphHired project with Clean Architecture.

## Project Structure
GraphHired/
```text
GraphHired/
├── docker-compose.yml           # Orquestación de infraestructura (Vista Física)
├── frontend/                    # Capa de Presentación (Client)
│   ├── src/
│   │   ├── app/                 # Rutas de Next.js (Dashboard, Formularios)
│   │   ├── components/          # Componentes de UI reutilizables (TailwindCSS)
│   │   └── lib/                 # Clientes HTTP para consumir la API
│   ├── package.json             
│   └── Dockerfile               
└── backend/                     # Capa de Lógica y Datos (Server)
    ├── app/
    │   ├── api/                 # Capa de Presentación del API
    │   │   └── routes/          # Endpoints (ej. candidates.py)
    │   ├── core/                # Configuración global y conexión a DB (database.py)
    │   ├── models/              # Modelos de SQLAlchemy (entities.py)
    │   └── services/            # Lógica de negocio e IA (embedding_service.py)
    ├── requirements.txt         
    ├── main.py                  # Punto de entrada de FastAPI
    └── Dockerfile
```
## Getting Started

### Prerequisites
- Docker & Docker Compose
- Node.js (for frontend)
- Python 3.x (for backend)

### Installation
1. Clone the repository
2. Copy `.env.example` to `.env` and configure


## Guía rápida para desarrolladores (Onboarding)

### 1) Requisitos
- Docker Desktop
- Git
- Visual Studio Code (recomendado)

### 2) Estructura del proyecto
- Orquestación: `docker-compose.yml`
- Variables globales: `.env`
- Backend (FastAPI): `backend/app/main.py`
- Frontend (Next.js): `frontend/app/`
- SQL inicial: `backend/init.sql`

### 3) Configuración inicial
1. Clonar repositorio.
2. Crear/configurar variables:
   - Raíz: `.env`
   - Backend referencia: `backend/.env.example`
   - Frontend: `frontend/.env.local`
3. Levantar servicios:

```sh
docker-compose up --build
```

### 4) Verificación rápida
- Frontend: `http://localhost:3000`
- Backend health: `http://localhost:8000/health`
- API docs: `http://localhost:8000/docs`

### 5) Flujo mínimo a probar
1. **PoC** (`/poc`): transforma texto a mayúsculas y registra en DB.
2. **Upload CV** (`/upload`): carga CV y análisis de perfil.
3. **Dashboard** (`/dashboard`): matching de vacantes y postulación.

### 6) Convenciones del equipo
- Backend:
  - Schemas: `backend/app/models/schemas.py`
  - Seguridad/sanitización: `backend/app/core/security.py`
  - Acceso a datos: `backend/app/repositories/`
- Frontend:
  - Cliente API: `frontend/hooks/useApi.ts`
  - Componentes: `frontend/components/`

### 7) Checklist antes de abrir PR
- [ ] Ejecuta sin errores con `docker-compose up --build`
- [ ] Prueba `/poc`, `/upload`, `/dashboard`
- [ ] Revisa contrato API en `/docs`
- [ ] No rompe validación/sanitización
- [ ] Actualiza README si cambia flujo o arquitectura

### 8) Comandos útiles
```sh
# Ver logs
docker-compose logs -f

# Reiniciar limpio (contenedores + volúmenes)
docker-compose down -v
docker-compose up --build
```

3. Run `docker-compose up`

## License
MIT
