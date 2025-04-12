# app/models/user.py

from typing import TYPE_CHECKING
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, func

from db.base_class import Base
from models.mixins import CreatedAtMixin

if TYPE_CHECKING:
    from .route import Route  # only for type hints - will not cause import on runtime


class User(CreatedAtMixin, Base):
    __tablename__ = "users"

    telegram_id: Mapped[int] = mapped_column(unique=True, index=True, nullable=False)
    username: Mapped[str | None] = mapped_column(index=True, nullable=False, default="new_user_username")
    first_name: Mapped[str] = mapped_column(nullable=False, default="new_user_first_name")
    last_name: Mapped[str | None] = mapped_column(nullable=True)
    language: Mapped[str | None] = mapped_column(nullable=True)
    is_premium: Mapped[bool] = mapped_column(nullable=False, default=False)
    is_bot: Mapped[bool] = mapped_column(nullable=False, default=False)
    last_active: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=func.now())

    owned_routes: Mapped[list["Route"]] = relationship(
        back_populates="owner",
        foreign_keys="Route.owner_id",
        cascade="all, delete-orphan",
    )

    ai_cache_entries: Mapped[list["AICache"]] = relationship(
        back_populates="user",
    )

    route_access: Mapped[list["RouteAccess"]] = relationship(
        back_populates="user",
    )

    exports: Mapped[list["Export"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, telegram_id={self.telegram_id}, username={self.username})>"
