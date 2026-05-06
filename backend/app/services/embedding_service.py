# COMENTARIO DE ARCHIVO - GRAPHHIRED
# Servicio de embeddings. Partes: normalizacion de nombre de modelo, cache del cliente OpenAI y generacion segura de vectores.

"""Embedding service built on top of OpenAI embeddings."""
from __future__ import annotations

import logging
from typing import Optional

from langchain_openai import OpenAIEmbeddings

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Encapsulates embedding model setup and vector generation."""

    _embed_model: Optional[OpenAIEmbeddings] = None

    @staticmethod
    def _normalize_model_name(model_name: str) -> str:
        raw = (model_name or "").strip()
        if not raw:
            return "text-embedding-3-small"
        return raw

    @staticmethod
    def _resolve_embedding_model_name() -> str:
        return EmbeddingService._normalize_model_name(settings.OPENAI_EMBEDDING_MODEL)

    @classmethod
    def _get_model(cls) -> OpenAIEmbeddings:
        if cls._embed_model is not None:
            return cls._embed_model

        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not configured")

        cls._embed_model = OpenAIEmbeddings(
            model=cls._resolve_embedding_model_name(),
            api_key=settings.OPENAI_API_KEY,
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
