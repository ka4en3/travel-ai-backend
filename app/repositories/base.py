# app/repositories/base.py

import logging
from typing import Generic, TypeVar, Type
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.base_class import Base

logger = logging.getLogger(__name__)

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Basic repository with common CRUD operations:
    - get(id)
    - get_all()
    - delete(id)
    """

    def __init__(self, model: Type[ModelType], session: AsyncSession):
        """
        :param model: SQLAlchemy model
        :param session: asynchronous session SQLAlchemy
        """
        self.model = model
        self.session = session

    async def get(self, id: int) -> ModelType | None:
        """Get object by ID"""
        logger.debug(f"Fetching {self.model.__name__} with id={id}")
        stmt = select(self.model).where(self.model.id == id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self) -> list[ModelType]:
        """Get all objects in the model"""
        logger.debug(f"Fetching all records of {self.model.__name__}")
        stmt = select(self.model)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def delete(self, id: int) -> bool:
        """Delete object by ID"""
        logger.info(f"Attempting to delete {self.model.__name__} with id={id}")
        obj = await self.get(id)
        if not obj:
            logger.warning(f"{self.model.__name__} with id={id} not found")
            return False
        await self.session.delete(obj)
        await self.session.commit()
        logger.info(f"{self.model.__name__} with id={id} deleted")
        return True
