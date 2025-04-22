# app/repositories/route_access.py

import logging

from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from models.route_access import RouteAccess
from schemas.route_access import RouteAccessCreate
from repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class RouteAccessRepository(BaseRepository[RouteAccess]):
    """
    Repository for working with RouteAccess model.
    Throws IntegrityError if user already exists.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(RouteAccess, session)

    async def get_by_user_and_route(self, user_id: int, route_id: int) -> Optional[RouteAccess]:
        """
        Get route access entry by user_id and route_id.
        """
        logger.debug("Route access repo: fetching RouteAccess (user_id=%s, route_id=%s)", user_id, route_id)
        stmt = select(RouteAccess).where(RouteAccess.user_id == user_id, RouteAccess.route_id == route_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_by_user(self, user_id: int) -> List[RouteAccess]:
        """
        Get all route access entries for a given user.
        """
        logger.debug("Route access repo: fetching all RouteAccess (user_id=%s)", user_id)
        stmt = select(RouteAccess).where(RouteAccess.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_all_by_route(self, route_id: int) -> List[RouteAccess]:
        """
        Get all route access entries for a given route.
        """
        logger.debug("Route access repo: fetching all RouteAccess (route_id=%s)", route_id)
        stmt = select(RouteAccess).where(RouteAccess.route_id == route_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create(self, obj_in: RouteAccessCreate, commit: bool = True) -> RouteAccess:
        """
        Create a new RouteAccess entry.
        """
        new_access = RouteAccess(**obj_in.model_dump())
        self.session.add(new_access)
        if commit:  # in case commit=False all exceptions are caught in the service layer
            try:
                await self.session.commit()
                await self.session.refresh(new_access)
            except IntegrityError as e:
                logger.debug("Route access repo: IntegrityError on RouteAccess creation: %s", e)
                await self.session.rollback()
                raise

        logger.debug(
            "Route access repo: created RouteAccess (id=%s)", new_access.id
        )  # in case commit=False still needs to be logged
        return new_access

    async def delete_by_user_and_route(self, user_id: int, route_id: int) -> bool:
        """
        Delete RouteAccess entry for given user and route.
        """
        delete_access = await self.get_by_user_and_route(user_id, route_id)
        if not delete_access:
            logger.debug("Route access repo: RouteAccess (user_id=%s, route_id=%s) not found", user_id, route_id)
            return False
        await self.session.delete(delete_access)
        await self.session.commit()
        logger.debug("Route access repo: deleted RouteAccess (user_id=%s, route_id=%s)", user_id, route_id)
        return True
