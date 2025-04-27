# app/api/routes/route.py

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.access import require_route_access
from constants.roles import RouteRole
from db.sessions import get_session
from api.dependencies import get_current_user
from schemas.route import RouteRead, RouteShort, RouteGenerateRequest
from services.crud.route_service import RouteService
from repositories.route import RouteRepository
from repositories.user import UserRepository
from repositories.ai_cache import AICacheRepository
from repositories import RouteAccessRepository
from exceptions.route import (
    RouteAlreadyExistsError,
    RouteNotFoundError,
    InvalidRouteDataError,
    PermissionDeniedError,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/routes", tags=["Routes"])


def get_route_service(session: AsyncSession = Depends(get_session)) -> RouteService:
    """Dependency injection for RouteService."""
    return RouteService(
        route_repo=RouteRepository(session),
        user_repo=UserRepository(session),
        cache_repo=AICacheRepository(session),
        access_repo=RouteAccessRepository(session),
    )


@router.get("/", response_model=List[RouteShort])
async def list_routes(
    current_user=Depends(get_current_user),
    svc: RouteService = Depends(get_route_service),
):
    """
    Get a list of all routes for the current user (short info). No role checking.
    """
    return await svc.list_routes_for_user(current_user.id)


@router.get("/{id}", response_model=RouteRead)
async def get_route(
    id: int,
    _=Depends(require_route_access([RouteRole.VIEWER, RouteRole.EDITOR, RouteRole.CREATOR])),
    svc: RouteService = Depends(get_route_service),
):
    """
    Get detailed information about a route by ID and check access.
    Role check for VIEWER, EDITOR and CREATOR.
    Raises:
        RouteNotFoundError: If route does not exist.
    """
    try:
        return await svc.get_route_by_id(id)
    except PermissionDeniedError as e:
        logger.warning(str(e))
        raise HTTPException(status_code=403, detail=e.message)
    except RouteNotFoundError as e:
        logger.warning(str(e))
        raise HTTPException(status_code=404, detail=e.message)


# search by share_code - available without role check if share_code is known
@router.get("/by_code/{share_code}", response_model=RouteRead)
async def get_route_by_code(
    share_code: str,
    svc: RouteService = Depends(get_route_service),
):
    """
    Get route by share_code.
    Raises:
        RouteNotFoundError: If route does not exist.
    """
    try:
        return await svc.get_route_by_code(share_code)
    except RouteNotFoundError as e:
        logger.warning(str(e))
        raise HTTPException(status_code=404, detail=e.message)


@router.get("/by_owner/{owner_id}", response_model=List[RouteRead])
async def get_routes_by_owner(
    owner_id: int,
    current_user=Depends(get_current_user),
    svc: RouteService = Depends(get_route_service),
):
    """
    Get all routes owned by a specific user.
    """
    if current_user.id != owner_id:
        raise HTTPException(
            status_code=403,
            detail="You can view only your own routes.",
        )
    return await svc.get_route_by_owner(owner_id)


@router.post(
    "/",
    response_model=RouteShort,
    status_code=status.HTTP_201_CREATED,
)
async def create_route(
    route_in: RouteGenerateRequest,
    current_user=Depends(get_current_user),
    svc: RouteService = Depends(get_route_service),
):
    """
    Create a new travel route.
    Raises:
        RouteAlreadyExistsError: If route with the same share_code already exists.
        InvalidRouteDataError: If route data is invalid.
    """
    try:
        return await svc.create_route(route_in, owner_id=current_user.id)
    except RouteAlreadyExistsError as e:
        logger.warning(str(e))
        raise HTTPException(status_code=409, detail=e.message)
    except InvalidRouteDataError as e:
        logger.warning(str(e))
        raise HTTPException(status_code=422, detail=e.message)


@router.put("/{id}", response_model=RouteShort)
async def rebuild_route(
    id: int,
    route_in: RouteGenerateRequest,
    current_user=Depends(get_current_user),
    _=Depends(require_route_access([RouteRole.CREATOR, RouteRole.EDITOR])),
    svc: RouteService = Depends(get_route_service),
):
    """
    Rebuild an existing route by ID (delete + create new).
    Role check for CREATOR and EDITOR.
    Raises:
        RouteNotFoundError: If route does not exist.
        RouteAlreadyExistsError: If route with the same share_code already exists.
        InvalidRouteDataError: If route data is invalid.
    """
    try:
        return await svc.rebuild_route(id, route_in, owner_id=current_user.id)
    except PermissionDeniedError as e:
        logger.warning(str(e))
        raise HTTPException(status_code=403, detail=e.message)
    except RouteNotFoundError as e:
        logger.warning(str(e))
        raise HTTPException(status_code=404, detail=e.message)
    except RouteAlreadyExistsError as e:
        logger.warning(str(e))
        raise HTTPException(status_code=409, detail=e.message)
    except InvalidRouteDataError as e:
        logger.warning(str(e))
        raise HTTPException(status_code=422, detail=e.message)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_route(
    id: int,
    _=Depends(require_route_access([RouteRole.CREATOR, RouteRole.EDITOR])),
    svc: RouteService = Depends(get_route_service),
):
    """
    Delete a route by ID.
    Role check for CREATOR and EDITOR.
    Raises:
        RouteNotFoundError: If route does not exist.
    """
    try:
        await svc.delete_route(id)
    except PermissionDeniedError as e:
        logger.warning(str(e))
        raise HTTPException(status_code=403, detail=e.message)
    except RouteNotFoundError as e:
        logger.warning(str(e))
        raise HTTPException(status_code=404, detail=e.message)
