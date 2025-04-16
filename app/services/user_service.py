# app/services/user_service.py

import logging
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from repositories.user import UserRepository
from schemas.user import UserCreate, UserRead, UserShort
from exceptions.user import UserAlreadyExistsError, UserNotFoundError

logger = logging.getLogger(__name__)


class UserService:
    """
    Service for managing User logic.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = UserRepository(session)

    async def create_user(self, user_in: UserCreate) -> UserRead:
        existing = await self.repo.get_by_telegram_id(user_in.telegram_id)
        if existing:
            logger.warning("User already exists: telegram_id=%s", user_in.telegram_id)
            raise UserAlreadyExistsError(user_in.telegram_id)
        user = await self.repo.create(user_in)
        logger.info("User created with id=%s", user.id)
        return user

    async def get_user_by_id(self, user_id: int) -> UserRead:
        user = await self.repo.get(user_id)
        if not user:
            logger.warning("User not found: id=%s", user_id)
            raise UserNotFoundError()
        return user

    async def get_user_by_telegram_id(self, telegram_id: int) -> UserRead:
        user = await self.repo.get_by_telegram_id(telegram_id)
        if not user:
            logger.warning("User not found: telegram_id=%s", telegram_id)
            raise UserNotFoundError()
        return user

    async def list_users(self) -> List[UserShort]:
        return await self.repo.get_all()

    async def delete_user(self, user_id: int) -> None:
        deleted = await self.repo.delete(user_id)
        if not deleted:
            logger.warning("User not found for deletion: id=%s", user_id)
            raise UserNotFoundError()
