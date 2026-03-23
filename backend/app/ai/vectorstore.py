"""ChromaDB vector store management.

Improvement: Personal RAG isolation via per-user collections.
"""

import logging
from typing import List, Optional
from langchain_chroma import Chroma
from app.ai.embeddings import get_embedding_function
from app.config import settings

logger = logging.getLogger(__name__)

_stores: dict = {}


def get_vectorstore(collection_name: Optional[str] = None) -> Chroma:
    """Get or create a ChromaDB vector store.

    For public legal docs: use default collection.
    For personal docs: use 'user_{user_id}' collection for isolation.
    """
    name = collection_name or settings.CHROMA_COLLECTION_NAME
    if name not in _stores:
        _stores[name] = Chroma(
            collection_name=name,
            embedding_function=get_embedding_function(),
            persist_directory=settings.CHROMA_PERSIST_DIR,
        )
    return _stores[name]


def get_personal_vectorstore(user_id: int) -> Chroma:
    """Get isolated vector store for a user's personal documents."""
    return get_vectorstore(f"user_{user_id}")


def add_chunks_to_store(
    chunks: List[dict],
    collection_name: Optional[str] = None,
) -> int:
    """Add text chunks with metadata to vector store.

    Args:
        chunks: List of {"text": ..., "metadata": {...}} dicts.
        collection_name: Target collection (None = public legal docs).

    Returns:
        Number of chunks added.
    """
    if not chunks:
        return 0

    store = get_vectorstore(collection_name)
    texts = [c["text"] for c in chunks]
    metadatas = [c.get("metadata", {}) for c in chunks]

    store.add_texts(texts=texts, metadatas=metadatas)
    logger.info(f"Added {len(texts)} chunks to collection '{collection_name}'")
    return len(texts)


def search_similar(
    query: str,
    collection_name: Optional[str] = None,
    top_k: int = settings.TOP_K_RESULTS,
    filter_dict: Optional[dict] = None,
) -> List[dict]:
    """Search for similar chunks in vector store.

    Returns list of {"text": str, "metadata": dict, "score": float}.
    """
    store = get_vectorstore(collection_name)
    results = store.similarity_search_with_relevance_scores(
        query, k=top_k, filter=filter_dict
    )

    return [
        {
            "text": doc.page_content,
            "metadata": doc.metadata,
            "score": score,
        }
        for doc, score in results
    ]
