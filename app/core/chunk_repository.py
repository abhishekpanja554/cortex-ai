import uuid
from uuid import UUID, uuid4
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector
from sqlalchemy import delete
from sqlalchemy.dialects.postgresql import insert

from app.core.db import get_session

metadata = sa.MetaData()
note_chunks_table = sa.Table(
    "note_chunks",
    metadata,
    sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
    sa.Column("note_id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column("owner_id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column("chunk_index", sa.Integer, nullable=False),
    sa.Column("chunk_text", sa.Text, nullable=False),
    sa.Column("embedding", Vector(3072), nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
)

def save_chunks(note_id: UUID, owner_id: UUID, chunks: list[str], embeddingd: list[list[float]]) -> None:
    if len(chunks) != len(embeddingd):
        raise ValueError(f"chunks and embeddings must have the same length ({len(chunks)} != {len(embeddingd)})")

    if not chunks:
        return

    insert_values = [
        {
            "note_id": note_id,
            "owner_id": owner_id,
            "chunk_index": i,
            "chunk_text": chunk,
            "embedding": embedding,
        }
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddingd))
    ]

    with get_session() as session:
        session.execute(insert(note_chunks_table), insert_values)
        session.commit()

def delete_chunks(note_id: UUID ) -> None:
    with get_session() as session:
        session.execute(delete(note_chunks_table).where(note_chunks_table.c.note_id == note_id))
        session.commit()

    uuid.UUID("4a1e44a4-d3f1-4308-ae65-87810d6c2aba")