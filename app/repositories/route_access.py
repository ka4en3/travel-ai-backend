# app/repositories/route_access.py

import logging
from sqlalchemy import select, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from models.route_access import RouteAccess
from schemas.route_access import RouteAccessCreate
from repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class RouteAccessRepository(BaseRepository[RouteAccess]):
    """
    Repository for working with RouteAccess model.
    """

    model = RouteAccess

    def __init__(self, session: AsyncSession):
        super().__init__(RouteAccess, session)

    async def get_by_user_and_route(
        self, user_id: int, route_id: int
    ) -> Optional[RouteAccess]:
        """
        Get route access entry by user_id and route_id.
        """
        logger.debug(
            "RouteAccess Repo: Fetching RouteAccess for user_id=%s and route_id=%s",
            user_id,
            route_id,
        )
        stmt = select(RouteAccess).where(
            RouteAccess.user_id == user_id, RouteAccess.route_id == route_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_by_user(self, user_id: int) -> List[RouteAccess]:
        """
        Get all route access entries for a given user.
        """
        logger.debug(
            "RouteAccess Repo: Fetching all RouteAccess for user_id=%s", user_id
        )
        stmt = select(RouteAccess).where(RouteAccess.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_all_by_route(self, route_id: int) -> List[RouteAccess]:
        """
        Get all route access entries for a given route.
        """
        logger.debug(
            "RouteAccess Repo: Fetching all RouteAccess for route_id=%s", route_id
        )
        stmt = select(RouteAccess).where(RouteAccess.route_id == route_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create(self, obj_in: RouteAccessCreate) -> RouteAccess:
        """
        Create a new RouteAccess entry.
        """
        access = RouteAccess(**obj_in.model_dump())
        self.session.add(access)
        try:
            await self.session.commit()
            await self.session.refresh(access)
        except IntegrityError as e:
            logger.debug(
                "RouteAccess Repo: IntegrityError on RouteAccess creation: %s", e
            )
            await self.session.rollback()
            raise

        logger.debug("RouteAccess Repo: Created RouteAccess: %s", access)
        return access

    async def delete_by_user_and_route(self, user_id: int, route_id: int) -> bool:
        """
        Delete RouteAccess entry for given user and route.
        """
        access = await self.get_by_user_and_route(user_id, route_id)
        if not access:
            logger.debug(
                "RouteAccess Repo: RouteAccess not found for user_id=%s, route_id=%s",
                user_id,
                route_id,
            )
            return False
        await self.session.delete(access)
        await self.session.commit()
        logger.debug(
            "RouteAccess Repo: Deleted RouteAccess for user_id=%s, route_id=%s",
            user_id,
            route_id,
        )
        return True
