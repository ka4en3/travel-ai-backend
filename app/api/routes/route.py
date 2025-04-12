# app/api/routes/route.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from db.sessions import get_session
from schemas.route import RouteRead, RouteCreate, RouteShort, RouteUpdate
from repositories.route import RouteRepository

import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/routes", tags=["Routes"])


@router.get("/", response_model=List[RouteShort])
async def list_routes(session: AsyncSession = Depends(get_session)):
    """
    Get a list of all routes (short info).
    """
    repo = RouteRepository(session)
    routes = await repo.get_all()
    logger.info("Fetched %d routes", len(routes))
    return routes


@router.get("/{id}", response_model=RouteRead)
async def get_route(id: int, session: AsyncSession = Depends(get_session)):
    """
    Get detailed information about a route by ID.
    """
    repo = RouteRepository(session)
    route = await repo.get(id)
    if not route:
        logger.warning("Route with id=%d not found", id)
        raise HTTPException(status_code=404, detail="Route not found")
    return route


@router.post("/", response_model=RouteRead, status_code=status.HTTP_201_CREATED)
async def create_route(route_in: RouteCreate, session: AsyncSession = Depends(get_session)):
    """
    Create a new travel route.
    """
    repo = RouteRepository(session)
    existing = await repo.get_by_share_code(route_in.share_code)
    if existing:
        logger.info("Route already exists: share_code=%s", route_in.share_code)
        raise HTTPException(status_code=409, detail="Route already exists")
    route = await repo.create(route_in)
    logger.info("Created new route with id=%d", route.id)
    return route


@router.put("/{id}", response_model=RouteRead)
async def update_route(id: int, route_in: RouteUpdate, session: AsyncSession = Depends(get_session)):
    """
    Update an existing route by ID.
    """
    repo = RouteRepository(session)
    route = await repo.update(id, route_in)
    if not route:
        logger.warning("Failed to update route with id=%d: not found", id)
        raise HTTPException(status_code=404, detail="Route not found")
    logger.info("Updated route with id=%d", id)
    return route


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_route(id: int, session: AsyncSession = Depends(get_session)):
    """
    Delete a route by ID.
    """
    repo = RouteRepository(session)
    success = await repo.delete(id)
    if not success:
        logger.warning("Failed to delete route with id=%d: not found", id)
        raise HTTPException(status_code=404, detail="Route not found")
    logger.info("Deleted route with id=%d", id)
