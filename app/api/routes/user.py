# app/api/routes/user.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from db.sessions import get_session
from schemas.user import UserCreate, UserRead, UserShort
from services.user_service import UserService
from exceptions.user import UserAlreadyExistsError, UserNotFoundError

router = APIRouter(prefix="/users", tags=["Users"])


def get_user_service(session: AsyncSession = Depends(get_session)) -> UserService:
    return UserService(session)


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(user_in: UserCreate, service: UserService = Depends(get_user_service)):
    """
    Create a new user from Telegram data.
    """
    try:
        return await service.create_user(user_in)
    except UserAlreadyExistsError:
        raise HTTPException(status_code=409, detail="User already exists")


@router.get("/", response_model=List[UserShort])
async def list_users(service: UserService = Depends(get_user_service)):
    """
    Get a list of all users.
    """
    return await service.list_users()


# @router.get("/{user_id}", response_model=UserRead)
# async def get_user(user_id: int, service: UserService = Depends(get_user_service)):
#     """
#     Get full user details by ID.
#     """
#     try:
#         return await service.get_user_by_id(user_id)
#     except UserNotFoundError:
#         raise HTTPException(status_code=404, detail="User not found")


@router.get("/{telegram_id}", response_model=UserRead)
async def get_user_by_telegram_id(
    telegram_id: int,
    service: UserService = Depends(get_user_service),
):
    """
    Get full user details by Telegram ID.
    """
    try:
        return await service.get_user_by_telegram_id(telegram_id)
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, service: UserService = Depends(get_user_service)):
    """
    Delete a user by ID.
    """
    try:
        await service.delete_user(user_id)
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")
