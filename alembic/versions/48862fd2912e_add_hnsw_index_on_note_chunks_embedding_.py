"""add hnsw index on note_chunks embedding via halfvec cast

Revision ID: 48862fd2912e
Revises: 70618cbaf8a8
Create Date: 2026-09-27 18:01:49.343738

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '48862fd2912e'
down_revision: Union[str, Sequence[str], None] = '70618cbaf8a8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "CREATE INDEX ix_note_chunks_embedding_hnsw "
        "ON note_chunks USING hnsw ((embedding::halfvec(3072)) halfvec_cosine_ops)"
    )


def downgrade() -> None:
    op.drop_index("ix_note_chunks_embedding_hnsw", table_name="note_chunks")
