# app/repositories/user.py


# @router.post("/users")
# async def register_user(data: UserCreate, session: AsyncSession = Depends(get_session)):
#     repo = UserRepository(session)
#     return await repo.create(data)


from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.models.user import User
from app.schemas.user import UserCreate
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, user_data: UserCreate) -> User:
        user = User(**user_data.model_dump())
        self.session.add(user)
        try:
            await self.session.commit()
            await self.session.refresh(user)
            return user
        except IntegrityError:
            await self.session.rollback()
            raise
