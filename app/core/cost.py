import logging
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from app.core.db import get_session

logger = logging.getLogger(__name__)

MODEL_PRICING = {
    "gemini-3.5-flash-lite": {"input": 0.30, "output": 2.50},
}

metadata = sa.MetaData()
llm_usage_table = sa.Table(
    "llm_usage", metadata,
    sa.Column("id", PGUUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
    sa.Column("owner_id", PGUUID(as_uuid=True), nullable=False),
    sa.Column("source", sa.Text, nullable=False),
    sa.Column("model", sa.Text, nullable=False),
    sa.Column("prompt_tokens", sa.Integer, nullable=False),
    sa.Column("output_tokens", sa.Integer, nullable=False),
    sa.Column("estimated_cost_usd", sa.Numeric(14, 10), nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
)

def record_llm_usage(
        owner_id: UUID,
        source: str,
        model: str,
        prompt_token: int,
        output_tokens: int
) -> None:
    pricing = MODEL_PRICING.get(model)
    if  pricing is None:
        logger.warning("No pricing entry for model=%s; recording cost as $0", model)
        pricing = {"input": 0.0, "output": 0.0}
    cost = (prompt_token / 1_000_000) * pricing["input"] + (output_tokens / 1_000_000) * pricing["output"]
    with get_session() as session:
        session.execute(
            sa.insert(llm_usage_table).values(
                owner_id=owner_id, source=source, model=model,
                prompt_tokens=prompt_token, output_tokens=output_tokens,
                estimated_cost_usd=cost,
            ),
        )
        session.commit()