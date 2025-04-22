from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from db.sessions import get_session
from models.user import User
from dependencies.auth import get_current_user

from repositories.route_access import RouteAccessRepository
from services.crud.route_access_service import RouteAccessService

from schemas.common import SuccessResponse
from exceptions.route_access import RouteAccessAlreadyExistsError, RouteAccessNotFoundError

router = APIRouter(prefix="/route-access", tags=["Route Access"])


def get_route_access_service(session: AsyncSession = Depends(get_session)) -> RouteAccessService:
    return RouteAccessService(
        RouteAccessRepository(session),
    )


@router.post("/{route_id}/get-share-code", status_code=status.HTTP_200_OK)
async def get_share_code(
    route_id: int,
    user: User = Depends(get_current_user),
    service: RouteAccessService = Depends(get_route_access_service),
):
    """
    Provide a share code for the given route if the current user has sufficient permissions.
    """
    try:
        code = await service.generate_share_code(user.id, route_id)
        return {"share_code": code}
    except RouteAccessForbiddenError as e:
        logger.warning(str(e))
        raise HTTPException(status_code=403, detail=e.message)
    except RouteAccessNotFoundError as e:
        logger.warning(str(e))
        raise HTTPException(status_code=404, detail=e.message)


@router.post("/{route_id}/add-editor", response_model=SuccessResponse)
async def add_editor(
    route_id: int,
    user_id: int,
    service: RouteAccessService = Depends(get_route_access_service),
):
    """
    Grant EDITOR role to a user for the given route.
    """
    try:
        await service.grant_editor_access(route_id=route_id, user_id=user_id)
        return SuccessResponse(message="Editor access granted successfully.")
    except RouteAccessAlreadyExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.delete("/{route_id}/remove-access", response_model=SuccessResponse)
async def remove_access(
    route_id: int,
    user_id: int,
    service: RouteAccessService = Depends(get_route_access_service),
):
    """
    Revoke any access for a user to the given route.
    """
    try:
        await service.revoke_access(user_id=user_id, route_id=route_id)
        return SuccessResponse(message="Access revoked successfully.")
    except RouteAccessNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
