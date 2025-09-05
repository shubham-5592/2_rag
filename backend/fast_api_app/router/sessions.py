from fast_api_app.dependencies import get_db
from db import models
from schema import schemas
from rag.rag import create_session_name

from fastapi import APIRouter, Depends, HTTPException
from fast_api_app.router.log_decorator import log_response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from sqlalchemy.orm import selectinload


router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.get("/", response_model=list[schemas.SessionOut])
@log_response
async def list_sessions(user_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(models.Session).where(models.Session.user_id == user_id).order_by(models.Session.updated_at.desc())
    res = await db.execute(stmt)
    sessions = res.scalars().all()
    return [schemas.SessionOut(id=s.id, user_id=s.user_id, name=s.name) for s in sessions]


@router.post("/", response_model=schemas.SessionOut)
@log_response
async def create_session(payload: schemas.SessionCreate, db: AsyncSession = Depends(get_db)):
    # Ensure user exists (create lightweight user row if not)
    user = await db.get(models.User, payload.user_id)
    if not user:
        user = models.User(id=payload.user_id)
        db.add(user)
        await db.commit()
    await db.flush()
    session = models.Session(user_id=payload.user_id, name=payload.name or "New Session")
    db.add(session)    
    await db.commit()
    await db.flush()
    # If no explicit name, try to name from first message when available (lazy)
    return schemas.SessionOut(id=session.id, user_id=session.user_id, name=session.name)


# @router.patch("/{session_id}", response_model=schemas.SessionOut)
# async def update_session(session_id: str, payload: schemas.SessionUpdate, db: AsyncSession = Depends(get_db)):
#     session = await db.get(models.Session, session_id)
#     if not session:
#         raise HTTPException(status_code=404, detail="Session not found")
#     if payload.name:
#         session.name = payload.name
#     await db.flush()
#     return schemas.SessionOut(id=session.id, user_id=session.user_id, name=session.name)


@router.delete("/{session_id}")
@log_response
async def delete_session(session_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(models.Session).options(selectinload(models.Session.messages)).where(models.Session.id == session_id)
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    await db.delete(session)    
    await db.commit()
    return {"ok": True}


@router.get("/{session_id}/history", response_model=schemas.HistoryOut)
@log_response
async def get_history(session_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(models.Session).options(selectinload(models.Session.messages)).where(models.Session.id == session_id)
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    messages = [
        schemas.MessageOut(id=m.id, role=m.role, content=m.content,
                           created_at=str(m.created_at))
        for m in session.messages
    ]
    return schemas.HistoryOut(session_id=session.id, messages=messages)


@router.delete("/{session_id}/history")
@log_response
async def delete_history(session_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(models.Session).options(selectinload(models.Session.messages)).where(models.Session.id == session_id)
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    for m in list(session.messages):
        await db.delete(m)
    await db.commit()
    return {"ok": True}