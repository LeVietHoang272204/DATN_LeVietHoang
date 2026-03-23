"""Smart chunking for Vietnamese legal documents.

Improvement: Instead of fixed 500-token chunks, we use a hybrid strategy:
1. Try to split by legal article structure (Điều, Khoản, Mục, Chương)
2. Fallback to recursive character splitting with overlap
This preserves legal context within each chunk.
"""

import re
from typing import List, Optional
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.config import settings


# Vietnamese legal structure patterns (ordered by hierarchy)
LEGAL_SEPARATORS = [
    r"\n(?=CHƯƠNG\s+[IVXLCDM\d]+)",      # Chương (Chapter)
    r"\n(?=Mục\s+\d+)",                    # Mục (Section)
    r"\n(?=Điều\s+\d+)",                   # Điều (Article) — primary split
    r"\n(?=\d+\.\s)",                       # Khoản (Clause) numbered
    r"\n(?=[a-zđ]\)\s)",                    # Điểm (Point) lettered
]


def chunk_legal_text(
    text: str,
    chunk_size: int = settings.CHUNK_SIZE,
    chunk_overlap: int = settings.CHUNK_OVERLAP,
    metadata: Optional[dict] = None,
) -> List[dict]:
    """Split legal text into chunks preserving article boundaries.

    Returns list of {"text": ..., "metadata": {...}} dicts.
    """
    if not text or not text.strip():
        return []

    # Step 1: Try article-level splitting first
    articles = _split_by_articles(text)

    chunks = []
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " "],
        length_function=len,
    )

    if articles and len(articles) > 1:
        # Split each article further if too long
        for article in articles:
            article_text = article["text"]
            article_meta = article.get("meta", {})
            if len(article_text) > chunk_size:
                sub_chunks = splitter.split_text(article_text)
                for i, sc in enumerate(sub_chunks):
                    chunk_meta = {**(metadata or {}), **article_meta, "sub_chunk": i}
                    chunks.append({"text": sc, "metadata": chunk_meta})
            else:
                chunk_meta = {**(metadata or {}), **article_meta}
                chunks.append({"text": article_text, "metadata": chunk_meta})
    else:
        # Fallback: recursive splitting
        sub_chunks = splitter.split_text(text)
        for i, sc in enumerate(sub_chunks):
            chunk_meta = {**(metadata or {}), "chunk_index": i}
            chunks.append({"text": sc, "metadata": chunk_meta})

    return chunks


def _split_by_articles(text: str) -> List[dict]:
    """Split text by Điều (Article) boundaries."""
    pattern = r"(Điều\s+(\d+)[^\n]*)"
    parts = re.split(pattern, text)

    articles = []
    current_text = parts[0].strip() if parts else ""

    # If there's preamble before first article, include it
    if current_text:
        articles.append({"text": current_text, "meta": {"section": "preamble"}})

    i = 1
    while i < len(parts):
        if i + 2 < len(parts):
            header = parts[i]
            article_num = parts[i + 1]
            body = parts[i + 2].strip()
            full_text = f"{header}\n{body}" if body else header
            articles.append({
                "text": full_text,
                "meta": {"article_number": article_num, "section": f"Điều {article_num}"},
            })
            i += 3
        else:
            remaining = "".join(parts[i:]).strip()
            if remaining:
                articles.append({"text": remaining, "meta": {"section": "appendix"}})
            break

    return articles
