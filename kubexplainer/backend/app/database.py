from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager
from .models import Base
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./data/app.db")

engine = create_async_engine(DATABASE_URL, echo=False)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@asynccontextmanager
async def get_session():
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()
