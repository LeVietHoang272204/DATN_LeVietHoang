import json
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.chat import (
    ChatMessageCreate, ChatMessageResponse,
    ChatSessionResponse, ChatSessionDetail,
)
from app.services import chat_service
from app.ai.rag_pipeline import stream_legal_response
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/chat", tags=["Chat"])


@router.get("/sessions", response_model=list[ChatSessionResponse])
def list_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return chat_service.get_user_sessions(db, current_user.id)


@router.get("/sessions/{session_id}", response_model=ChatSessionDetail)
def get_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = chat_service.get_session_detail(db, session_id, current_user.id)
    if not session:
        raise HTTPException(status_code=404, detail="Không tìm thấy phiên chat")
    return session


@router.post("/send")
def send_message(
    data: ChatMessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    result = chat_service.send_message(
        db=db,
        user_id=current_user.id,
        content=data.content,
        session_id=data.session_id,
        use_personal_docs=data.use_personal_docs,
    )
    return {
        "session_id": result["session_id"],
        "message": ChatMessageResponse.model_validate(result["message"]),
        "confidence": result["confidence"],
        "sources": result["sources"],
        "warning": result.get("warning"),
    }


@router.get("/stream/{session_id}")
def stream_response(
    session_id: int,
    question: str,
    use_personal_docs: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """SSE streaming endpoint for real-time responses."""
    collection = f"user_{current_user.id}" if use_personal_docs else None

    # Get chat history
    session = chat_service.get_session_detail(db, session_id, current_user.id)
    history = []
    if session:
        for msg in session.messages[-6:]:
            history.append({"role": msg.role, "content": msg.content})

    def event_generator():
        for chunk in stream_legal_response(
            question=question,
            collection_name=collection,
            chat_history=history,
        ):
            yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.delete("/sessions/{session_id}")
def delete_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not chat_service.delete_session(db, session_id, current_user.id):
        raise HTTPException(status_code=404, detail="Không tìm thấy phiên chat")
    return {"detail": "Đã xóa phiên chat"}
