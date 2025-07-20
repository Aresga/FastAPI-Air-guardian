from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from src.settings import settings

"""
This module sets up the asynchronous SQLAlchemy engine, session maker, and base class for ORM models,
configured for use with FastAPI. It provides:

- An async engine (`async_engine`) connected to the database specified in settings.
- An async session maker (`AsyncSessionLocal`) for creating database sessions.
- A declarative base class (`Base`) for defining ORM models.
- An async dependency function (`get_db`) for FastAPI routes, yielding a database session within a context manager.

Usage:
	Import `Base` to define ORM models.
	Use `get_db` as a dependency in FastAPI endpoints to access the database session.
"""

# Async engine and session (for FastAPI)
async_engine = create_async_engine(settings.DATABASE_URL)
AsyncSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=async_engine)


Base = declarative_base()


# Dependency for FastAPI
## this function is an async generator that provides a database session 

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session ## provide sees to the caller while maintaining session context 