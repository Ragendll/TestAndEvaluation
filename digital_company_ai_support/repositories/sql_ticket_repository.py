from datetime import timezone
from typing import Iterable, List

from sqlalchemy.orm import Session

from digital_company_ai_support.db.models import TicketEntity
from digital_company_ai_support.models.department import Department
from digital_company_ai_support.models.ticket import Ticket
from digital_company_ai_support.models.ticket_priority import TicketPriority
from digital_company_ai_support.repositories.iticket_repository import ITicketRepository


class SqlTicketRepository(ITicketRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def getAll(self) -> Iterable[Ticket]:
        entities: List[TicketEntity] = (
            self._session.query(TicketEntity).order_by(TicketEntity.id.asc()).all()
        )
        return [self._to_domain(e) for e in entities]

    def get(self, ticketId: int) -> Ticket | None:
        entity = self._session.get(TicketEntity, ticketId)
        return self._to_domain(entity) if entity else None

    def create(self, ticket: Ticket) -> Ticket:
        entity = TicketEntity(
            text=ticket.text,
            department=ticket.department.value,
            priority=ticket.priority.value,
            recommended_action=ticket.recommendedAction,
        )
        self._session.add(entity)
        self._session.commit()
        self._session.refresh(entity)
        return self._to_domain(entity)

    def _to_domain(self, e: TicketEntity) -> Ticket:
        created = e.created_at_utc
        if created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)

        dept = Department(e.department) if e.department in Department._value2member_map_ else Department.Unknown
        pr = TicketPriority(e.priority) if e.priority in TicketPriority._value2member_map_ else TicketPriority.Normal

        return Ticket(
            id=e.id,
            createdAtUtc=created,
            text=e.text,
            department=dept,
            priority=pr,
            recommendedAction=e.recommended_action,
        )