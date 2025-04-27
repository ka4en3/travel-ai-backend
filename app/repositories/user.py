# app/repositories/user.py

import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from models.user import User
from schemas.user import UserCreate
from repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class UserRepository(BaseRepository[User]):
    """
    Repository for the User model.
    Throws IntegrityError if user already exists.
    """

    def __init__(self, session: AsyncSession):
        """
        :param session: asynchronous session SQLAlchemy
        """
        super().__init__(User, session)

    async def create(self, user_data: UserCreate, **kwargs) -> User:
        """Create a new user"""
        logger.debug("User repo: creating new User")
        # user = User(**user_data.model_dump())
        user = User(**user_data.model_dump(exclude={"password"}), password_hash=kwargs.get("password_hash"))
        self.session.add(user)
        try:
            await self.session.commit()
            await self.session.refresh(user)
            logger.debug("User repo: User (id=%s, telegram_id=%s) created", user.id, user_data.telegram_id)
            return user
        except IntegrityError as e:
            logger.debug("User repo: IntegrityError on User creation: %s", e)
            await self.session.rollback()
            raise

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        """Get user by telegram_id"""
        logger.debug("User repo: fetching User (telegram_id=%s)", telegram_id)
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        """Get user by username"""
        logger.debug("User repo: fetching User (username=%s)", username)
        stmt = select(User).where(User.username == username)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete_by_telegram_id(self, telegram_id: int) -> bool:
        """
        Delete a RouteDay by ID.
        """
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            logger.debug("User repo: User (telegram_id=%s) not found", telegram_id)
            return False
        await self.session.delete(user)
        await self.session.commit()
        logger.debug("User repo: deleted User (telegram_id=%s)", telegram_id)
        return True

    async def delete_by_email(self, email: str) -> bool:
        logger.info("User repo: deleting User by email=%s", email)
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            return False
        await self.session.delete(user)
        await self.session.commit()
        return True
