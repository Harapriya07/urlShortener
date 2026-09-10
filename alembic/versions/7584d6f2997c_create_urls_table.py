"""create urls table

Revision ID: 7584d6f2997c
Revises: 
Create Date: 2026-09-10 21:05:17.593631

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7584d6f2997c'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "urls",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("original_url", sa.String(), nullable=False),
        sa.Column("short_code", sa.String(), nullable=True),
        sa.Column("clicks", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("short_code")
    )
    op.create_index(
        "ix_urls_id",
        "urls",
        ["id"],
        unique=False
    )
    op.create_index(
        "ix_urls_short_code",
        "urls",
        ["short_code"],
        unique=False
    )


def downgrade() -> None:
    op.drop_index("ix_urls_short_code", table_name="urls")
    op.drop_index("ix_urls_id", table_name="urls")
    op.drop_table("urls")