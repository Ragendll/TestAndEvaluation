from fastapi import APIRouter, Body, Depends, HTTPException

from digital_company_ai_support.models.ticket import Ticket
from digital_company_ai_support.repositories.iticket_repository import ITicketRepository
from digital_company_ai_support.services.routing_service import RoutingService
from digital_company_ai_support.dependencies import get_repository, get_routing_service
from digital_company_ai_support.services.errors import LlmUnavailableError

router = APIRouter(prefix="/api/tickets", tags=["tickets"])


@router.get("")
def getAll(repository: ITicketRepository = Depends(get_repository)):
    return repository.getAll()


@router.get("/{ticketId}")
def get(ticketId: int, repository: ITicketRepository = Depends(get_repository)):
    ticket = repository.get(ticketId)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@router.post("", status_code=201)
def create(
    text: str = Body(..., media_type="text/plain", description="Текст обращения"),
    repository: ITicketRepository = Depends(get_repository),
    routing: RoutingService = Depends(get_routing_service),
):
    ticket = Ticket(text=text)

    try:
        routing.enrich(ticket)
    except LlmUnavailableError as e:
        raise HTTPException(status_code=503, detail=str(e))

    created = repository.create(ticket)
    return created