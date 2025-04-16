# app/repositories/route.py

from sqlalchemy import select, delete
from sqlalchemy.exc import IntegrityError

from models.route import Route, RouteDay, Activity
from schemas.route import RouteCreate, RouteDayCreate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import Optional, List
import logging
from .base import BaseRepository

logger = logging.getLogger(__name__)


class RouteRepository(BaseRepository[Route]):
    """
    Repository for working with Route model.
    """

    model = Route

    def __init__(self, session: AsyncSession):
        super().__init__(Route, session)

    async def get(self, id: int) -> Optional[Route]:
        """Get route by ID"""
        logger.debug("Route Repo: Fetching Route by Id=%s", id)
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

        if route is None:
            logger.debug("Route Repo: Route with Id=%s not found", id)

        return route

    async def get_by_share_code(self, share_code: str) -> Optional[Route]:
        """
        Get route by its unique share code.
        """
        logger.debug("Route Repo: Fetching Route by share_code=%s", share_code)
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

        if route is None:
            logger.debug("Route Repo: Route with code=%s not found", share_code)

        return route

    async def get_by_owner_id(self, owner_id: int) -> list[Route]:
        """
        Get all routes created by a specific user.
        """
        logger.debug("Route Repo: Fetching all Routes for owner_id=%s", owner_id)
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
        logger.debug(f"Route Repo: creating new Route")

        new_route = Route(**obj_in.model_dump(exclude={"days"}))
        self.session.add(new_route)
        await self.session.flush()
        if commit:
            try:
                await self.session.commit()
                await self.session.refresh(new_route)
                logger.debug(f"Route Repo: Route created with id={new_route.id}")
                return new_route
            except IntegrityError as e:
                logger.debug("Route Repo: IntegrityError on Route creation: %s", e)
                await self.session.rollback()
                raise

        logger.debug("Route Repo: Created new Route with id=%s", new_route.id)
        return new_route

    # ================= ROUTE DAY ================= #

    async def create_day(self, route_id: int, day_data: RouteDayCreate) -> RouteDay:
        route = await self.get(route_id)
        if not route:
            message = f"Route Repo: Route {route_id} not found"
            logger.debug(message)
            raise ValueError(message)

        new_day = RouteDay(
            route_id=route_id, **day_data.model_dump(exclude={"activities"})
        )
        self.session.add(new_day)
        await self.session.flush()  # flush to get day.id

        for activity_data in day_data.activities:
            activity = Activity(day_id=new_day.id, **activity_data.model_dump())
            self.session.add(activity)

        try:
            await self.session.commit()
            await self.session.refresh(new_day)
        except IntegrityError as e:
            logger.debug("Route Repo: IntegrityError on RouteDay creation: %s", e)
            await self.session.rollback()
            raise

        logger.debug(
            "Route Repo: Created RouteDay id=%s for route_id=%s", new_day.id, route_id
        )
        return new_day

    async def get_days_by_route(self, route_id: int) -> List[RouteDay]:
        """
        Get all RouteDay entries for a given route with activities.
        """
        stmt = (
            select(RouteDay)
            .where(RouteDay.route_id == route_id)
            .options(selectinload(RouteDay.activities))
        )
        result = await self.session.execute(stmt)
        days = result.scalars().all()
        logger.debug(
            "Route Repo: Fetched %s RouteDays for route_id=%s", len(days), route_id
        )
        return days

    async def delete_day(self, day_id: int) -> bool:
        """
        Delete a RouteDay by ID.
        """
        stmt = select(RouteDay).where(RouteDay.id == day_id)
        result = await self.session.execute(stmt)
        day = result.scalar_one_or_none()
        if not day:
            logger.debug("Route Repo: RouteDay with Id=%s not found", day_id)
            return False
        await self.session.delete(day)
        await self.session.commit()
        logger.debug("Route Repo: Deleted RouteDay id=%s", day_id)
        return True
