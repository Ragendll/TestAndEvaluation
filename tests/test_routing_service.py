from digital_company_ai_support.models.department import Department
from digital_company_ai_support.models.ticket import Ticket
from digital_company_ai_support.services.routing_service import RoutingService
from digital_company_ai_support.services.keyword_ticket_classifier import KeywordTicketClassifier


def test_routing_enrich_sets_fields():
    routing = RoutingService(KeywordTicketClassifier())

    ticket = Ticket(text="VPN не работает, срочно, проблема DNS")
    routing.enrich(ticket)

    assert ticket.department == Department.It
    assert ticket.priority.value in ["High", "Critical"]
    assert ticket.recommendedAction != ""