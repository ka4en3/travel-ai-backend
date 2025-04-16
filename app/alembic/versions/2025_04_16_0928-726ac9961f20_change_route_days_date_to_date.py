"""change route_days.date to DATE

Revision ID: 726ac9961f20
Revises: 11f350b6607d
Create Date: 2025-04-16 09:28:11.446222

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "726ac9961f20"
down_revision: Union[str, None] = "11f350b6607d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.alter_column(
        "route_days",
        "date",
        type_=sa.Date(),
        existing_type=sa.TIMESTAMP(),
        postgresql_using="date::date",
    )


def downgrade():
    op.alter_column(
        "route_days",
        "date",
        type_=sa.TIMESTAMP(),
        existing_type=sa.Date(),
        postgresql_using="date::timestamp",
    )
