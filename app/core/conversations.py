import sqlalchemy as sa
from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from uuid import UUID

from app.core.db import get_session

metadata = sa.MetaData()
conversations_table = sa.Table(
    "conversations", metadata,
    sa.Column("id", PGUUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
    sa.Column("owner_id", PGUUID(as_uuid=True), nullable=False),
    sa.Column("history", JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
)

def create_conversation(owner_id: UUID) -> UUID:
    stmt = sa.insert(conversations_table).values(owner_id=owner_id).returning(conversations_table.c.id)
    with get_session() as session:
        conversation_id = session.execute(stmt).scalar_one()
        session.commit()
        return conversation_id

def get_conversation(conversation_id: UUID, owner_id: UUID) -> dict | None:
    stmt = select(conversations_table).where(
        conversations_table.c.id == conversation_id,
        conversations_table.c.owner_id == owner_id,
    )
    with get_session() as session:
        row = session.execute(stmt).first()
        return dict(row._mapping) if row else None

def append_turn(
        conversation_id: UUID,
        owner_id: UUID,
        user_text: str,
        model_text: str
) -> None:
    new_entries = [
        {"role":"user", "content": user_text},
        {"role":"model", "content": model_text}
    ]
    with get_session() as session:
        row = session.execute(
            select(conversations_table).where(
                conversations_table.c.id == conversation_id,
                conversations_table.c.owner_id == owner_id,
            )
        ).first()
        if row is None:
            return
        session.execute(
            update(conversations_table)
            .where(
                conversations_table.c.id == conversation_id,
                conversations_table.c.owner_id == owner_id
            ).values(history=row.history + new_entries, updated_at=sa.text("now()"))
        )
        session.commit()