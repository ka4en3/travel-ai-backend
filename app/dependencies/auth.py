# app/dependencies/auth.py

from models import User
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status
from db.sessions import get_session
from services.crud.user_service import UserService
from repositories.user import UserRepository


def get_user_service(session: AsyncSession = Depends(get_session)) -> UserService:
    """Dependency for user service."""
    return UserService(UserRepository(session))


async def get_current_user(
    service: UserService = Depends(get_user_service),
) -> User:
    return await service.get_user_by_id(1)
