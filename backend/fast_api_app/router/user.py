from fast_api_app.dependencies import get_db
from db import models
from schema import schemas

from fastapi import APIRouter, Depends
from fast_api_app.router.log_decorator import log_response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

router = APIRouter(prefix="/user", tags=["user"])

@router.post("/", response_model=schemas.UserOut)
@log_response
async def create_user(payload: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(models.User).where(
            models.User.email == payload.email,
            models.User.username == payload.username
        )
    )
    user = result.scalar_one_or_none()
    if user:
        return schemas.UserOut(id=user.id, email=user.email, username=user.username)
    user = models.User(email=payload.email, username=payload.username)
    db.add(user)
    await db.commit()
    await db.flush()
    return schemas.UserOut(id=user.id, email=user.email, username=user.username)
