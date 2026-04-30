-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Logs table for PoC
CREATE TABLE IF NOT EXISTS logs (
    id SERIAL PRIMARY KEY,
    input_text TEXT NOT NULL,
    output_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Candidates table
CREATE TABLE IF NOT EXISTS candidates (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    phone VARCHAR(50),
    cv_text TEXT,
    cv_embedding vector(1536),
    expected_salary DECIMAL(12,2),
    work_modality VARCHAR(50),
    location VARCHAR(255),
    skills JSONB DEFAULT '[]',
    experience_years INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Job vacancies table
CREATE TABLE IF NOT EXISTS vacancies (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    company VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    description_embedding vector(1536),
    required_skills JSONB DEFAULT '[]',
    salary_min DECIMAL(12,2),
    salary_max DECIMAL(12,2),
    work_modality VARCHAR(50),
    location VARCHAR(255),
    experience_required INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Applications table
CREATE TABLE IF NOT EXISTS applications (
    id SERIAL PRIMARY KEY,
    candidate_id INTEGER REFERENCES candidates(id) ON DELETE CASCADE,
    vacancy_id INTEGER REFERENCES vacancies(id) ON DELETE CASCADE,
    match_score DECIMAL(5,2),
    status VARCHAR(50) DEFAULT 'postulado',
    evidence JSONB DEFAULT '{}',
    next_steps JSONB DEFAULT '[]',
    agent_reason TEXT,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(candidate_id, vacancy_id)
);

-- Users table for candidate authentication
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    candidate_id INTEGER UNIQUE REFERENCES candidates(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Appointments table for interview/follow-up scheduling
CREATE TABLE IF NOT EXISTS appointments (
    id SERIAL PRIMARY KEY,
    application_id INTEGER REFERENCES applications(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    location VARCHAR(255),
    start_at TIMESTAMP NOT NULL,
    end_at TIMESTAMP NOT NULL,
    google_calendar_url TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Agent trace events for explainability
CREATE TABLE IF NOT EXISTS agent_events (
    id SERIAL PRIMARY KEY,
    candidate_id INTEGER REFERENCES candidates(id) ON DELETE CASCADE,
    application_id INTEGER REFERENCES applications(id) ON DELETE CASCADE,
    agent_name VARCHAR(100) NOT NULL,
    action VARCHAR(255) NOT NULL,
    reason TEXT NOT NULL,
    input_summary TEXT,
    output_summary TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for vector similarity search
CREATE INDEX IF NOT EXISTS idx_candidates_embedding ON candidates USING ivfflat (cv_embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS idx_vacancies_embedding ON vacancies USING ivfflat (description_embedding vector_cosine_ops) WITH (lists = 100);

-- Insert sample vacancies for testing
INSERT INTO vacancies (title, company, description, required_skills, salary_min, salary_max, work_modality, location, experience_required) VALUES
('Senior Python Developer', 'TechCorp', 'Buscamos desarrollador Python senior con experiencia en FastAPI, Django y bases de datos. Trabajo en proyectos de IA y machine learning.', '["Python", "FastAPI", "Django", "PostgreSQL", "Docker", "AI/ML"]', 80000, 120000, 'remote', 'Colombia', 5),
('Full Stack Developer', 'InnovateTech', 'Desarrollador full stack para aplicaciones web modernas con React y Node.js. Experiencia en arquitecturas cloud.', '["JavaScript", "React", "Node.js", "TypeScript", "AWS", "MongoDB"]', 60000, 90000, 'hybrid', 'Bogotá', 3),
('Data Engineer', 'DataFlow', 'Ingeniero de datos para diseñar pipelines ETL y trabajar con big data. Conocimientos en Spark y cloud.', '["Python", "Spark", "SQL", "Airflow", "AWS", "Data Modeling"]', 70000, 100000, 'remote', 'Latinoamérica', 4),
('Frontend React Developer', 'DesignStudio', 'Desarrollador frontend especializado en React y diseño de interfaces modernas.', '["React", "TypeScript", "CSS", "Tailwind", "Next.js", "Figma"]', 50000, 75000, 'onsite', 'Medellín', 2),
('DevOps Engineer', 'CloudNative', 'Ingeniero DevOps para automatización de infraestructura y CI/CD.', '["Docker", "Kubernetes", "Terraform", "AWS", "GitHub Actions", "Linux"]', 75000, 110000, 'remote', 'Colombia', 4);
