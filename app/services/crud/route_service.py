# app/services/crud/route_service.py

import logging
from typing import Optional, List

from schemas.route import RouteCreate, RouteRead, RouteShort
from repositories.route import RouteRepository
from repositories.user import UserRepository
from repositories.ai_cache import AICacheRepository
from exceptions.route import (
    RouteAlreadyExistsError,
    RouteNotFoundError,
    InvalidRouteDataError,
)

logger = logging.getLogger(__name__)


class RouteService:
    """
    Service layer for managing Routes, RouteDays, and Activities logic.
    Throws RouteAlreadyExistsError, RouteNotFoundError, InvalidRouteDataError.
    """

    def __init__(self, route_repo: RouteRepository, user_repo: UserRepository, cache_repo: AICacheRepository):
        self.route_repo = route_repo
        self.user_repo = user_repo
        self.cache_repo = cache_repo

    async def _check_foreign_keys(self, new_data: RouteCreate) -> None:
        """
        Validate all foreign key references in the RouteCreate schema.

        Raises:
            InvalidRouteDataError: if any FK points to a non-existent object.
        """
        user_repo = self.user_repo
        cache_repo = self.cache_repo
        owner = await user_repo.get(new_data.owner_id)
        if not owner:
            message = "Owner (user_id=%s) does not exist"
            logger.warning(message, new_data.owner_id)
            raise InvalidRouteDataError(message % new_data.owner_id)

        if new_data.ai_cache_id is not None:
            ai_cache = await cache_repo.get(new_data.ai_cache_id)
            if not ai_cache:
                message = "AICache reference (id=%s) does not exist"
                logger.warning(message, new_data.ai_cache_id)
                raise InvalidRouteDataError(message % new_data.ai_cache_id)

        if getattr(new_data, "last_edited_by", None) is not None:
            editor = await user_repo.get(new_data.last_edited_by)
            if not editor:
                message = "Last editor (user_id=%s) does not exist"
                logger.warning(message, new_data.last_edited_by)
                raise InvalidRouteDataError(message % new_data.last_edited_by)

    async def create_route(self, new_data: RouteCreate) -> RouteShort:
        """
        Create a new Route and optionally RouteDays and Activities.
        Performs FK checks on owner_id, ai_cache_id, and last_edited_by (if provided).
        Raises:
            RouteAlreadyExistsError: If Route with the same share_code already exists.
            InvalidRouteDataError: If Route data is invalid.
        """
        logger.info("Route service: creating new Route")

        # check if share_code already exists
        share_code = new_data.share_code.strip()
        if await self.route_repo.get_by_share_code(share_code):
            message = "Route service: Route (code=%s) already exists"
            logger.warning(message, share_code)
            raise RouteAlreadyExistsError(message % share_code)
        # check foreign keys
        await self._check_foreign_keys(new_data)

        try:
            new_route = await self.route_repo.create(new_data, commit=True)
            # creating route days, if any
            if hasattr(new_data, "days") and new_data.days:
                for day in new_data.days:
                    await self.route_repo.create_day(new_route.id, day)
        except Exception as e:
            message = "Route service: Route can't be created: %s. Check logs for details"
            logger.warning(message, e)
            raise InvalidRouteDataError(message % e)

        logger.info("Route service: Route (id=%s, code=%s) created", new_route.id, share_code)
        return await self.route_repo.get(new_route.id)

    async def list_routes(self) -> List[RouteShort]:
        """
        Return a short list of all routes.
        """
        routes = await self.route_repo.get_all()
        logger.info("Route service: fetched %s Routes", len(routes))
        return routes

    async def get_route_by_id(self, route_id: int) -> RouteRead:
        """
        Get a route by its ID.
        Raises:
            RouteNotFoundError: If route does not exist.
        """
        logger.info("Route service: getting Route (id=%s)", route_id)
        route = await self.route_repo.get(route_id)
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

        logger.info("Route service: getting Route (code=%s)", share_code)
        route = await self.route_repo.get_by_share_code(share_code)
        if not route:
            message = "Route service: Route (code=%s) not found"
            logger.warning(message, share_code)
            raise RouteNotFoundError(message % share_code)
        return route

    async def get_route_by_owner(self, owner_id: int) -> List[RouteRead]:
        """
        Get all routes owned by a specific user.
        """
        logger.info("Route service: getting Routes by owner_id=%s", owner_id)
        return await self.route_repo.get_by_owner_id(owner_id)

    async def delete_route(self, route_id: int) -> bool:
        """
        Delete a route and all related data.
        """
        logger.info("Route service: deleting Route (id=%s)", route_id)
        await self.get_route_by_id(route_id)
        await self.route_repo.delete(route_id)
        return True

    async def rebuild_route(self, old_route_id: int, new_data: RouteCreate) -> RouteShort:
        """
        Throws:
            RouteNotFoundError: If Route does not exist.
            RouteAlreadyExistsError: If Route with the same share_code already exists.
            InvalidRouteDataError: If Route data is invalid.
        """
        logger.info("Route service: rebuilding Route (id=%s)", old_route_id)

        return await self.route_repo.transaction(self._rebuild_route_tx, old_route_id, new_data)

    async def _rebuild_route_tx(self, old_route_id: int, new_data: RouteCreate) -> RouteShort:
        # check if route exists
        existing = await self.route_repo.get(old_route_id)
        if not existing:
            message = "Route service: Route (id=%s) not found"
            logger.warning(message, old_route_id)
            raise RouteNotFoundError(message % old_route_id)
        # check if share_code already exists
        share_code = new_data.share_code.strip()
        existing_code = await self.route_repo.get_by_share_code(share_code)
        if existing_code:
            message = "Route service: Route (code=%s) already exists"
            logger.warning(message, share_code)
            raise RouteAlreadyExistsError(message % share_code)
        # check foreign keys
        await self._check_foreign_keys(new_data)

        try:
            # delete existing route
            await self.route_repo.delete(old_route_id, commit=False)
            # create new route
            new_route = await self.route_repo.create(new_data, commit=False)
            # creating route days, if any
            if hasattr(new_data, "days") and new_data.days:
                for day in new_data.days:
                    await self.route_repo.create_day(new_route.id, day)
        except Exception as e:
            message = "Route service: Route can't be rebuild: %s. Check logs for details"
            logger.warning(message, e)
            raise InvalidRouteDataError(message % e)

        return await self.route_repo.get(new_route.id)
