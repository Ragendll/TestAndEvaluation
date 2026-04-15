import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


class Base(DeclarativeBase):
    pass


def _default_sqlite_url() -> str:
    data_dir = Path(__file__).resolve().parents[2] / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    db_path = data_dir / "tickets.db"
    return f"sqlite:///{db_path.as_posix()}"


DATABASE_URL = os.getenv("DATABASE_URL", _default_sqlite_url())

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db() -> None:
    from digital_company_ai_support.db.models import TicketEntity  # noqa: F401
    Base.metadata.create_all(bind=engine)