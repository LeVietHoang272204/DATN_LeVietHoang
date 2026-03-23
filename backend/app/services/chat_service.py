import json
from typing import Optional, List
from sqlalchemy.orm import Session

from app.models.chat import ChatSession, ChatMessage
from app.ai.rag_pipeline import query_legal, stream_legal_response


def create_session(db: Session, user_id: int, title: str = "Cuộc trò chuyện mới") -> ChatSession:
    session = ChatSession(user_id=user_id, title=title)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_user_sessions(db: Session, user_id: int) -> List[ChatSession]:
    sessions = (
        db.query(ChatSession)
        .filter(ChatSession.user_id == user_id)
        .order_by(ChatSession.updated_at.desc())
        .all()
    )
    for s in sessions:
        s.message_count = len(s.messages)
    return sessions


def get_session_detail(db: Session, session_id: int, user_id: int) -> Optional[ChatSession]:
    session = (
        db.query(ChatSession)
        .filter(ChatSession.id == session_id, ChatSession.user_id == user_id)
        .first()
    )
    return session


def send_message(
    db: Session,
    user_id: int,
    content: str,
    session_id: Optional[int] = None,
    use_personal_docs: bool = False,
) -> dict:
    """Send a message and get AI response."""
    # Get or create session
    if session_id:
        session = db.query(ChatSession).filter(
            ChatSession.id == session_id, ChatSession.user_id == user_id
        ).first()
        if not session:
            session = create_session(db, user_id)
    else:
        session = create_session(db, user_id, title=content[:50])

    # Save user message
    user_msg = ChatMessage(session_id=session.id, role="user", content=content)
    db.add(user_msg)
    db.commit()

    # Build chat history
    history = []
    for msg in session.messages[-6:]:
        history.append({"role": msg.role, "content": msg.content})

    # Determine collection
    collection = f"user_{user_id}" if use_personal_docs else None

    # Query RAG
    result = query_legal(
        question=content,
        collection_name=collection,
        chat_history=history,
    )

    # Save AI response
    ai_msg = ChatMessage(
        session_id=session.id,
        role="assistant",
        content=result["answer"],
        confidence_score=result["confidence"],
        sources=json.dumps(result["sources"], ensure_ascii=False),
    )
    db.add(ai_msg)
    db.commit()
    db.refresh(ai_msg)

    return {
        "session_id": session.id,
        "message": ai_msg,
        "confidence": result["confidence"],
        "sources": result["sources"],
        "warning": result.get("warning"),
    }


def delete_session(db: Session, session_id: int, user_id: int) -> bool:
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id, ChatSession.user_id == user_id
    ).first()
    if not session:
        return False
    db.delete(session)
    db.commit()
    return True
