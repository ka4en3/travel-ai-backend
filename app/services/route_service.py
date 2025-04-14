# app/services/route_service.py

import logging
from typing import Optional, List

from sqlalchemy.ext.asyncio import AsyncSession

from schemas.route import RouteCreate, RouteRead, RouteShort
from repositories.route import RouteRepository
from exceptions.route import (
    RouteAlreadyExistsError,
    RouteNotFoundError,
    InvalidRouteDataError,
)
from repositories.user import UserRepository

logger = logging.getLogger(__name__)


class RouteService:
    """
    Service layer for managing Routes, RouteDays, and Activities.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = RouteRepository(session)

    async def create_route(self, new_data: RouteCreate) -> RouteShort:
        """
        Create a new Route and optionally RouteDays and Activities.
        Performs FK checks on owner_id, ai_cache_id, and last_edited_by (if provided).
        """
        logger.info("Creating new route with share_code=%s", new_data.share_code)

        if await self.repo.get_by_share_code(new_data.share_code):
            message = f"Route with code '{new_data.share_code}' already exists"
            logger.warning(message)
            raise RouteAlreadyExistsError(message)

        await check_foreign_keys(self, new_data)

        new_route = await self.repo.create(new_data, commit=True)

        # --- Creating route days, if any --- #
        if hasattr(new_data, "days") and new_data.days:
            for day in new_data.days:
                await self.repo.create_day(new_route.id, day)

        logger.info("Route created with id=%s", new_route.id)
        return await self.repo.get(new_route.id)

    async def list_routes(self) -> List[RouteShort]:
        """
        Return a short list of all routes.
        """
        routes = await self.repo.get_all()
        logger.info("Fetched %d routes", len(routes))
        return routes

    async def get_route_by_id(self, route_id: int) -> RouteRead:
        """
        Get a route by its ID.
        Raises:
            RouteNotFoundError: If route does not exist.
        """
        logger.info("Getting route by ID: %s", route_id)
        route = await self.repo.get(route_id)
        if not route:
            message = f"Route (id={route_id}) not found"
            logger.warning(message)
            raise RouteNotFoundError(message)
        return route

    async def get_route_by_code(self, code: str) -> Optional[RouteRead]:
        """
        Get a route by its share_code.
        Raises:
            RouteNotFoundError: If route does not exist.
        """
        logger.info("Getting route by share_code: %s", code)
        route = await self.repo.get_by_share_code(code)
        if not route:
            message = f"Route with code '{code}' not found"
            logger.warning(message)
            raise RouteNotFoundError(message)
        return route

    async def get_route_by_owner(self, owner_id: int) -> List[RouteRead]:
        """
        Get all routes owned by a specific user.
        """
        logger.info("Getting routes by owner_id: %s", owner_id)
        return await self.repo.get_by_owner_id(owner_id)

    async def delete_route(self, route_id: int) -> bool:
        """
        Delete a route and all related data.
        Raises:
            RouteNotFoundError: If route does not exist.
        """
        logger.info("Deleting route with id=%s", route_id)
        route = await self.repo.get(route_id)
        if not route:
            message = f"Route (id={route_id}) not found"
            logger.warning(message)
            raise RouteNotFoundError(message)

        await self.repo.delete(route_id)
        return True

    async def rebuild_route(
        self, old_route_id: int, new_data: RouteCreate
    ) -> RouteShort:
        """
        Atomically replace an existing route with a new one.
        """
        logger.info("Rebuilding route with id=%s", old_route_id)

        # async with self.session.begin():  # open transaction
        # check if route exists
        existing = await self.repo.get(old_route_id)
        if not existing:
            message = f"Route (id={old_route_id}) not found"
            logger.warning(message)
            raise RouteNotFoundError(message)

        # check if share_code already exists
        existing_code = await self.repo.get_by_share_code(new_data.share_code)
        if existing_code and existing_code.id != old_route_id:
            message = f"Route with code '{new_data.share_code}' already exists"
            logger.warning(message)
            raise RouteAlreadyExistsError(message)
        # check foreign keys
        await check_foreign_keys(self, new_data)

        # delete existing route
        await self.repo.delete(old_route_id, commit=True)

        # create new route
        new_route = await self.repo.create(new_data, commit=True)
        # creating route days, if any
        if hasattr(new_data, "days") and new_data.days:
            for day in new_data.days:
                await self.repo.create_day(new_route.id, day)

        return await self.repo.get(new_route.id)


async def check_foreign_keys(self, new_data: RouteCreate) -> None:
    user_repo = UserRepository(self.session)
    owner = await user_repo.get(new_data.owner_id)
    if not owner:
        message = f"User-owner (id={new_data.owner_id}) does not exist"
        logger.warning(message)
        raise InvalidRouteDataError(message)

    if new_data.ai_cache_id is not None:
        from repositories.ai_cache import AICacheRepository

        ai_repo = AICacheRepository(self.session)
        ai_cache = await ai_repo.get(new_data.ai_cache_id)
        if not ai_cache:
            message = f"AICache reference (id={new_data.ai_cache_id}) does not exist"
            logger.warning(message)
            raise InvalidRouteDataError(message)

    if getattr(new_data, "last_edited_by", None) is not None:
        editor = await user_repo.get(new_data.last_edited_by)
        if not editor:
            message = f"Last user-editor (id={new_data.last_edited_by}) does not exist"
            logger.warning(message)
            raise InvalidRouteDataError(message)
