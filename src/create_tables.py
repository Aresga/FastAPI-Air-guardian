import asyncio
from src.database import async_engine, Base
from src.model import Violation
import logging

"""
This script handles the creation and dropping of all database tables defined in the SQLAlchemy models.
Functions:
	create_all_tables():
		Asynchronously drops all existing tables and recreates them based on the SQLAlchemy model metadata.
		Logs a message upon successful creation.

Usage:
	Run this script directly to reset and create all tables in the database using the async SQLAlchemy engine.
"""

logging.basicConfig(level=logging.INFO)

async def create_all_tables():
    async with async_engine.begin() as conn:
        # drop all tables (if they exist) before creating new ones
        await conn.run_sync(Base.metadata.drop_all)
        # create the violations tables based on the model class .
        await conn.run_sync(Base.metadata.create_all)
    logging.info("Database tables created successfully.")

if __name__ == "__main__":
    asyncio.run(create_all_tables())