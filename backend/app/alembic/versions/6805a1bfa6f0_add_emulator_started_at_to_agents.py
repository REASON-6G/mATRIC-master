"""add emulator_started_at to agents

Revision ID: 6805a1bfa6f0
Revises: bb7fa6d22e23
Create Date: 2025-09-25 10:39:04.614726
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "6805a1bfa6f0"
down_revision = "bb7fa6d22e23"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "agents",
        sa.Column("emulator_started_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        "ix_agents_emulator_started_at",
        "agents",
        ["emulator_started_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_agents_emulator_started_at", table_name="agents")
    op.drop_column("agents", "emulator_started_at")
