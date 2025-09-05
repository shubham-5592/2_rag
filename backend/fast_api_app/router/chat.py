from fast_api_app.dependencies import get_db
from db import models
from schema import schemas
from rag.rag import create_session_name, run_rag

from fastapi import APIRouter, Depends, HTTPException
from fast_api_app.router.log_decorator import log_response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/", response_model=schemas.ChatResponse)
@log_response
async def chat(payload: schemas.ChatRequest, db: AsyncSession = Depends(get_db)):
    stmt = select(models.Session).options(selectinload(models.Session.messages)).where(models.Session.id == payload.session_id)
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()
    if not session or session.user_id != payload.user_id:
        raise HTTPException(status_code=404, detail="Session not found for user")
    # Build chat history for LLM from stored messages
    history = [(m.role, m.content) for m in session.messages]
    # Run RAG
    answer, sources = await run_rag(payload.query, history)
    # Persist both user question and assistant answer
    user_msg = models.Message(session_id=session.id, role="user", content=payload.query)
    asst_msg = models.Message(session_id=session.id, role="assistant", content=answer)
    db.add_all([user_msg, asst_msg])
    # If session still has default name, try to auto-name from first messages
    if session.name in ("New Session", "") and len(session.messages) > 3:
        try:
            session.name = create_session_name([user_msg, asst_msg] + list(session.messages))
        except Exception:
            pass
        await db.flush()
    sources = [schemas.SourceItem(**src) for src in sources]
    return schemas.ChatResponse(answer=answer, sources=sources, session_id=session.id)