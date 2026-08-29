"""add last_status column

Revision ID: 1b424ba1224b
Revises: 51f9effca94c
Create Date: 2026-08-29 19:30:02.791348

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1b424ba1224b'
down_revision: Union[str, None] = '51f9effca94c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "tender_records",
        sa.Column("last_status", sa.String(length=20), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("tender_records", "last_status")
