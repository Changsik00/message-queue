"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-04-06

"""
from typing import Sequence, Union

from alembic import op

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id    UUID PRIMARY KEY,
            user_id     VARCHAR(100) NOT NULL,
            total_price INTEGER NOT NULL,
            status      VARCHAR(20) DEFAULT 'PENDING',
            created_at  TIMESTAMPTZ DEFAULT NOW()
        )
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS event_logs (
            id           SERIAL PRIMARY KEY,
            order_id     UUID NOT NULL,
            worker_type  VARCHAR(50) NOT NULL,
            mq_type      VARCHAR(50) NOT NULL,
            language     VARCHAR(20) NOT NULL,
            published_at TIMESTAMPTZ,
            consumed_at  TIMESTAMPTZ,
            latency_ms   INTEGER,
            status       VARCHAR(20),
            created_at   TIMESTAMPTZ DEFAULT NOW()
        )
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS processed_events (
            id           SERIAL PRIMARY KEY,
            event_id     VARCHAR NOT NULL,
            group_id     VARCHAR NOT NULL,
            mq_type      VARCHAR NOT NULL,
            data         VARCHAR NOT NULL,
            processed_at TIMESTAMPTZ DEFAULT NOW(),
            latency_ms   INTEGER NOT NULL
        )
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS processed_events")
    op.execute("DROP TABLE IF EXISTS event_logs")
    op.execute("DROP TABLE IF EXISTS orders")
