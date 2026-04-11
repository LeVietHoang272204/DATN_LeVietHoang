"""RAG Query Pipeline with confidence scoring.

Improvements included:
- Confidence scoring for each answer
- Conflict detection (newer documents prioritized)
- Low-confidence warnings
- Source citation in structured format
"""

import json
import logging
from typing import Optional, List

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

from app.ai.vectorstore import search_similar
from app.ai.prompt_templates import (
    SYSTEM_PROMPT,
    RAG_PROMPT_TEMPLATE,
    SUMMARY_PROMPT_TEMPLATE,
    CONFIDENCE_PROMPT,
    CHATBOT_PROMPT,
)
from app.core.rate_limiter import gemini_limiter
from app.config import settings

logger = logging.getLogger(__name__)


def _get_llm() -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model=settings.GEMINI_MODEL,
        google_api_key=settings.GOOGLE_API_KEY,
        temperature=0.1,
        convert_system_message_to_human=True,
    )


def query_legal(
    question: str,
    collection_name: Optional[str] = None,
    legal_field: Optional[str] = None,
    active_only: bool = True,
    top_k: int = settings.TOP_K_RESULTS,
    chat_history: Optional[List[dict]] = None,
    prefetched_results: Optional[List[dict]] = None,
) -> dict:
    """Main RAG query: retrieve context + generate answer with confidence.

    Returns:
        {
            "answer": str,
            "confidence": float,
            "sources": [{"document_title": ..., "chunk_text": ..., "relevance_score": ...}],
            "warning": str | None
        }
    """
    # Build filter
    filter_dict = {}
    if legal_field:
        filter_dict["legal_field"] = legal_field

    # Step 1: Retrieve relevant chunks (use prefetched if provided)
    if prefetched_results is not None:
        results = prefetched_results
    else:
        results = search_similar(
            query=question,
            collection_name=collection_name,
            top_k=top_k,
            filter_dict=filter_dict if filter_dict else None,
        )

    if not results:
        # Fallback: trả lời như chatbot thông thường
        return _chatbot_fallback(question, chat_history)

    # Check if retrieved docs are actually relevant (avg score > 0.35)
    avg_score = sum(r.get("score", 0) for r in results) / len(results)
    if avg_score < 0.35:
        # Scores too low = docs not relevant, use chatbot mode
        return _chatbot_fallback(question, chat_history)

    # Step 2: Build context with metadata
    context_parts = []
    sources = []
    for r in results:
        meta = r.get("metadata", {})
        doc_title = meta.get("document_title", "Không rõ")
        doc_number = meta.get("document_number", "")
        section = meta.get("section", "")
        source_label = f"[{doc_title}"
        if doc_number:
            source_label += f" - {doc_number}"
        if section:
            source_label += f" - {section}"
        source_label += "]"

        context_parts.append(f"{source_label}\n{r['text']}")
        sources.append({
            "document_title": doc_title,
            "document_number": doc_number,
            "chunk_text": r["text"][:300],
            "relevance_score": round(r["score"], 3),
        })

    context = "\n\n---\n\n".join(context_parts)

    # Step 3: Build prompt and generate
    prompt = RAG_PROMPT_TEMPLATE.format(context=context, question=question)

    llm = _get_llm()
    messages = [SystemMessage(content=SYSTEM_PROMPT)]

    # Add chat history for multi-turn
    if chat_history:
        for msg in chat_history[-6:]:  # Last 3 turns (6 messages)
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            else:
                from langchain_core.messages import AIMessage
                messages.append(AIMessage(content=msg["content"]))

    messages.append(HumanMessage(content=prompt))

    gemini_limiter.wait_if_needed()
    response = llm.invoke(messages)
    answer = response.content

    # Step 4: Confidence scoring from retrieval scores (no extra Gemini call)
    confidence = _compute_confidence_from_results(results)

    warning = None
    if confidence < settings.CONFIDENCE_THRESHOLD:
        warning = (
            "⚠️ Độ tin cậy thấp. Câu trả lời có thể chưa đầy đủ hoặc chính xác. "
            "Vui lòng tham khảo thêm ý kiến chuyên gia pháp lý."
        )

    return {
        "answer": answer,
        "confidence": confidence,
        "sources": sources,
        "warning": warning,
    }


def _chatbot_fallback(
    question: str,
    chat_history: Optional[List[dict]] = None,
) -> dict:
    """Fallback to general chatbot when no relevant documents found."""
    llm = _get_llm()
    messages = [SystemMessage(content=SYSTEM_PROMPT)]

    if chat_history:
        for msg in chat_history[-6:]:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            else:
                from langchain_core.messages import AIMessage
                messages.append(AIMessage(content=msg["content"]))

    prompt = CHATBOT_PROMPT.format(question=question)
    messages.append(HumanMessage(content=prompt))

    gemini_limiter.wait_if_needed()
    response = llm.invoke(messages)

    return {
        "answer": response.content,
        "confidence": 0.0,
        "sources": [],
        "warning": None,
    }


def summarize_text(
    text: str, summary_length: str = "trung bình"
) -> str:
    """Summarize a legal document text."""
    prompt = SUMMARY_PROMPT_TEMPLATE.format(text=text[:8000], summary_length=summary_length)

    llm = _get_llm()
    gemini_limiter.wait_if_needed()
    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content


def stream_legal_response(
    question: str,
    collection_name: Optional[str] = None,
    legal_field: Optional[str] = None,
    chat_history: Optional[List[dict]] = None,
):
    """Streaming version of query_legal for SSE responses."""
    filter_dict = {}
    if legal_field:
        filter_dict["legal_field"] = legal_field

    results = search_similar(
        query=question,
        collection_name=collection_name,
        filter_dict=filter_dict if filter_dict else None,
    )

    if not results:
        yield {
            "type": "answer",
            "content": "Tôi không tìm thấy thông tin liên quan trong cơ sở dữ liệu.",
        }
        return

    context_parts = []
    sources = []
    for r in results:
        meta = r.get("metadata", {})
        doc_title = meta.get("document_title", "Không rõ")
        context_parts.append(f"[{doc_title}]\n{r['text']}")
        sources.append({
            "document_title": doc_title,
            "chunk_text": r["text"][:200],
            "relevance_score": round(r["score"], 3),
        })

    context = "\n\n---\n\n".join(context_parts)
    prompt = RAG_PROMPT_TEMPLATE.format(context=context, question=question)

    llm = _get_llm()
    messages = [SystemMessage(content=SYSTEM_PROMPT)]
    if chat_history:
        for msg in chat_history[-6:]:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            else:
                from langchain_core.messages import AIMessage
                messages.append(AIMessage(content=msg["content"]))
    messages.append(HumanMessage(content=prompt))

    gemini_limiter.wait_if_needed()
    for chunk in llm.stream(messages):
        if chunk.content:
            yield {"type": "token", "content": chunk.content}

    yield {"type": "sources", "content": json.dumps(sources, ensure_ascii=False)}
    yield {"type": "done", "content": ""}


def _compute_confidence_from_results(results: list) -> float:
    """Compute confidence from retrieval similarity scores (no extra LLM call)."""
    if not results:
        return 0.0
    scores = [r.get("score", 0.0) for r in results]
    avg_score = sum(scores) / len(scores)
    # ChromaDB cosine distance: lower = more similar; convert to 0–1 confidence
    # If score is already similarity (0–1), use directly
    # Guard: clamp to [0, 1]
    return max(0.0, min(1.0, float(avg_score)))
