# COMENTARIO DE ARCHIVO - GRAPHHIRED
# Servicio de matching semantico. Partes: keywords fallback, matching SQLite, matching pgvector y seleccion del motor segun configuracion.

"""Matching service layer.

Decides which engine to use based on runtime configuration.
"""
from __future__ import annotations

from collections.abc import Iterable
import re

import bleach
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.entities import Candidate, Vacancy


class MatchingService:
    """Facade that switches between SQLite keyword matching and pgvector matching."""

    @staticmethod
    def _normalize_model_name(model_name: str) -> str:
        raw = (model_name or "").strip()
        if not raw:
            return "models/gemini-embedding-001"
        if raw in {"text-embedding-004", "models/text-embedding-004"}:
            return "models/gemini-embedding-001"
        if raw.startswith("models/"):
            return raw
        return f"models/{raw}"

    @staticmethod
    def _resolve_embedding_model_name() -> str:
        return MatchingService._normalize_model_name(settings.GEMINI_EMBEDDING_MODEL)

    @staticmethod
    async def get_best_matches(
        db: AsyncSession,
        candidate: Candidate,
        limit: int = 5,
    ) -> list[tuple[Vacancy, float]]:
        if settings.USE_SQLITE:
            return await MatchingService._sqlite_text_matching(db, candidate, limit)
        return await MatchingService._pgvector_semantic_matching(db, candidate, limit)

    @staticmethod
    def _candidate_keywords(candidate: Candidate) -> list[str]:
        keywords: list[str] = []

        raw_skills = candidate.skills or []
        if isinstance(raw_skills, str):
            raw_iterable: Iterable[str] = raw_skills.split(",")
        else:
            raw_iterable = raw_skills

        for item in raw_iterable:
            if not item:
                continue
            cleaned = bleach.clean(str(item), tags=[], attributes={}, strip=True).strip().lower()
            if cleaned and cleaned not in keywords:
                keywords.append(cleaned)

        if keywords:
            return keywords

        fallback_text = bleach.clean(candidate.cv_text or "", tags=[], attributes={}, strip=True).lower()
        if not fallback_text:
            return keywords

        tokens = re.split(r"[\s,;/|]+", fallback_text)
        for token in tokens:
            token = token.strip()
            if len(token) < 3:
                continue
            if token not in keywords:
                keywords.append(token)

        return keywords

    @staticmethod
    async def _sqlite_text_matching(
        db: AsyncSession,
        candidate: Candidate,
        limit: int,
    ) -> list[tuple[Vacancy, float]]:
        """Fallback: keyword matching scored in Python for SQLite development."""
        keywords = MatchingService._candidate_keywords(candidate)

        stmt = select(Vacancy).where(Vacancy.is_active.is_(True))
        result = await db.execute(stmt)
        all_vacancies = result.scalars().all()

        # Filter by exact location match
        candidate_location = (candidate.location or "").strip().lower()
        vacancies = [
            v for v in all_vacancies 
            if (v.location or "").strip().lower() == candidate_location
        ]

        if not vacancies:
            return []

        scored_vacancies: list[tuple[float, Vacancy]] = []
        for vacancy in vacancies:
            search_fragments = [
                vacancy.title,
                vacancy.company,
                vacancy.description,
                vacancy.location,
                vacancy.work_modality,
            ]
            if vacancy.required_skills:
                search_fragments.extend(str(skill) for skill in vacancy.required_skills if skill)

            haystack = " ".join(fragment.lower() for fragment in search_fragments if fragment)
            matched_keywords = sum(1 for keyword in keywords if keyword in haystack)
            similarity_score = (matched_keywords / max(len(keywords), 1)) * 100.0
            scored_vacancies.append((similarity_score, vacancy))

        scored_vacancies.sort(key=lambda item: (item[0], item[1].id), reverse=True)
        return [(vacancy, score) for score, vacancy in scored_vacancies[:limit]]

    @staticmethod
    async def _pgvector_semantic_matching(
        db: AsyncSession,
        candidate: Candidate,
        limit: int,
    ) -> list[tuple[Vacancy, float]]:
        """Production path using cosine distance over pgvector embeddings."""
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not configured")

        candidate_embedding = candidate.cv_embedding
        if not candidate_embedding:
            if not candidate.cv_text:
                raise ValueError("Candidate has no CV text to generate an embedding")

            embeddings = GoogleGenerativeAIEmbeddings(
                model=MatchingService._resolve_embedding_model_name(),
                google_api_key=settings.GEMINI_API_KEY,
            )
            clean_cv_text = bleach.clean(candidate.cv_text, tags=[], attributes={}, strip=True).strip()
            candidate_embedding = embeddings.embed_query(
                clean_cv_text,
                output_dimensionality=1536,
            )
            candidate.cv_embedding = candidate_embedding
            await db.commit()

        embeddings = GoogleGenerativeAIEmbeddings(
            model=MatchingService._resolve_embedding_model_name(),
            google_api_key=settings.GEMINI_API_KEY,
        )

        vacancies_without_embedding_stmt = select(Vacancy).where(
            Vacancy.is_active.is_(True),
            Vacancy.description_embedding.is_(None),
        )
        vacancies_without_embedding = (await db.execute(vacancies_without_embedding_stmt)).scalars().all()

        for vacancy in vacancies_without_embedding:
            clean_description = bleach.clean(vacancy.description or "", tags=[], attributes={}, strip=True).strip()
            if not clean_description:
                continue
            vacancy.description_embedding = embeddings.embed_query(
                clean_description,
                output_dimensionality=1536,
            )

        if vacancies_without_embedding:
            await db.commit()

        distance_expr = Vacancy.description_embedding.cosine_distance(candidate_embedding)
        candidate_location = (candidate.location or "").strip().lower()
        stmt = (
            select(Vacancy, distance_expr.label("distance"))
            .where(
                Vacancy.is_active.is_(True), 
                Vacancy.description_embedding.is_not(None),
                # Filter by exact location match
            )
            .order_by(distance_expr)
            .limit(limit)
        )

        result = await db.execute(stmt)
        rows = result.all()

        # Filter by location in Python to handle case-insensitive comparison
        matches: list[tuple[Vacancy, float]] = []
        for vacancy, distance in rows:
            vacancy_location = (vacancy.location or "").strip().lower()
            if vacancy_location == candidate_location:
                similarity_score = max(0.0, min(100.0, (1.0 - float(distance)) * 100.0))
                matches.append((vacancy, similarity_score))

        return matches
