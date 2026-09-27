"""create note_chunks table

Revision ID: 70618cbaf8a8
Revises: 
Create Date: 2026-09-20 23:35:34.160780

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector


# revision identifiers, used by Alembic.
revision: str = '70618cbaf8a8'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "note_chunks",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid = True), primary_key = True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("note_id",sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("owner_id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("chunk_index", sa.Integer, nullable=False),
        sa.Column("chunk_text", sa.Text, nullable=False),
        sa.Column("embedding", Vector(3072), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    op.create_index("idx_note_chunks_note_id", "note_chunks", ["note_id"])

def downgrade() -> None:
    op.drop_table("note_chunks")
