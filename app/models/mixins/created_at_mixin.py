# app/models/mixins/created_at_mixin.py

from datetime import datetime
from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column


class CreatedAtMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now(),
    )
