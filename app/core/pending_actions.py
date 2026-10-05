from uuid import UUID

import sqlalchemy as sa
from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID

from app.core.db import get_session

metadata = sa.MetaData()
pending_actions_table = sa.Table(
    "pending_actions",
    metadata,
    sa.Column("id", PGUUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
    sa.Column("owner_id", PGUUID(as_uuid=True), nullable=False),
    sa.Column("tool_name", sa.Text, nullable=False),
    sa.Column("tool_args", JSONB, nullable=False),
    sa.Column("status", sa.Text, nullable=False, server_default=sa.text("'PENDING'")),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
)

def create_pending_action(
        owner_id: UUID,
        tool_name: str,
        tool_args: dict
) -> UUID:
    stmt = (
        sa.insert(pending_actions_table)
        .values(owner_id=owner_id, tool_name=tool_name, tool_args=tool_args)
        .returning(pending_actions_table.c.id)
    )

    with get_session() as session:
        confirmation_id = session.execute(stmt).scalar_one()
        session.commit()
        return confirmation_id

def get_pending_action(confirmation_id: UUID) -> dict | None:
    stmt = select(pending_actions_table).where(pending_actions_table.c.id == confirmation_id)
    with get_session() as session:
        row = session.execute(stmt).first()
        return dict(row._mapping) if row else None

def resolve_pending_action(confirmation_id: UUID, owner_id: UUID, approved: bool) -> dict | None:
    new_status = "EXECUTED" if approved else "REJECTED"
    stmt = (
        update(pending_actions_table)
        .where(
            pending_actions_table.c.id == confirmation_id,
            pending_actions_table.c.owner_id == owner_id,
            pending_actions_table.c.status == "PENDING",
        )
        .values(status=new_status, resolved_at=sa.text("now()"))
        .returning(pending_actions_table.c.tool_name, pending_actions_table.c.tool_args)
    )
    with get_session() as session:
        row = session.execute(stmt).first()
        session.commit()
        return dict(row._mapping) if row else None