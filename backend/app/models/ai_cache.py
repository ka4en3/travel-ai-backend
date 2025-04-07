from datetime import datetime
from sqlalchemy import String, DateTime, JSON, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class AICache(Base):
    __tablename__ = "ai_cache"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, nullable=False)
    cache_key: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    prompt_hash: Mapped[str | None] = mapped_column(nullable=True)
    origin: Mapped[str | None] = mapped_column(String, index=True, nullable=True)
    destination: Mapped[str | None] = mapped_column(String, index=True, nullable=True)
    duration_days: Mapped[int | None] = mapped_column(nullable=True)
    interests: Mapped[list[str]] = mapped_column(JSON, nullable=True)
    budget: Mapped[float | None] = mapped_column(nullable=True)
    result: Mapped[dict] = mapped_column(JSON, nullable=False)
    hit_count: Mapped[int] = mapped_column(nullable=False, default=1)
    source: Mapped[str] = mapped_column(nullable=False, default="bot")
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship()

    routes: Mapped[list["Route"]] = relationship(
        back_populates="ai_cache",
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_cache_from_to_days_budget", "origin", "destination", "duration_days", "budget"),
    )

    def __repr__(self) -> str:
        return f"<AICache(destination={self.destination}, hits={self.hit_count})>"
