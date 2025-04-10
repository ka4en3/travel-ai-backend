from datetime import datetime
from typing import List
from sqlalchemy import ForeignKey, String, Integer, DateTime, JSON, Table, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base_class import Base
from models.mixins import CreatedAtMixin


class Route(CreatedAtMixin, Base):
    __tablename__ = "routes"

    name: Mapped[str] = mapped_column(nullable=False, index=True)
    share_code: Mapped[str] = mapped_column(
        String, unique=True, index=True, nullable=False
    )
    is_public: Mapped[bool] = mapped_column(nullable=False, default=False)

    origin: Mapped[str] = mapped_column(String, index=True, nullable=False)
    destination: Mapped[str] = mapped_column(String, index=True, nullable=False)
    duration_days: Mapped[int] = mapped_column(nullable=False)
    interests: Mapped[list[str]] = mapped_column(
        JSON, nullable=True
    )  # Stored as a JSON array
    budget: Mapped[float] = mapped_column(nullable=False)

    # Route data - stores the actual AI-generated route
    route_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    last_edited_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    ai_cache_id: Mapped[int | None] = mapped_column(
        ForeignKey("ai_cache.id", ondelete="SET NULL"), nullable=True
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now(),
        onupdate=func.now(),
        server_default=func.now(),
    )

    owner: Mapped["User"] = relationship(
        back_populates="owned_routes", foreign_keys=[owner_id]
    )
    access_list: Mapped[list["RouteAccess"]] = relationship(
        back_populates="route",
        cascade="all, delete-orphan",
    )
    days: Mapped[List["RouteDay"]] = relationship(
        back_populates="route",
        cascade="all, delete-orphan",
    )
    ai_cache: Mapped["AICache"] = relationship(
        back_populates="routes",
    )
    exports: Mapped[list["Export"]] = relationship(
        back_populates="route",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Route(id={self.id}, destination={self.destination})>"


class RouteDay(Base):
    __tablename__ = "route_days"

    route_id: Mapped[int] = mapped_column(
        ForeignKey("routes.id", ondelete="CASCADE"), nullable=False
    )
    day_number: Mapped[int] = mapped_column(nullable=False)
    description: Mapped[str | None] = mapped_column(nullable=True)
    date: Mapped[datetime | None] = mapped_column(nullable=True)

    route: Mapped["Route"] = relationship(
        back_populates="days",
    )
    activities: Mapped[List["Activity"]] = relationship(
        back_populates="day",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<RouteDay(route_id={self.route_id}, day={self.day_number})>"


class Activity(Base):
    __tablename__ = "activities"

    day_id: Mapped[int] = mapped_column(
        ForeignKey("route_days.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str | None] = mapped_column(nullable=True)
    start_time: Mapped[str | None] = mapped_column(nullable=True)  # Format: "HH:MM"
    end_time: Mapped[str | None] = mapped_column(nullable=True)  # Format: "HH:MM"
    location: Mapped[str | None] = mapped_column(nullable=True)
    cost: Mapped[float | None] = mapped_column(nullable=True)  # Estimated cost
    notes: Mapped[str | None] = mapped_column(nullable=True)
    activity_type: Mapped[str | None] = mapped_column(
        nullable=True
    )  # e.g., "Sightseeing", "Food", "Transportation"
    external_link: Mapped[str | None] = mapped_column(nullable=True)

    day: Mapped["RouteDay"] = relationship(
        back_populates="activities",
    )

    def __repr__(self) -> str:
        return f"<Activity(name={self.name}, type={self.activity_type})>"
