from datetime import datetime, timezone
from pydantic import BaseModel, Field

from digital_company_ai_support.models.department import Department
from digital_company_ai_support.models.ticket_priority import TicketPriority


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Ticket(BaseModel):
    id: int | None = None
    createdAtUtc: datetime = Field(default_factory=utc_now)

    text: str

    department: Department = Department.Unknown
    priority: TicketPriority = TicketPriority.Normal
    recommendedAction: str = ""