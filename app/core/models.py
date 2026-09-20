from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, AliasGenerator
from pydantic.alias_generators import to_camel


class JobType(str, Enum):
    EMBED = "EMBED"
    DELETE_EMBEDDINGS = "DELETE_EMBEDDINGS"

class EmbeddingJobMessage(BaseModel):
    job_id: UUID
    note_id: UUID
    owner_id: UUID
    job_type: JobType
    title: str | None
    body: str | None
    published_at: datetime

    model_config = ConfigDict(
        alias_generator = AliasGenerator(
            validation_alias = to_camel
        ),
        populate_by_name = True
    )