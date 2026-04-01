import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from digital_company_ai_support.db.database import Base
from digital_company_ai_support.db.models import TicketEntity  # noqa: F401


@pytest.fixture()
def db_session():
    # ВАЖНО: sqlite:// + StaticPool => один connection, и in-memory БД не "теряется"
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    Base.metadata.create_all(bind=engine)

    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()