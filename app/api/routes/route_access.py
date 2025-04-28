# app/api/routes/route_access.py

from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession

from constants.roles import RouteRole
from db.sessions import get_session
from schemas.route_access import RouteAccessRead
from schemas.user import UserRead
from services.crud.route_access_service import RouteAccessService
from repositories.route_access import RouteAccessRepository
from repositories.route import RouteRepository
from api.dependencies import get_current_user
from exceptions.route import RouteNotFoundError, PermissionDeniedError
from exceptions.route_access import RouteAccessAlreadyExistsError, RouteAccessNotFoundError

router = APIRouter(prefix="/route-access", tags=["Route Access"])


def get_route_access_service(session: AsyncSession = Depends(get_session)) -> RouteAccessService:
    return RouteAccessService(
        access_repo=RouteAccessRepository(session),
        route_repo=RouteRepository(session),
    )


@router.get("/{route_id}/get-share-code")
async def get_share_code(
    route_id: int,
    current_user: UserRead = Depends(get_current_user),
    service: RouteAccessService = Depends(get_route_access_service),
):
    """
    Return the share_code for a route, if the current user is creator or editor.
    """
    try:
        code = await service.get_share_code(current_user.id, route_id)
        return {"share_code": code}
    except RouteNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.post("/accept-by-code", response_model=RouteAccessRead)
async def accept_by_code(
    code: str = Body(..., embed=True),
    current_user: UserRead = Depends(get_current_user),
    service: RouteAccessService = Depends(get_route_access_service),
):
    """
    Grant VIEWER access to the route identified by share_code.
    """
    try:
        access = await service.accept_by_share_code(current_user.id, code)
        return RouteAccessRead.model_validate(access)
    except RouteNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RouteAccessAlreadyExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.post("/{route_id}/grant-editor")
async def grant_editor(
    route_id: int,
    target_user_id: int = Body(..., embed=True),
    current_user: UserRead = Depends(get_current_user),
    service: RouteAccessService = Depends(get_route_access_service),
):
    """
    Grant EDITOR access on a route. Only CREATOR or EDITOR can do this.
    """
    try:
        await service.grant_editor(current_user.id, target_user_id, route_id)
        return {"message": "Editor access granted successfully."}
    except RouteNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except (PermissionDeniedError, RouteAccessAlreadyExistsError) as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.delete("/{route_id}/revoke-access")
async def revoke_access(
    route_id: int,
    target_user_id: int = Body(..., embed=True),
    current_user: UserRead = Depends(get_current_user),
    service: RouteAccessService = Depends(get_route_access_service),
):
    """
    Revoke any access (VIEWER or EDITOR) from a user. Only CREATOR or EDITOR can do this.
    """
    try:
        await service.revoke_access(current_user.id, target_user_id, route_id, RouteRole.VIEWER)
        await service.revoke_access(current_user.id, target_user_id, route_id, RouteRole.EDITOR)
        return {"message": "Access revoked successfully."}
    except RouteNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except (PermissionDeniedError, RouteAccessNotFoundError) as e:
        raise HTTPException(status_code=403, detail=str(e))
