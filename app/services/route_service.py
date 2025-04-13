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

    async def create_route(self, route_data: RouteCreate) -> RouteRead:
        """
        Create a new Route and optionally RouteDays and Activities.
        Performs FK checks on owner_id, ai_cache_id, and last_edited_by (if provided).
        """
        logger.info("Creating new route with share_code=%s", route_data.share_code)

        if await self.repo.get_by_share_code(route_data.share_code):
            logger.warning("Route with share_code '%s' already exists", route_data.share_code)
            raise RouteAlreadyExistsError(route_data.share_code)

        # --- Verification of owner existence (mandatory) --- #
        user_repo = UserRepository(self.session)
        owner = await user_repo.get(route_data.owner_id)
        if not owner:
            raise InvalidRouteDataError(f"User with id={route_data.owner_id} does not exist")

        # --- Checking the existence of ai_cache (if specified) --- #
        if route_data.ai_cache_id is not None:
            from repositories.ai_cache import AICacheRepository

            ai_repo = AICacheRepository(self.session)
            ai_cache = await ai_repo.get(route_data.ai_cache_id)
            if not ai_cache:
                raise InvalidRouteDataError(f"AICache with id={route_data.ai_cache_id} does not exist")

        # --- Checking the existence of last_edited_by (if specified) --- #
        if getattr(route_data, "last_edited_by", None) is not None:
            editor = await user_repo.get(route_data.last_edited_by)
            if not editor:
                raise InvalidRouteDataError(f"User with id={route_data.last_edited_by} does not exist")

        route = await self.repo.create(route_data)

        # --- Creating route days, if any --- #
        if hasattr(route_data, "days") and route_data.days:
            for day in route_data.days:
                await self.repo.create_day(route.id, day)

        logger.info("Route created with id=%s", route.id)
        return await self.repo.get(route.id)

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
            logger.warning(f"Route with id '{route_id}' not found")
            raise RouteNotFoundError()
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
            logger.warning(f"Route with '{code}' not found")
            raise RouteNotFoundError()
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
        success = await self.repo.delete(route_id)
        if not success:
            logger.warning(f"Route with id '{route_id}' not found")
            raise RouteNotFoundError(route_id)
        return success

    async def rebuild_route(self, route_id: int, new_data: RouteCreate) -> RouteRead:
        """
        Replace an existing route with a new one.
        """
        logger.info("Rebuilding route with id=%s", route_id)
        await self.delete_route(route_id)
        return await self.create_route(new_data)
