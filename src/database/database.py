from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

from src.config import DATABASE_URL


engine = create_async_engine(DATABASE_URL)

SesMaker = async_sessionmaker(
    engine,
    expire_on_commit=False
)

class Base(DeclarativeBase):
    pass

async def get_session():
    async with SesMaker() as session:
        yield session

Session = Annotated[AsyncSession, Depends(get_session)]
