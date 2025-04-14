# app/repositories/route.py

from sqlalchemy import select, delete
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
        logger.info("Fetching route by Id=%s", id)
        stmt = (
            select(Route)
            .where(Route.id == id)
            .options(selectinload(Route.days))
            .options(selectinload(Route.access_list))
            .options(selectinload(Route.exports))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_share_code(self, share_code: str) -> Optional[Route]:
        """
        Get route by its unique share code.
        """
        logger.info("Fetching route by share_code=%s", share_code)
        stmt = (
            select(Route)
            .where(Route.share_code == share_code)
            .options(selectinload(Route.days))
            .options(selectinload(Route.access_list))
            .options(selectinload(Route.exports))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_owner_id(self, owner_id: int) -> list[Route]:
        """
        Get all routes created by a specific user.
        """
        logger.info("Fetching all routes for owner_id=%s", owner_id)
        stmt = (
            select(Route)
            .where(Route.owner_id == owner_id)
            .options(selectinload(Route.days))
            .options(selectinload(Route.access_list))
            .options(selectinload(Route.exports))
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create(self, obj_in: RouteCreate, commit: bool = True) -> Route:
        """
        Create a new route from the provided dictionary.
        """
        new_route = Route(**obj_in.model_dump(exclude={"days"}))
        self.session.add(new_route)
        await self.session.flush()
        if commit:
            await self.session.commit()
            await self.session.refresh(new_route)
        logger.info("Created new route with id=%s", new_route.id)
        return new_route

    # ================= ROUTE DAY ================= #

    async def create_day(self, route_id: int, day_data: RouteDayCreate) -> RouteDay:
        route = await self.get(route_id)
        if not route:
            message = f"Route {route_id} not found"
            logger.warning(message)
            raise ValueError(message)

        new_day = RouteDay(
            route_id=route_id, **day_data.model_dump(exclude={"activities"})
        )
        self.session.add(new_day)
        await self.session.flush()  # flush to get day.id

        for activity_data in day_data.activities:
            activity = Activity(day_id=new_day.id, **activity_data.model_dump())
            self.session.add(activity)

        await self.session.commit()
        await self.session.refresh(new_day)
        logger.info("Created RouteDay id=%s for route_id=%s", new_day.id, route_id)
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
        logger.info("Fetched %s RouteDays for route_id=%s", len(days), route_id)
        return days

    async def delete_day(self, day_id: int) -> bool:
        """
        Delete a RouteDay by ID.
        """
        stmt = select(RouteDay).where(RouteDay.id == day_id)
        result = await self.session.execute(stmt)
        day = result.scalar_one_or_none()
        if not day:
            return False
        await self.session.delete(day)
        await self.session.commit()
        logger.info("Deleted RouteDay id=%s", day_id)
        return True

    # ================= ACTIVITY ================= #

    # async def create_activity(self, day_id: int, activity_data: ActivityCreate) -> Activity:
    #     """
    #     Create an Activity under a given RouteDay.
    #     """
    #     new_activity = Activity(**activity_data.model_dump(), route_day_id=day_id)
    #     self.session.add(new_activity)
    #     await self.session.commit()
    #     await self.session.refresh(new_activity)
    #     logger.info("Created Activity id=%s for day_id=%s", new_activity.id, day_id)
    #     return new_activity
    #
    # async def get_activities_by_day(self, day_id: int) -> List[Activity]:
    #     """
    #     Get all Activity entries for a given RouteDay.
    #     """
    #     stmt = select(Activity).where(Activity.route_day_id == day_id)
    #     result = await self.session.execute(stmt)
    #     activities = result.scalars().all()
    #     logger.info("Fetched %s Activities for day_id=%s", len(activities), day_id)
    #     return activities
    #
    # async def delete_activity(self, activity_id: int) -> None:
    #     """
    #     Delete an Activity by its ID.
    #     """
    #     stmt = delete(Activity).where(Activity.id == activity_id)
    #     await self.session.execute(stmt)
    #     await self.session.commit()
    #     logger.info("Deleted Activity id=%s", activity_id)
