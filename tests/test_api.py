from fastapi.testclient import TestClient

from digital_company_ai_support.main import app
from digital_company_ai_support.dependencies import get_db_session, get_routing_service
from digital_company_ai_support.services.routing_service import RoutingService
from digital_company_ai_support.services.iticket_classifier import ITicketClassifier
from digital_company_ai_support.models.department import Department


class FakeClassifier(ITicketClassifier):
    def predictDepartment(self, text: str) -> Department:
        if "vpn" in text.lower():
            return Department.It
        return Department.Support


def test_api_create_ticket_enriched(db_session):
    def _get_test_db():
        yield db_session

    app.dependency_overrides[get_db_session] = _get_test_db
    app.dependency_overrides[get_routing_service] = lambda: RoutingService(FakeClassifier())

    client = TestClient(app)

    resp = client.post(
        "/api/tickets",
        content="VPN не работает, срочно",
        headers={"Content-Type": "text/plain"},
    )
    assert resp.status_code == 201

    data = resp.json()
    assert data["id"] == 1
    assert data["department"] == "It"
    assert data["recommendedAction"]

    app.dependency_overrides.clear()