from functools import lru_cache

from fastapi import Depends
from sqlalchemy.orm import Session

from digital_company_ai_support.config import settings
from digital_company_ai_support.db.database import SessionLocal
from digital_company_ai_support.repositories.iticket_repository import ITicketRepository
from digital_company_ai_support.repositories.sql_ticket_repository import SqlTicketRepository
from digital_company_ai_support.services.iticket_classifier import ITicketClassifier
from digital_company_ai_support.services.llm_client_factory import create_openai_client
from digital_company_ai_support.services.llm_ticket_classifier import LlmTicketClassifier
from digital_company_ai_support.services.routing_service import RoutingService


def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_repository(db: Session = Depends(get_db_session)) -> ITicketRepository:
    return SqlTicketRepository(db)


@lru_cache(maxsize=1)
def get_classifier_singleton() -> ITicketClassifier:
    settings.validate()
    client = create_openai_client(
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url,
        timeout_seconds=settings.llm_timeout_seconds,
        max_retries=settings.llm_max_retries,
    )
    return LlmTicketClassifier(client=client, model=settings.llm_model)


def get_classifier() -> ITicketClassifier:
    return get_classifier_singleton()


def get_routing_service(classifier: ITicketClassifier = Depends(get_classifier)) -> RoutingService:
    return RoutingService(classifier)