# app/services/crud/user_service.py

import logging
from typing import List

from repositories.user import UserRepository
from schemas.user import UserCreate, UserRead, UserShort
from exceptions.user import UserAlreadyExistsError, UserNotFoundError

logger = logging.getLogger(__name__)


class UserService:
    """
    Service layer for managing User logic.
    """

    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def create_user(self, user_in: UserCreate) -> UserRead:
        existing = await self.repo.get_by_telegram_id(user_in.telegram_id)
        if existing:
            message = "User service: User already exists: telegram_id=%s"
            logger.warning(message, user_in.telegram_id)
            raise UserAlreadyExistsError(message % user_in.telegram_id)
        user = await self.repo.create(user_in)
        logger.info("User service: User created with user_id=%s", user.id)
        return user

    async def get_user_by_id(self, user_id: int) -> UserRead:
        user = await self.repo.get(user_id)
        if not user:
            message = "User service: User not found: id=%s"
            logger.warning(message, user_id)
            raise UserNotFoundError(message % user_id)
        return user

    async def get_user_by_telegram_id(self, telegram_id: int) -> UserRead:
        user = await self.repo.get_by_telegram_id(telegram_id)
        if not user:
            message = "User service: User not found: telegram_id=%s"
            logger.warning(message, telegram_id)
            raise UserNotFoundError(message % telegram_id)
        return user

    async def list_users(self) -> List[UserShort]:
        return await self.repo.get_all()

    async def delete_user(self, user_id: int) -> None:
        deleted = await self.repo.delete(user_id)
        if not deleted:
            message = "User service: User not found for deletion: id=%s"
            logger.warning(message, user_id)
            raise UserNotFoundError(message % user_id)
        logger.info("User service: User with id=%s deleted", user_id)
