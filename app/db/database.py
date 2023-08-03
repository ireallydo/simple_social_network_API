from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from asyncio import sleep
from db.models import BaseModel
from settings import Settings
from httpx import AsyncClient
from loguru import logger


settings = Settings()

db_con_str = f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}/{settings.DB_NAME}"
logger.debug(f"DB Connection string: {db_con_str }")
engine = create_async_engine(db_con_str, echo=False, pool_pre_ping=True)
SessionLocal = sessionmaker(engine, autocommit=False, autoflush=False, class_=AsyncSession)
session = AsyncClient()


async def init_db():
    await sleep(20)
    async with engine.begin() as connection:
        # logger.debug("Database: dropping all tables")
        # await connection.run_sync(BaseModel.metadata.drop_all)
        logger.debug("Database: creating all tables")
        await connection.run_sync(BaseModel.metadata.create_all)
