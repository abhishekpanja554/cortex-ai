"""add title to note_chunks

Revision ID: c3f9a1d2e7b4
Revises: 6a1903aff0c3
Create Date: 2026-11-04 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'c3f9a1d2e7b4'
down_revision: Union[str, Sequence[str], None] = '6a1903aff0c3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("note_chunks", sa.Column("title", sa.Text, nullable=True))

    # The worker embeds f"{title}\n\n{body}", and chunk 0 always starts at the
    # first token, so the text before the first blank line of chunk 0 is the title.
    # Empty titles become NULL rather than ''.
    op.execute(
        r"""
        UPDATE note_chunks AS nc
        SET title = first_chunk.title
        FROM (
            SELECT note_id, NULLIF(split_part(chunk_text, E'\n\n', 1), '') AS title
            FROM note_chunks
            WHERE chunk_index = 0
        ) AS first_chunk
        WHERE nc.note_id = first_chunk.note_id
        """
    )


def downgrade() -> None:
    op.drop_column("note_chunks", "title")
