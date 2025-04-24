# app/services/crud/route_service.py

import logging
import math
from typing import Optional, List

from utils.utils import generate_nanoid_code
from constants.roles import RouteRole
from schemas.route import RouteCreate, RouteRead, RouteShort, RouteGenerateRequest, RouteDayCreate
from schemas.route_access import RouteAccessCreate
from repositories import *
from exceptions.route import (
    RouteAlreadyExistsError,
    RouteNotFoundError,
    InvalidRouteDataError,
)
from services.crud.route_access_service import RouteAccessService


logger = logging.getLogger(__name__)


class RouteService:
    """
    Service layer for managing Routes, RouteDays, and Activities logic.
    Throws RouteAlreadyExistsError, RouteNotFoundError, InvalidRouteDataError.
    """

    def __init__(
        self,
        route_repo: RouteRepository,
        user_repo: UserRepository,
        cache_repo: AICacheRepository,
        access_repo: RouteAccessRepository,
    ):
        self.route_repo = route_repo
        self.user_repo = user_repo
        self.cache_repo = cache_repo
        self.access_repo = access_repo

    async def _check_foreign_keys(
        self,
        new_data: RouteCreate,
    ) -> None:
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

    async def _get_new_data(
        self,
        payload: RouteGenerateRequest,
        owner_id: int,
    ) -> RouteCreate:
        result = None

        # first check cache
        cached = await self.cache_repo.find_similar(
            origin=payload.origin.strip().lower(),
            destination=payload.destination.strip().lower(),
            duration_days=payload.duration_days,
            budget=math.ceil(payload.budget),
        )
        if cached:
            logger.info("Cache hit: using cached plan id=%s", cached.id)
            result = cached.result
            cached.hit_count += 1
            # await self.cache_repo.session.commit()
        else:
            pass
            # TODO: no cache -> ask AI
            # try:
            #     result = await self.ai_svc.generate_route(
            #         origin=payload.origin,
            #         destination=payload.destination,
            #         duration_days=payload.duration_days,
            #         interests=payload.interests,
            #         budget=payload.budget,
            #     )
            # except Exception as e:
            #     logger.error("AI generation failed: %s", e)
            #     raise InvalidRouteDataError("Failed to generate route via AI")

            # save new cache
            # cache_entry = AICacheCreate(
            #     origin=payload.origin,
            #     destination=payload.destination,
            #     duration_days=payload.duration_days,
            #     budget=payload.budget,
            #     interests=payload.interests or [],
            #     original_prompt=result.get("original_prompt", ""),
            #     prompt_hash=result.get("prompt_hash", ""),
            #     result=result,
            # )
            # await self.cache_repo.create(cache_entry)

        if result is None:
            raise InvalidRouteDataError("Route service: failed to generate route, no data received from AI")

        # build scheme RouteCreate
        new_data = RouteCreate(
            name=result["name"],
            origin=payload.origin,
            destination=payload.destination,
            duration_days=payload.duration_days,
            budget=payload.budget,
            interests=payload.interests or cached.interests,
            route_data=result,
            days=[RouteDayCreate(**day) for day in result["days"]],
            is_public=payload.is_public,
            ai_cache_id=(cached.id if cached else None),
            share_code=generate_nanoid_code(),
            owner_id=owner_id,
        )

        # COMMENTED OUT: can't be as now use generate_nanoid_code()
        # check if share_code already exists
        # if await self.route_repo.get_by_share_code(new_data.share_code):
        #     message = "Route service: Route (code=%s) already exists"
        #     logger.warning(message, new_data.share_code)
        #     raise RouteAlreadyExistsError(message % new_data.share_code)

        return new_data

    async def create_route(
        self,
        payload: RouteGenerateRequest,
        owner_id: int,
    ) -> RouteShort:
        """
        Create a new Route and optionally RouteDays and Activities.
        Performs FK checks on owner_id, ai_cache_id, and last_edited_by (if provided).
        Raises:
            RouteAlreadyExistsError: If Route with the same share_code already exists.
            InvalidRouteDataError: If Route data is invalid.
        """
        logger.info("Route service: creating new route for %s → %s", payload.origin, payload.destination)

        # build new data
        new_data = await self._get_new_data(payload, owner_id)

        # check foreign keys
        await self._check_foreign_keys(new_data)

        try:
            new_route = await self.route_repo.create(new_data, commit=True)
            # creating route days, if any
            if hasattr(new_data, "days") and new_data.days:
                for day in new_data.days:
                    await self.route_repo.create_day(new_route.id, day, commit=True)

            # add route access
            access_svc = RouteAccessService(access_repo=self.access_repo)
            await access_svc.grant_access(
                RouteAccessCreate(
                    user_id=new_data.owner_id,
                    route_id=new_route.id,
                    role=RouteRole.CREATOR,
                ),
                commit=True,
            )
        except Exception as e:
            message = "Route service: failed to save Route: %s. Check logs for details"
            logger.error(message, e)
            raise InvalidRouteDataError(message % e)

        logger.info(
            "Route service: Route (id=%s, code=%s) created",
            new_route.id,
            new_route.share_code,
        )
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

    async def rebuild_route(
        self,
        old_route_id: int,
        payload: RouteGenerateRequest,
        owner_id: int,
    ) -> RouteShort:
        """
        Throws:
            RouteNotFoundError: If Route does not exist.
            RouteAlreadyExistsError: If Route with the same share_code already exists.
            InvalidRouteDataError: If Route data is invalid.
        """
        logger.info("Route service: rebuilding Route (id=%s)", old_route_id)

        return await self.route_repo.transaction(self._rebuild_route_tx, old_route_id, payload, owner_id)

    async def _rebuild_route_tx(self, old_route_id: int, payload: RouteGenerateRequest, owner_id: int) -> RouteShort:
        # check if route exists
        existing = await self.route_repo.get(old_route_id)
        if not existing:
            message = "Route service: Route (id=%s) not found"
            logger.warning(message, old_route_id)
            raise RouteNotFoundError(message % old_route_id)

        # build new data
        new_data = await self._get_new_data(payload, owner_id)

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
                    await self.route_repo.create_day(new_route.id, day, commit=False)

            # add route access
            access_service = RouteAccessService(access_repo=self.access_repo)
            await access_service.grant_access(
                RouteAccessCreate(
                    user_id=new_data.owner_id,
                    route_id=new_route.id,
                    role=RouteRole.CREATOR,
                ),
                commit=False,
            )
        except Exception as e:
            message = "Route service: Route can't be rebuild: %s. Check logs for details"
            logger.error(message, e)
            raise InvalidRouteDataError(message % e)

        return await self.route_repo.get(new_route.id)
