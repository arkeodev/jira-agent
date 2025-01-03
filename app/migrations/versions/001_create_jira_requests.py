"""Create jira_requests table

Revision ID: 001
Revises:
Create Date: 2025-01-03 22:17:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql import func

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "jira_requests",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("request", sa.Text(), nullable=True),
        sa.Column("response", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=func.now(),
            nullable=True,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_jira_requests_id"), "jira_requests", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_jira_requests_id"), table_name="jira_requests")
    op.drop_table("jira_requests")
