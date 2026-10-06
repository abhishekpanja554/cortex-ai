"""add llm_usage table

Revision ID: fb0c0031d556
Revises: 9e4e7c032c83
Create Date: 2026-10-06 11:06:12.483587

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'fb0c0031d556'
down_revision: Union[str, Sequence[str], None] = '9e4e7c032c83'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
    "llm_usage",
    sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
    sa.Column("owner_id", postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column("source", sa.Text, nullable=False),
    sa.Column("model", sa.Text, nullable=False),
    sa.Column("prompt_tokens", sa.Integer, nullable=False),
    sa.Column("output_tokens", sa.Integer, nullable=False),
    sa.Column("estimated_cost_usd", sa.Numeric(14, 10), nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
)


def downgrade() -> None:
    op.drop_table("llm_usage")
