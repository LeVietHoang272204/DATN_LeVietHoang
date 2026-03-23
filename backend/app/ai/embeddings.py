"""BGE-M3 Embedding wrapper for Vietnamese legal text."""

from langchain_core.embeddings import Embeddings
from sentence_transformers import SentenceTransformer
from typing import List
from app.config import settings

_model = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(
            settings.EMBEDDING_MODEL, device=settings.EMBEDDING_DEVICE
        )
    return _model


class BGEM3Embeddings(Embeddings):
    """LangChain-compatible wrapper around BGE-M3 for Vietnamese text."""

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        model = _get_model()
        embeddings = model.encode(texts, normalize_embeddings=True)
        return embeddings.tolist()

    def embed_query(self, text: str) -> List[float]:
        model = _get_model()
        embedding = model.encode(text, normalize_embeddings=True)
        return embedding.tolist()


def get_embedding_function() -> BGEM3Embeddings:
    return BGEM3Embeddings()
