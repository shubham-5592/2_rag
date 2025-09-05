from db.dbo import get_async_session

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession



async def get_db(session: AsyncSession = Depends(get_async_session)):
    return session