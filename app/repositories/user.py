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
    """

    model = User

    def __init__(self, session: AsyncSession):
        """
        :param session: asynchronous session SQLAlchemy
        """
        super().__init__(User, session)

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        """Get user by telegram_id"""
        logger.debug(f"User Repo: fetching User with telegram_id={telegram_id}")
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        """Get user by username"""
        logger.debug(f"User Repo: fetching User with username={username}")
        stmt = select(User).where(User.username == username)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, user_data: UserCreate) -> User:
        """Create a new user"""
        logger.debug(
            f"User Repo: Creating new User with telegram_id={user_data.telegram_id}"
        )
        user = User(**user_data.model_dump())
        self.session.add(user)
        try:
            await self.session.commit()
            await self.session.refresh(user)
            logger.debug(f"User Repo: user created with id={user.id}")
            return user
        except IntegrityError as e:
            logger.debug("User Repo: IntegrityError on user creation: %s", e)
            await self.session.rollback()
            raise
