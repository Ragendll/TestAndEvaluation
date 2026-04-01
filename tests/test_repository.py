from digital_company_ai_support.models.ticket import Ticket
from digital_company_ai_support.repositories.sql_ticket_repository import SqlTicketRepository


def test_repository_create_and_get(db_session):
    repo = SqlTicketRepository(db_session)
    created = repo.create(Ticket(text="Не работает логин"))

    assert created.id == 1
    loaded = repo.get(1)
    assert loaded is not None
    assert loaded.text == "Не работает логин"