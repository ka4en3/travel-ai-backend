# app/models/route_access.py

from enum import Enum
from sqlalchemy import ForeignKey, Enum as PgEnum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base_class import Base


class RouteRole(Enum):
    CREATOR = "creator"
    EDITOR = "editor"
    VIEWER = "viewer"


# Many-to-many relationship for shared routes
class RouteAccess(Base):
    __tablename__ = "route_access"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=False)
    route_id: Mapped[int] = mapped_column(ForeignKey("routes.id", ondelete="CASCADE"), nullable=False)
    role: Mapped[RouteRole] = mapped_column(PgEnum(RouteRole), nullable=False, default=RouteRole.VIEWER)

    user: Mapped["User"] = relationship(
        back_populates="route_access",
    )
    route: Mapped["Route"] = relationship(
        back_populates="access_list",
    )

    __table_args__ = (UniqueConstraint("user_id", "route_id", name="uq_user_route"),)

    def __repr__(self) -> str:
        return f"<RouteAccess(user_id={self.user_id}, route_id={self.route_id}, role={self.role})>"
