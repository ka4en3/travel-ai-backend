# app/repositories/base.py

from typing import Generic, TypeVar, Type
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.base_class import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def get(self, _id: int) -> ModelType | None:
        stmt = select(self.model).where(self.model.id == _id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self) -> list[ModelType]:
        stmt = select(self.model)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def delete(self, _id: int) -> bool:
        obj = await self.get(_id)
        if not obj:
            return False
        await self.session.delete(obj)
        await self.session.commit()
        return True
