# app/repositories/user.py


# @router.post("/users")
# async def register_user(data: UserCreate, session: AsyncSession = Depends(get_session)):
#     repo = UserRepository(session)
#     return await repo.create(data)


import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.models.user import User
from app.schemas.user import UserCreate
from app.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class UserRepository(BaseRepository[User]):
    """
    Repository for the User model.
    Provides methods for working with users.
    """

    def __init__(self, session: AsyncSession):
        """
        :param session: asynchronous session SQLAlchemy
        """
        super().__init__(User, session)

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        """Get user by telegram_id"""
        logger.debug(f"Fetching User with telegram_id={telegram_id}")
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, user_data: UserCreate) -> User:
        """Create a new user"""
        logger.info(f"Creating new User with telegram_id={user_data.telegram_id}")
        user = User(**user_data.model_dump())
        self.session.add(user)
        try:
            await self.session.commit()
            await self.session.refresh(user)
            logger.info(f"User created with id={user.id}")
            return user
        except IntegrityError as e:
            logger.warning("IntegrityError on user creation: %s", e)
            await self.session.rollback()
            raise
