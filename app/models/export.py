# app/models/export.py

from enum import Enum
from sqlalchemy import ForeignKey, String, Enum as PgEnum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base_class import Base
from models.mixins import CreatedAtMixin


class ExportType(Enum):
    PDF = "pdf"
    GOOGLE_CALENDAR = "google_calendar"
    GOOGLE_DOCS = "google_docs"


class ExportStatus(Enum):
    QUEUED = "queued"
    SUCCESS = "success"
    FAILED = "failed"


class Export(CreatedAtMixin, Base):
    __tablename__ = "exports"

    route_id: Mapped[int] = mapped_column(
        ForeignKey("routes.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    export_type: Mapped[ExportType] = mapped_column(
        PgEnum(ExportType),
        nullable=False,
    )

    status: Mapped[ExportStatus] = mapped_column(
        PgEnum(ExportStatus),
        nullable=False,
        default=ExportStatus.QUEUED,
    )

    file_path: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )  # For PDF exports
    external_id: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )  # For Google Calendar/Docs exports
    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    user: Mapped["User"] = relationship(
        back_populates="exports",
    )
    route: Mapped["Route"] = relationship(
        back_populates="exports",
    )

    def __repr__(self) -> str:
        return f"<Export(id={self.id}, type={self.export_type}, status={self.status})>"
