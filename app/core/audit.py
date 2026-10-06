import logging
from uuid import UUID

audit_logger = logging.getLogger("audit")

def log_llm_call(
        owner_id: UUID,
        source: str,
        model: str,
        redaction_count: int
) -> None:
    audit_logger.info(
        "LLM call: owner_id=%s source=%s model=%s redactions=%d",
        owner_id, source, model, redaction_count,
    )