# app/services/crud/user_service.py

import logging
from typing import List

from repositories.user import UserRepository
from schemas.user import UserCreate, UserRead, UserShort
from exceptions.user import (
    UserAlreadyExistsError,
    UserNotFoundError,
    InvalidUserDataError,
    AuthenticationError,
)
from utils.security import hash_password, verify_password, create_access_token
from schemas.token import Token

logger = logging.getLogger(__name__)


class UserService:
    """
    Service layer for managing User logic.
    Throws UserAlreadyExistsError, UserNotFoundError, InvalidUserDataError
    """

    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def _create_telegram_user(self, user_in: UserCreate) -> UserRead:
        """
        Create a new user.
        Raises:
            UserAlreadyExistsError: If user already exists.
            InvalidUserDataError: If user data is invalid.
        """
        existing = await self.repo.get_by_telegram_id(user_in.telegram_id)
        if existing:
            message = "User service: User (telegram_id=%s) already exists"
            logger.warning(message, user_in.telegram_id)
            raise UserAlreadyExistsError(message % user_in.telegram_id)

        try:
            user = await self.repo.create(user_in)
        except Exception as e:
            message = "User service: User (telegram_id=%s) can't be created: %s. Check logs for details"
            logger.warning(message, user_in.telegram_id, e)
            raise InvalidUserDataError(message % (user_in.telegram_id, e))

        return user

    async def register(self, user_in: UserCreate) -> UserRead:
        # e-mail registration
        if user_in.email:
            existing = await self.repo.get_by_email(user_in.email)
            if existing:
                message = "User service: User (e-mail=%s) already exists"
                logger.warning(message, user_in.email)
                raise UserAlreadyExistsError(message % user_in.email)

            hashed = hash_password(user_in.password)

            try:
                user = await self.repo.create(
                    UserCreate(**user_in.model_dump(exclude={"password"}), password_hash=hashed)
                )
            except Exception as e:
                message = "User service: User (e-mail=%s) can't be created: %s. Check logs for details"
                logger.warning(message, user_in.email, e)
                raise InvalidUserDataError(message % (user_in.email, e))
        else:
            # Telegram registration
            user = await self._create_telegram_user(user_in)

        logger.info(
            "User service: User (user_id=%s, telegram_id=%s, e-mail=%s) created",
            user.id,
            user.telegram_id,
            user.email,
        )

        return user

    async def authenticate(self, email: str, password: str) -> Token:
        """
        Проверить email/password.
        Raises AuthenticationError если невалидно.

        Аутентифицировать и вернуть JWT.
        """
        user = await self.repo.get_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            raise AuthenticationError()
        token = create_access_token(subject=str(user.id))
        return Token(access_token=token)

    async def get_user_by_id(self, user_id: int) -> UserRead:
        """
        Get user by ID.
        Raises:
            UserNotFoundError: If user not found.
        """
        user = await self.repo.get(user_id)
        if not user:
            message = "User service: User (id=%s) not found"
            logger.warning(message, user_id)
            raise UserNotFoundError(message % user_id)
        return user

    async def get_user_by_telegram_id(self, telegram_id: int) -> UserRead:
        """
        Get user by Telegram ID.
        Raises:
            UserNotFoundError: If user not found.
        """
        user = await self.repo.get_by_telegram_id(telegram_id)
        if not user:
            message = "User service: User (telegram_id=%s) not found"
            logger.warning(message, telegram_id)
            raise UserNotFoundError(message % telegram_id)
        return user

    async def list_users(self) -> List[UserShort]:
        """List all users."""
        return await self.repo.get_all()

    async def delete_user(self, user_id: int) -> None:
        """Delete a user by ID."""
        await self.get_user_by_id(user_id)
        await self.repo.delete(user_id)
        logger.info("User service: User (id=%s) deleted", user_id)

    async def delete_user_by_telegram_id(self, telegram_id: int) -> None:
        """Delete a user by Telegram ID."""
        await self.get_user_by_telegram_id(telegram_id)
        await self.repo.delete_by_telegram_id(telegram_id)
        logger.info("User service: User (telegram_id=%s) deleted", telegram_id)
