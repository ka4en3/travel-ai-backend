from datetime import datetime
from sqlalchemy import String, DateTime, Text, JSON, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base_class import Base
from models.mixins import CreatedAtMixin


class AICache(CreatedAtMixin, Base):
    __tablename__ = "ai_cache"

    cache_key: Mapped[str] = mapped_column(
        String, unique=True, index=True, nullable=False
    )
    prompt_hash: Mapped[str | None] = mapped_column(nullable=True)
    original_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)

    origin: Mapped[str | None] = mapped_column(String, index=True, nullable=True)
    destination: Mapped[str | None] = mapped_column(String, index=True, nullable=True)
    duration_days: Mapped[int | None] = mapped_column(nullable=True)
    interests: Mapped[list[str]] = mapped_column(JSON, nullable=True)
    budget: Mapped[float | None] = mapped_column(nullable=True)

    result: Mapped[dict] = mapped_column(JSON, nullable=False)

    hit_count: Mapped[int] = mapped_column(nullable=False, default=1)

    source: Mapped[str] = mapped_column(nullable=False, default="bot")

    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    user: Mapped["User"] = relationship(
        back_populates="ai_cache_entries",
    )

    routes: Mapped[list["Route"]] = relationship(
        back_populates="ai_cache",
    )

    __table_args__ = (
        Index(
            "ix_cache_from_to_days_budget",
            "origin",
            "destination",
            "duration_days",
            "budget",
        ),
    )

    def __repr__(self) -> str:
        return f"<AICache(destination={self.destination}, hits={self.hit_count})>"
