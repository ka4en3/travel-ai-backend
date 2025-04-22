# app/services/crud/route_access_service.py

import logging
from typing import Optional, List

from constants.roles import RouteRole
from schemas.route_access import RouteAccessCreate
from repositories.route_access import RouteAccessRepository
from exceptions.route_access import (
    RouteAccessAlreadyExistsError,
    RouteAccessNotFoundError,
)

logger = logging.getLogger(__name__)


class RouteAccessService:
    """
    Service layer for managing RouteAccess logic.
    """

    def __init__(self, repo: RouteAccessRepository):
        self.repo = repo

    async def grant_access(self, data: RouteAccessCreate, commit: bool = True) -> None:
        """
        Grant access to a user for a route.
        Raises:
            RouteAccessAlreadyExistsError: If access already exists.
        """
        existing = await self.repo.get_by_user_and_route(data.user_id, data.route_id)
        if existing:
            message = "Route access service: RouteAccess (user_id=%s, route_id=%s) already exists"
            logger.warning(message, data.user_id, data.route_id)
            raise RouteAccessAlreadyExistsError(message % (data.user_id, data.route_id))
        await self.repo.create(data, commit)
        logger.info(
            "Route access service: granted %s access to user_id=%s for route_id=%s",
            data.role,
            data.user_id,
            data.route_id,
        )

    async def grant_editor_access(self, route_id: int, user_id: int) -> None:
        """
        Grant 'EDITOR' role access to a user for the given route.
        """
        # from schemas.route_access import RouteAccessCreate  # avoid circular import

        access_data = RouteAccessCreate(
            user_id=user_id,
            route_id=route_id,
            role=RouteRole.EDITOR,
        )
        await self.grant_access(access_data)

    async def revoke_access(self, user_id: int, route_id: int) -> None:
        """
        Revoke access to a user for a route.
        Raises:
            RouteAccessNotFoundError: If no access exists.
        """
        existing = await self.repo.get_by_user_and_route(user_id, route_id)
        if not existing:
            message = "Route access service: RouteAccess not found for user_id=%s and route_id=%s"
            logger.warning(message, user_id, route_id)
            raise RouteAccessNotFoundError(message % (user_id, route_id))
        await self.repo.delete_by_user_and_route(user_id, route_id)
        logger.info("Route access service: revoked access for user_id=%s for route_id=%s", user_id, route_id)

    async def check_user_has_access(self, user_id: int, route_id: int, required_roles: List[RouteRole]) -> bool:
        """
        Check if a user has one of the required roles for the route.
        Returns:
            True if access exists and role is acceptable.
        Raises:
            RouteAccessNotFoundError If no access exists.
        """
        access = await self.repo.get_by_user_and_route(user_id, route_id)
        if not access:
            message = "Route access service: Route access not found for user_id=%s and route_id=%s"
            logger.warning(message, user_id, route_id)
            raise RouteAccessNotFoundError(message % (user_id, route_id))
        if access.role not in required_roles:
            logger.warning(
                "Route access service: user_id=%s has insufficient role %s for route_id=%s. Required: %s",
                user_id,
                access.role,
                route_id,
                repr(required_roles),
            )
            return False
        return True

    async def list_access_for_user(self, user_id: int) -> List[int]:
        """
        Return a list of route IDs accessible by a given user.
        """
        access_list = await self.repo.get_all_by_user(user_id)
        return [a.route_id for a in access_list]

    async def list_users_with_access(self, route_id: int) -> List[int]:
        """
        Return a list of user IDs that have access to a given route.
        """
        access_list = await self.repo.get_all_by_route(route_id)
        return [a.user_id for a in access_list]
