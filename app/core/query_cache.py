import sqlalchemy as sa

from datetime import datetime, timezone, timedelta
from uuid import UUID
from sqlalchemy import select
from app.core.db import get_session
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from pgvector.sqlalchemy import Vector

SIMILARITY_THRESHOLD = 0.05
TTL_MINUTES = 15
metadata = sa.MetaData()
query_cache_table = sa.Table(
    "query_cache", metadata,
    sa.Column("id", PGUUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
    sa.Column("owner_id", PGUUID(as_uuid=True), nullable=False),
    sa.Column("query_embedding", Vector(3072), nullable=False),
    sa.Column("answer", sa.Text, nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
)

def get_cached_answer(owner_id: UUID, query_embedding: list[float]) -> str | None:
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=TTL_MINUTES)
    distance_expr = query_cache_table.c.query_embedding.cosine_distance(query_embedding)
    stmt = (
        select(query_cache_table.c.answer, distance_expr.label("distance"))
        .where(query_cache_table.c.owner_id == owner_id, query_cache_table.c.created_at > cutoff)
        .order_by(distance_expr)
        .limit(1)
    )
    with get_session() as session:
        row = session.execute(stmt).first()
    return row.answer if row and row.distance < SIMILARITY_THRESHOLD else None

def store_answer(owner_id: UUID, query_embedding: list[float], answer: str) -> None:
    with get_session() as session:
        session.execute(sa.insert(query_cache_table).values(owner_id=owner_id, query_embedding=query_embedding, answer=answer))
        session.commit()