from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AuditEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    occurred_at: datetime
    event_type: str
    entity_type: str
    entity_id: UUID | None
    employee_id: UUID | None
    initiated_by: str
    summary: str
    details: dict[str, object] | None
