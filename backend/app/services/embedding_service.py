# COMENTARIO DE ARCHIVO - GRAPHHIRED
# Servicio de embeddings. Partes: normalizacion de nombre de modelo, cache del cliente Gemini y generacion segura de vectores.

"""Embedding service built on top of Gemini embeddings."""
from __future__ import annotations

import logging
from typing import Optional

from langchain_google_genai import GoogleGenerativeAIEmbeddings

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Encapsulates embedding model setup and vector generation."""

    _embed_model: Optional[GoogleGenerativeAIEmbeddings] = None

    @staticmethod
    def _normalize_model_name(model_name: str) -> str:
        raw = (model_name or "").strip()
        if not raw:
            return "models/gemini-embedding-001"

        # Backward compatibility: this model name may be unavailable on some keys/endpoints.
        if raw in {"text-embedding-004", "models/text-embedding-004"}:
            return "models/gemini-embedding-001"

        if raw.startswith("models/"):
            return raw
        return f"models/{raw}"

    @staticmethod
    def _resolve_embedding_model_name() -> str:
        return EmbeddingService._normalize_model_name(settings.GEMINI_EMBEDDING_MODEL)

    @classmethod
    def _get_model(cls) -> GoogleGenerativeAIEmbeddings:
        if cls._embed_model is not None:
            return cls._embed_model

        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not configured")

        cls._embed_model = GoogleGenerativeAIEmbeddings(
            model=cls._resolve_embedding_model_name(),
            google_api_key=settings.GEMINI_API_KEY,
        )
        return cls._embed_model

    @classmethod
    def generate_embedding(cls, text: str) -> Optional[list[float]]:
        """Generate a vector for the provided text.

        Returns None when input is empty or any provider/runtime error occurs.
        """
        if not text or not text.strip():
            return None

        try:
            model = cls._get_model()
            vector = model.embed_query(text, output_dimensionality=1536)
            if not vector:
                return None
            return [float(value) for value in vector]
        except Exception as exc:
            logger.exception("Failed to generate embedding: %s", exc)
            return None
