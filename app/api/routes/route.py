# app/api/routes/route.py
import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from db.sessions import get_session
from schemas.route import RouteRead, RouteCreate, RouteShort
from services.crud.route_service import RouteService
from repositories.route import RouteRepository
from repositories.user import UserRepository
from repositories.ai_cache import AICacheRepository
from exceptions.route import (
    RouteAlreadyExistsError,
    RouteNotFoundError,
    InvalidRouteDataError,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/routes", tags=["Routes"])


def get_route_service(session: AsyncSession = Depends(get_session)) -> RouteService:
    """Dependency injection for RouteService."""
    return RouteService(
        route_repo=RouteRepository(session),
        user_repo=UserRepository(session),
        cache_repo=AICacheRepository(session),
    )


@router.get("/", response_model=List[RouteShort])
async def list_routes(service: RouteService = Depends(get_route_service)):
    """
    Get a list of all routes (short info).
    """
    return await service.list_routes()


@router.get("/{id}", response_model=RouteRead)
async def get_route(id: int, service: RouteService = Depends(get_route_service)):
    """
    Get detailed information about a route by ID.
    Raises:
        RouteNotFoundError: If route does not exist.
    """
    try:
        return await service.get_route_by_id(id)
    except RouteNotFoundError as e:
        logger.warning(str(e))
        raise HTTPException(status_code=404, detail=e.message)


@router.get("/by_code/{share_code}", response_model=RouteRead)
async def get_route_by_code(share_code: str, service: RouteService = Depends(get_route_service)):
    """
    Get route by share_code.
    Raises:
        RouteNotFoundError: If route does not exist.
    """
    try:
        return await service.get_route_by_code(share_code)
    except RouteNotFoundError as e:
        logger.warning(str(e))
        raise HTTPException(status_code=404, detail=e.message)


@router.get("/by_owner/{owner_id}", response_model=List[RouteRead])
async def get_routes_by_owner(owner_id: int, service: RouteService = Depends(get_route_service)):
    """
    Get all routes owned by a specific user.
    """
    return await service.get_route_by_owner(owner_id)


@router.post("/", response_model=RouteShort, status_code=status.HTTP_201_CREATED)
async def create_route(route_in: RouteCreate, service: RouteService = Depends(get_route_service)):
    """
    Create a new travel route.
    Raises:
        RouteAlreadyExistsError: If route with the same share_code already exists.
        InvalidRouteDataError: If route data is invalid.
    """
    try:
        return await service.create_route(route_in)
    except RouteAlreadyExistsError as e:
        logger.warning(str(e))
        raise HTTPException(status_code=409, detail=e.message)
    except InvalidRouteDataError as e:
        logger.warning(str(e))
        raise HTTPException(status_code=422, detail=e.message)


@router.put("/{id}", response_model=RouteShort)
async def rebuild_route(id: int, route_in: RouteCreate, service: RouteService = Depends(get_route_service)):
    """
    Rebuild an existing route by ID (delete + create new).
    Raises:
        RouteNotFoundError: If route does not exist.
        RouteAlreadyExistsError: If route with the same share_code already exists.
        InvalidRouteDataError: If route data is invalid.
    """
    try:
        return await service.rebuild_route(id, route_in)
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
async def delete_route(id: int, service: RouteService = Depends(get_route_service)):
    """
    Delete a route by ID.
    Raises:
        RouteNotFoundError: If route does not exist.
    """
    try:
        await service.delete_route(id)
    except RouteNotFoundError as e:
        logger.warning(str(e))
        raise HTTPException(status_code=404, detail=e.message)
