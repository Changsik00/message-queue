"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-04-06

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "orders",
        sa.Column("order_id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.VARCHAR(100), nullable=False),
        sa.Column("total_price", sa.Integer(), nullable=False),
        sa.Column("status", sa.VARCHAR(20), server_default="PENDING", nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("order_id"),
    )

    op.create_table(
        "event_logs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("order_id", sa.UUID(), nullable=False),
        sa.Column("worker_type", sa.VARCHAR(50), nullable=False),
        sa.Column("mq_type", sa.VARCHAR(50), nullable=False),
        sa.Column("language", sa.VARCHAR(20), nullable=False),
        sa.Column("published_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("consumed_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("status", sa.VARCHAR(20), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "processed_events",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("event_id", sa.VARCHAR(), nullable=False),
        sa.Column("group_id", sa.VARCHAR(), nullable=False),
        sa.Column("mq_type", sa.VARCHAR(), nullable=False),
        sa.Column("data", sa.VARCHAR(), nullable=False),
        sa.Column(
            "processed_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=True,
        ),
        sa.Column("latency_ms", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("processed_events")
    op.drop_table("event_logs")
    op.drop_table("orders")
