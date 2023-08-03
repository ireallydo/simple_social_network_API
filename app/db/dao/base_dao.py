from typing import TypeVar, Generic, Type, NoReturn, List
from pydantic import BaseModel as BaseSchema
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import BaseModel
from db.database import SessionLocal, engine
from loguru import logger


DBModelType = TypeVar("DBModelType", bound=BaseModel)
CreateDTOType = TypeVar("CreateDTOType", bound=BaseSchema)
UpdateDTOType = TypeVar("UpdateDTOType", bound=BaseSchema)
DeleteDTOType = TypeVar("DeleteDTOType", bound=BaseSchema)


class BaseDAO(Generic[DBModelType, CreateDTOType, UpdateDTOType, DeleteDTOType]):
    def __init__(self, model: Type[DBModelType],
                 session_generator: Type[AsyncSession] = SessionLocal):
        self._model = model
        self._session_generator = session_generator

    async def create(self, input_data: CreateDTOType) -> DBModelType:
        logger.info(f"{self._model.__name__} DAO: Create db entry")
        logger.trace(f"{self._model.__name__} DAO: Data passed for creation: {input_data}")
        if isinstance(input_data, dict):
            new_line = input_data
        else:
            new_line = input_data.dict()
        db_model = self._model(**new_line)
        async with self._session_generator() as session:
            session.add(db_model)
            await session.commit()
            await session.refresh(db_model)
        logger.debug(f"{self._model.__name__} DAO: Create entry in database: {db_model}")
        return db_model

    async def get_by(self, **kwargs) -> DBModelType:
        logger.info(f"{self._model.__name__} DAO: Get db entry by parameters")
        logger.trace(
            f"{self._model.__name__} DAO: Data passed to filter: params: {kwargs}")
        async with self._session_generator() as session:
            resp = await session.execute(select(self._model).filter_by(**kwargs))
            resp = resp.scalar()
            logger.debug(f"{self._model.__name__} DAO: received a response from the database")
            return resp

    async def get_all_by(self, limit: int, offset: int, **kwargs) -> List[DBModelType]:
        logger.info(f"{self._model.__name__} DAO: Get all db entries by parameters")
        logger.info(
            f"{self._model.__name__} DAO: Data passed to filter: limit: {limit}, offset: {offset}, parameters: {kwargs}")
        async with self._session_generator() as session:
            result = await session.execute(select(self._model).filter_by(**kwargs).offset(offset).limit(limit))
            resp = [raw[0] for raw in result]
            logger.debug(f"{self._model.__name__} DAO: received a response from the database")
            return resp

    async def get_by_id(self, item_id) -> DBModelType:
        logger.info(f"{self._model.__name__} DAO: Get db entry by id: {item_id}")
        async with self._session_generator() as session:
            resp = await session.get(self._model, item_id)
            logger.debug(f"{self._model.__name__} DAO: received a response from the database")
            return resp

    async def patch(self, patch_data, item_id) -> DBModelType:
        logger.info(f"{self._model.__name__} DAO: Update db entry")
        logger.trace(
            f"{self._model.__name__} DAO: Data passed for update: item_id: {item_id}, patch_data: {patch_data}")
        async with self._session_generator() as session:
            if isinstance(patch_data, dict):
                pushed_data = patch_data
            else:
                pushed_data = patch_data.dict(exclude_unset=True)
            await session.execute(update(self._model).
                                  where(self._model.id == item_id).
                                  values(pushed_data))
            await session.commit()
            resp = await session.get(self._model, item_id)
            logger.debug(f"{self._model.__name__} DAO: Received updated entry from the database")
            return resp

    async def delete(self, item_id: str) -> NoReturn:
        async with self._session_generator() as session:
            await session.execute(delete(self._model).
                                  where(self._model.id == item_id))
            await session.commit()

