"""add conversations table

Revision ID: 9e4e7c032c83
Revises: b0952d273f26
Create Date: 2026-10-06 08:21:07.388887

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '9e4e7c032c83'
down_revision: Union[str, Sequence[str], None] = 'b0952d273f26'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
    "conversations",
    sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
    sa.Column("owner_id", postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column("history", postgresql.JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
)


def downgrade() -> None:
    op.drop_table("conversations")
