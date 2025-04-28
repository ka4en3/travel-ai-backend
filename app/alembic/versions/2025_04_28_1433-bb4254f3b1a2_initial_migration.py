"""Initial migration

Revision ID: bb4254f3b1a2
Revises:
Create Date: 2025-04-28 14:33:12.894337

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "bb4254f3b1a2"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "users",
        sa.Column("telegram_id", sa.Integer(), nullable=True),
        sa.Column("email", sa.String(length=256), nullable=True),
        sa.Column("password_hash", sa.String(length=128), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_superuser", sa.Boolean(), nullable=False),
        sa.Column("username", sa.String(length=128), nullable=True),
        sa.Column("first_name", sa.String(length=128), nullable=True),
        sa.Column("last_name", sa.String(length=128), nullable=True),
        sa.Column("language", sa.String(length=16), nullable=True),
        sa.Column("is_premium", sa.Boolean(), nullable=False),
        sa.Column("is_bot", sa.Boolean(), nullable=False),
        sa.Column("last_active", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)
    op.create_index(op.f("ix_users_telegram_id"), "users", ["telegram_id"], unique=True)
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=False)
    op.create_table(
        "ai_cache",
        sa.Column("cache_key", sa.String(), nullable=False),
        sa.Column("prompt_hash", sa.String(), nullable=False),
        sa.Column("original_prompt", sa.Text(), nullable=False),
        sa.Column("origin", sa.String(), nullable=False),
        sa.Column("destination", sa.String(), nullable=False),
        sa.Column("duration_days", sa.Integer(), nullable=False),
        sa.Column("budget", sa.Float(), nullable=False),
        sa.Column("interests", sa.JSON(), nullable=True),
        sa.Column("result", sa.JSON(), nullable=False),
        sa.Column("hit_count", sa.Integer(), nullable=False),
        sa.Column("source", sa.String(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_ai_cache_user_id_users"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_ai_cache")),
    )
    op.create_index(op.f("ix_ai_cache_budget"), "ai_cache", ["budget"], unique=False)
    op.create_index(op.f("ix_ai_cache_cache_key"), "ai_cache", ["cache_key"], unique=True)
    op.create_index(
        op.f("ix_ai_cache_destination"),
        "ai_cache",
        ["destination"],
        unique=False,
    )
    op.create_index(
        op.f("ix_ai_cache_duration_days"),
        "ai_cache",
        ["duration_days"],
        unique=False,
    )
    op.create_index(op.f("ix_ai_cache_id"), "ai_cache", ["id"], unique=False)
    op.create_index(op.f("ix_ai_cache_origin"), "ai_cache", ["origin"], unique=False)
    op.create_index(
        "ix_cache_from_to_days_budget",
        "ai_cache",
        ["origin", "destination", "duration_days", "budget"],
        unique=False,
    )
    op.create_table(
        "routes",
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("share_code", sa.String(), nullable=False),
        sa.Column("is_public", sa.Boolean(), nullable=False),
        sa.Column("origin", sa.String(), nullable=False),
        sa.Column("destination", sa.String(), nullable=False),
        sa.Column("duration_days", sa.Integer(), nullable=False),
        sa.Column("budget", sa.Float(), nullable=False),
        sa.Column("interests", sa.JSON(), nullable=False),
        sa.Column("route_data", sa.JSON(), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("ai_cache_id", sa.Integer(), nullable=True),
        sa.Column("last_edited_by", sa.Integer(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["ai_cache_id"],
            ["ai_cache.id"],
            name=op.f("fk_routes_ai_cache_id_ai_cache"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["last_edited_by"],
            ["users.id"],
            name=op.f("fk_routes_last_edited_by_users"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["owner_id"],
            ["users.id"],
            name=op.f("fk_routes_owner_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_routes")),
    )
    op.create_index(op.f("ix_routes_destination"), "routes", ["destination"], unique=False)
    op.create_index(op.f("ix_routes_id"), "routes", ["id"], unique=False)
    op.create_index(op.f("ix_routes_name"), "routes", ["name"], unique=False)
    op.create_index(op.f("ix_routes_origin"), "routes", ["origin"], unique=False)
    op.create_index(op.f("ix_routes_share_code"), "routes", ["share_code"], unique=True)
    op.create_table(
        "exports",
        sa.Column("route_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column(
            "export_type",
            sa.Enum("PDF", "GOOGLE_CALENDAR", "GOOGLE_DOCS", name="exporttype"),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum("QUEUED", "SUCCESS", "FAILED", name="exportstatus"),
            nullable=False,
        ),
        sa.Column("file_path", sa.String(), nullable=True),
        sa.Column("external_id", sa.String(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["route_id"],
            ["routes.id"],
            name=op.f("fk_exports_route_id_routes"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_exports_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_exports")),
    )
    op.create_index(op.f("ix_exports_id"), "exports", ["id"], unique=False)
    op.create_table(
        "route_access",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("route_id", sa.Integer(), nullable=False),
        sa.Column(
            "role",
            sa.Enum("CREATOR", "EDITOR", "VIEWER", name="routerole"),
            nullable=False,
        ),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["route_id"],
            ["routes.id"],
            name=op.f("fk_route_access_route_id_routes"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_route_access_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_route_access")),
        sa.UniqueConstraint("user_id", "route_id", "role", name="uq_user_route"),
    )
    op.create_index(op.f("ix_route_access_id"), "route_access", ["id"], unique=False)
    op.create_table(
        "route_days",
        sa.Column("route_id", sa.Integer(), nullable=False),
        sa.Column("day_number", sa.Integer(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("date", sa.Date(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["route_id"],
            ["routes.id"],
            name=op.f("fk_route_days_route_id_routes"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_route_days")),
    )
    op.create_index(op.f("ix_route_days_id"), "route_days", ["id"], unique=False)
    op.create_table(
        "activities",
        sa.Column("day_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("start_time", sa.String(), nullable=True),
        sa.Column("end_time", sa.String(), nullable=True),
        sa.Column("location", sa.String(), nullable=True),
        sa.Column("cost", sa.Float(), nullable=True),
        sa.Column("notes", sa.String(), nullable=True),
        sa.Column("activity_type", sa.String(), nullable=True),
        sa.Column("external_link", sa.String(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["day_id"],
            ["route_days.id"],
            name=op.f("fk_activities_day_id_route_days"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_activities")),
    )
    op.create_index(op.f("ix_activities_id"), "activities", ["id"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_activities_id"), table_name="activities")
    op.drop_table("activities")
    op.drop_index(op.f("ix_route_days_id"), table_name="route_days")
    op.drop_table("route_days")
    op.drop_index(op.f("ix_route_access_id"), table_name="route_access")
    op.drop_table("route_access")
    op.drop_index(op.f("ix_exports_id"), table_name="exports")
    op.drop_table("exports")
    op.drop_index(op.f("ix_routes_share_code"), table_name="routes")
    op.drop_index(op.f("ix_routes_origin"), table_name="routes")
    op.drop_index(op.f("ix_routes_name"), table_name="routes")
    op.drop_index(op.f("ix_routes_id"), table_name="routes")
    op.drop_index(op.f("ix_routes_destination"), table_name="routes")
    op.drop_table("routes")
    op.drop_index("ix_cache_from_to_days_budget", table_name="ai_cache")
    op.drop_index(op.f("ix_ai_cache_origin"), table_name="ai_cache")
    op.drop_index(op.f("ix_ai_cache_id"), table_name="ai_cache")
    op.drop_index(op.f("ix_ai_cache_duration_days"), table_name="ai_cache")
    op.drop_index(op.f("ix_ai_cache_destination"), table_name="ai_cache")
    op.drop_index(op.f("ix_ai_cache_cache_key"), table_name="ai_cache")
    op.drop_index(op.f("ix_ai_cache_budget"), table_name="ai_cache")
    op.drop_table("ai_cache")
    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.drop_index(op.f("ix_users_telegram_id"), table_name="users")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
    op.execute("DROP TYPE IF EXISTS routerole")
    op.execute("DROP TYPE IF EXISTS exporttype")
    op.execute("DROP TYPE IF EXISTS exportstatus")
