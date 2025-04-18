# app/services/crud/route_service.py

import logging
from typing import Optional, List

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
    Service layer for managing Routes, RouteDays, and Activities logic.
    """

    def __init__(self, repo: RouteRepository):
        self.repo = repo

    async def create_route(self, new_data: RouteCreate) -> RouteShort:
        """
        Create a new Route and optionally RouteDays and Activities.
        Performs FK checks on owner_id, ai_cache_id, and last_edited_by (if provided).
        """
        share_code = new_data.share_code.strip()

        logger.info("Route service: creating new Route with code=%s", share_code)

        if await self.repo.get_by_share_code(share_code):
            message = "Route service: Route with code %s already exists"
            logger.warning(message, share_code)
            raise RouteAlreadyExistsError(message % share_code)

        await check_foreign_keys(self, new_data)

        new_route = await self.repo.create(new_data, commit=True)

        # --- Creating route days, if any --- #
        if hasattr(new_data, "days") and new_data.days:
            for day in new_data.days:
                await self.repo.create_day(new_route.id, day)

        logger.info("Route service: Route created with id=%s", new_route.id)
        return await self.repo.get(new_route.id)

    async def list_routes(self) -> List[RouteShort]:
        """
        Return a short list of all routes.
        """
        routes = await self.repo.get_all()
        logger.info("Route service: fetched %s routes", len(routes))
        return routes

    async def get_route_by_id(self, route_id: int) -> RouteRead:
        """
        Get a route by its ID.
        Raises:
            RouteNotFoundError: If route does not exist.
        """
        logger.info("Route service: getting Route by id: %s", route_id)
        route = await self.repo.get(route_id)
        if not route:
            message = "Route service: Route (id=%s) not found"
            logger.warning(message, route_id)
            raise RouteNotFoundError(message % route_id)
        return route

    async def get_route_by_code(self, share_code: str) -> Optional[RouteRead]:
        """
        Get a route by its share_code.
        Raises:
            RouteNotFoundError: If route does not exist.
        """
        share_code = share_code.strip()

        logger.info("Route service: getting Route with code %s", share_code)
        route = await self.repo.get_by_share_code(share_code)
        if not route:
            message = "Route service: Route with code %s not found"
            logger.warning(message, share_code)
            raise RouteNotFoundError(message % share_code)
        return route

    async def get_route_by_owner(self, owner_id: int) -> List[RouteRead]:
        """
        Get all routes owned by a specific user.
        """
        logger.info("Route service: getting routes by owner_id: %s", owner_id)
        return await self.repo.get_by_owner_id(owner_id)

    async def delete_route(self, route_id: int) -> bool:
        """
        Delete a route and all related data.
        Raises:
            RouteNotFoundError: If route does not exist.
        """
        logger.info("Route service: deleting Route with id=%s", route_id)
        route = await self.repo.get(route_id)
        if not route:
            message = "Route service: Route (id=%s) not found"
            logger.warning(message, route_id)
            raise RouteNotFoundError(message % route_id)

        await self.repo.delete(route_id)
        return True

    async def rebuild_route(self, old_route_id: int, new_data: RouteCreate) -> RouteShort:
        """
        Atomically replace an existing route with a new one.
        """
        logger.info("Route service: rebuilding Route with id=%s", old_route_id)

        # check if route exists
        existing = await self.repo.get(old_route_id)
        if not existing:
            message = "Route service: Route (id=%s) not found"
            logger.warning(message, old_route_id)
            raise RouteNotFoundError(message % old_route_id)

        # check if share_code already exists
        share_code = new_data.share_code.strip()
        existing_code = await self.repo.get_by_share_code(share_code)
        if existing_code and existing_code.id != old_route_id:
            message = "Route service: Route with code %s already exists"
            logger.warning(message, share_code)
            raise RouteAlreadyExistsError(message % share_code)
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
        message = "User-owner (id=%s) does not exist"
        logger.warning(message, new_data.owner_id)
        raise InvalidRouteDataError(message % new_data.owner_id)

    if new_data.ai_cache_id is not None:
        from repositories.ai_cache import AICacheRepository

        ai_repo = AICacheRepository(self.session)
        ai_cache = await ai_repo.get(new_data.ai_cache_id)
        if not ai_cache:
            message = "AICache reference (id=%s) does not exist"
            logger.warning(message, new_data.ai_cache_id)
            raise InvalidRouteDataError(message % new_data.ai_cache_id)

    if getattr(new_data, "last_edited_by", None) is not None:
        editor = await user_repo.get(new_data.last_edited_by)
        if not editor:
            message = "Last user-editor (id=%s) does not exist"
            logger.warning(message, new_data.last_edited_by)
            raise InvalidRouteDataError(message % new_data.last_edited_by)
