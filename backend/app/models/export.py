from datetime import datetime
from enum import Enum
from sqlalchemy import ForeignKey, String, Integer, DateTime, Enum as PgEnum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class ExportType(str, Enum):
    PDF = "pdf"
    GOOGLE_CALENDAR = "google_calendar"
    GOOGLE_DOCS = "google_docs"

class Export(Base):
    __tablename__ = "exports"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, nullable=False)
    route_id: Mapped[int] = mapped_column(ForeignKey("routes.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    export_type: Mapped[ExportType] = mapped_column(PgEnum(ExportType), nullable=False)
    file_path: Mapped[str | None] = mapped_column(nullable=True)
    external_id: Mapped[str | None] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(nullable=False, default="success")
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    route: Mapped["Route"] = relationship()
    user: Mapped["User"] = relationship()

    def __repr__(self) -> str:
        return f"<Export(id={self.id}, type={self.export_type})>"
