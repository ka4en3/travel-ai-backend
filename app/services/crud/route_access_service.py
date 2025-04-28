# app/services/crud/route_access_service.py

import logging
from typing import Optional, List

from constants.roles import RouteRole
from models.route_access import RouteAccess
from schemas.route_access import RouteAccessCreate
from repositories.route_access import RouteAccessRepository
from repositories.route import RouteRepository
from exceptions.route_access import (
    RouteAccessAlreadyExistsError,
    RouteAccessNotFoundError,
)
from exceptions.route import (
    RouteNotFoundError,
    PermissionDeniedError,
)

logger = logging.getLogger(__name__)


class RouteAccessService:
    """
    Service layer for managing RouteAccess logic.
    """

    def __init__(
        self,
        access_repo: RouteAccessRepository,
        route_repo: RouteRepository = None,
    ):
        self.access_repo = access_repo
        self.route_repo = route_repo

    async def _ensure_route_exists(self, route_id: int):
        route = await self.route_repo.get(route_id)
        if not route:
            msg = "Route access service: Route (id=%s) not found"
            logger.warning(msg, route_id)
            raise RouteNotFoundError(msg % route_id)
        return route

    async def _ensure_has_role(
        self,
        user_id: int,
        route_id: int,
        allowed: List[RouteRole],
        action: str = "",
    ) -> bool:
        for role in allowed:
            access = await self.access_repo.get_by_user_and_route_and_role(user_id, route_id, role)
            if access:
                return True
        # User has no access
        msg = "Route access service: User (id=%s) has no %s access to route (id=%s)"
        logger.warning(msg, user_id, role, route_id)
        raise PermissionDeniedError(msg % (user_id, role, route_id))

    async def check_user_has_access(self, user_id: int, route_id: int, required_roles: List[RouteRole]) -> bool:
        return await self._ensure_has_role(user_id, route_id, required_roles, action="access route")

    async def get_share_code(self, user_id: int, route_id: int) -> str:
        """
        Return share_code for a route if user is CREATOR or EDITOR.
        """
        route = await self._ensure_route_exists(route_id)
        await self._ensure_has_role(
            user_id,
            route_id,
            allowed=[RouteRole.CREATOR, RouteRole.EDITOR],
            action="get share code",
        )
        return route.share_code

    async def grant_access(self, data: RouteAccessCreate, commit: bool = True) -> RouteAccess:
        """
        Grant access to a user for a route.
        Raises:
            RouteAccessAlreadyExistsError: If access already exists.
        """
        existing = await self.access_repo.get_by_user_and_route_and_role(data.user_id, data.route_id, data.role)
        if existing:
            message = "Route access service: RouteAccess (user_id=%s, role=%s, route_id=%s) already exists"
            logger.warning(message, data.user_id, data.role, data.route_id)
            raise RouteAccessAlreadyExistsError(message % (data.user_id, data.role, data.route_id))
        access = await self.access_repo.create(data, commit=commit)
        logger.info(
            "Route access service: granted %s access to user_id=%s for route_id=%s",
            data.role,
            data.user_id,
            data.route_id,
        )
        return access

    async def accept_by_share_code(self, user_id: int, share_code: str) -> RouteAccess:
        """
        Accept invitation by share code → grant VIEWER access.
        """
        route = await self.route_repo.get_by_share_code(share_code)
        if not route:
            msg = "Route access service: Route with share_code='%s' not found"
            logger.warning(msg, share_code)
            raise RouteNotFoundError(msg % share_code)

        existing = await self.access_repo.get_by_user_and_route_and_role(user_id, route.id, role=RouteRole.VIEWER)
        if existing:
            msg = "Route access service: User (id=%s) already has VIEWER access to Route (id=%s)"
            logger.warning(msg, user_id, route.id)
            raise RouteAccessAlreadyExistsError(msg % (user_id, route.id))

        data = RouteAccessCreate(
            user_id=user_id,
            route_id=route.id,
            role=RouteRole.VIEWER,
        )
        access = await self.grant_access(data)
        logger.info("Route access service: granted VIEWER access: %s", access)
        return access

    async def grant_editor(self, current_user_id: int, target_user_id: int, route_id: int) -> RouteAccess:
        """
        Grant EDITOR access to target_user. Only CREATOR or EDITOR can do this.
        """
        await self._ensure_route_exists(route_id)
        await self._ensure_has_role(
            current_user_id,
            route_id,
            allowed=[RouteRole.CREATOR, RouteRole.EDITOR],
            action="grant editor",
        )

        existing = await self.access_repo.get_by_user_and_route_and_role(
            target_user_id, route_id, role=RouteRole.EDITOR
        )
        if existing:
            msg = "Route access service: User (id=%s) already has EDITOR access to route (id=%s)"
            logger.warning(msg, target_user_id, route_id)
            raise RouteAccessAlreadyExistsError(msg % (target_user_id, route_id))

        data = RouteAccessCreate(
            user_id=target_user_id,
            route_id=route_id,
            role=RouteRole.EDITOR,
        )
        access = await self.grant_access(data)
        logger.info("Route access service: granted EDITOR access: %s", access)
        return access

    async def revoke_access(
        self, current_user_id: int, target_user_id: int, route_id: int, role_to_revoke: RouteRole
    ) -> None:
        """
        Revoke any access (VIEWER or EDITOR) for target_user. Only CREATOR or EDITOR can do this.
        """
        await self._ensure_route_exists(route_id)
        await self._ensure_has_role(
            current_user_id,
            route_id,
            allowed=[RouteRole.CREATOR, RouteRole.EDITOR],
            action="revoke access",
        )

        existing = await self.access_repo.get_by_user_and_route_and_role(target_user_id, route_id, role_to_revoke)
        if not existing:
            msg = "User (id=%s) has no %s access to route (id=%s)"
            logger.warning(msg, target_user_id, role_to_revoke, route_id)
            raise RouteAccessNotFoundError(msg % (target_user_id, role_to_revoke, route_id))

        await self.access_repo.delete_by_user_and_route_and_role(target_user_id, route_id, role_to_revoke)
        logger.info(
            "Revoked %s access for user (id=%s) on route (id=%s)",
            role_to_revoke,
            target_user_id,
            route_id,
        )

    async def list_access_for_user(self, user_id: int) -> List[int]:
        """
        Return a list of route IDs accessible by a given user.
        """
        access_list = await self.access_repo.get_all_by_user(user_id)
        return [a.route_id for a in access_list]

    async def list_users_with_access(self, route_id: int) -> List[int]:
        """
        Return a list of user IDs that have access to a given route.
        """
        access_list = await self.access_repo.get_all_by_route(route_id)
        return [a.user_id for a in access_list]
