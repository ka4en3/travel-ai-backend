# app/api/dependencies/access.py

from typing import List

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from db.sessions import get_session
from repositories.route_access import RouteAccessRepository
from repositories.route import RouteRepository
from services.crud.route_access_service import RouteAccessService
from api.dependencies import get_current_user
from constants.roles import RouteRole
from exceptions.route_access import RouteAccessNotFoundError


async def get_route_access_service(session: AsyncSession = Depends(get_session)) -> RouteAccessService:
    return RouteAccessService(
        access_repo=RouteAccessRepository(session),
        route_repo=RouteRepository(session),
    )


def require_route_access(required_roles: List[RouteRole]):
    async def dependency(
        id: int,
        current_user=Depends(get_current_user),
        access_service: RouteAccessService = Depends(get_route_access_service),
    ):
        try:
            has_access = await access_service.check_user_has_access(
                user_id=current_user.id,
                route_id=id,
                required_roles=required_roles,
            )
            if not has_access:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User does not have permission for this route",
                )
        except RouteAccessNotFoundError as e:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

    return dependency
