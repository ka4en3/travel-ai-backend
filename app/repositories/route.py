# app/repositories/route.py

import logging
from typing import Optional, List
from typing import Callable, Awaitable, TypeVar

from sqlalchemy import select, delete
from sqlalchemy.exc import IntegrityError

from models.route import Route, RouteDay, Activity
from schemas.route import RouteCreate, RouteDayCreate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .base import BaseRepository

logger = logging.getLogger(__name__)


class RouteRepository(BaseRepository[Route]):
    """
    Repository for working with Route, RouteDay, and Activity models.
    Throws IntegrityError if user already exists.
    Throws Exception in case of other exceptions.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(Route, session)

    T = TypeVar("T")

    async def transaction(self, func: Callable[..., Awaitable[T]], *args, **kwargs) -> T:
        """
        Execute actions in one transaction.
        """
        async with self.session.begin():
            result = await func(*args, **kwargs)
            return result

    async def get(self, id: int) -> Optional[Route]:
        """Get route by ID"""
        logger.debug("Route repo: fetching Route (id=%s)", id)
        stmt = (
            select(Route)
            .where(Route.id == id)
            .options(
                selectinload(Route.days).selectinload(RouteDay.activities),
                selectinload(Route.access_list),
                selectinload(Route.exports),
            )
        )
        result = await self.session.execute(stmt)
        route = result.scalar_one_or_none()
        return route

    async def get_by_share_code(self, share_code: str) -> Optional[Route]:
        """
        Get route by its unique share code.
        """
        logger.debug("Route repo: fetching Route (share_code=%s)", share_code)
        stmt = (
            select(Route)
            .where(Route.share_code == share_code)
            .options(
                selectinload(Route.days).selectinload(RouteDay.activities),
                selectinload(Route.access_list),
                selectinload(Route.exports),
            )
        )
        result = await self.session.execute(stmt)
        route = result.scalar_one_or_none()
        return route

    async def get_by_owner_id(self, owner_id: int) -> list[Route]:
        """
        Get all routes created by a specific user.
        """
        logger.debug("Route repo: fetching all Routes (owner_id=%s)", owner_id)
        stmt = (
            select(Route)
            .where(Route.owner_id == owner_id)
            .options(
                selectinload(Route.days).selectinload(RouteDay.activities),
                selectinload(Route.access_list),
                selectinload(Route.exports),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create(self, obj_in: RouteCreate, commit: bool = True) -> Route:
        """
        Create a new route from the provided dictionary.
        """
        logger.debug("Route repo: creating new Route")
        new_route = Route(**obj_in.model_dump(exclude={"days"}))
        self.session.add(new_route)
        await self.session.flush()
        if commit:
            try:
                await self.session.commit()
                await self.session.refresh(new_route)
                logger.debug("Route repo: Route (id=%s) created", new_route.id)
                return new_route
            except IntegrityError as e:
                logger.debug("Route repo: IntegrityError on Route creation: %s", e)
                await self.session.rollback()
                raise
            except Exception as e:
                logger.debug("Route repo: error: %s", e)
                await self.session.rollback()
                raise
        logger.debug("Route repo: created new Route (id=%s)", new_route.id)
        return new_route

    # ================= ROUTE DAY ================= #

    async def create_day(self, route_id: int, day_data: RouteDayCreate) -> RouteDay:
        # redundantly?
        # route = await self.get(route_id)
        # if not route:
        #     message = "Route Repo: Route (route_id=%s) not found"
        #     logger.debug(message, route_id)
        #     raise ValueError(message % route_id)

        new_day = RouteDay(route_id=route_id, **day_data.model_dump(exclude={"activities"}))
        self.session.add(new_day)
        await self.session.flush()  # flush to get day.id

        for activity_data in day_data.activities:
            activity = Activity(day_id=new_day.id, **activity_data.model_dump())
            self.session.add(activity)

        try:
            await self.session.commit()
            await self.session.refresh(new_day)
        except IntegrityError as e:
            logger.debug("Route repo: IntegrityError on RouteDay creation: %s", e)
            await self.session.rollback()
            raise
        except Exception as e:
            logger.debug("Route repo: error: %s", e)
            await self.session.rollback()
            raise

        logger.debug("Route repo: created RouteDay (id=%s) for Route (id=%s)", new_day.id, route_id)
        return new_day

    async def get_days_by_route(self, route_id: int) -> List[RouteDay]:
        """
        Get all RouteDay entries for a given route with activities.
        """
        stmt = select(RouteDay).where(RouteDay.route_id == route_id).options(selectinload(RouteDay.activities))
        result = await self.session.execute(stmt)
        days = result.scalars().all()
        logger.debug("Route repo: fetched %s RouteDays for Route (id=%s)", len(days), route_id)
        return days

    # Days are deleted automatically when the route is deleted !
    # async def delete_day(self, day_id: int) -> bool:
    #     """
    #     Delete a RouteDay by ID.
    #     """
    #     stmt = select(RouteDay).where(RouteDay.id == day_id)
    #     result = await self.session.execute(stmt)
    #     day = result.scalar_one_or_none()
    #     if not day:
    #         logger.debug("Route repo: RouteDay with id=%s not found", day_id)
    #         return False
    #     await self.session.delete(day)
    #     await self.session.commit()
    #     logger.debug("Route repo: deleted RouteDay id=%s, day_id)
    #     return True
