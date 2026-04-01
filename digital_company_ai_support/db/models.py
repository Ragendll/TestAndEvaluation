from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from digital_company_ai_support.db.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class TicketEntity(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    created_at_utc: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    text: Mapped[str] = mapped_column(Text, nullable=False)

    department: Mapped[str] = mapped_column(String(16), default="Unknown", nullable=False)
    priority: Mapped[str] = mapped_column(String(16), default="Normal", nullable=False)
    recommended_action: Mapped[str] = mapped_column(Text, default="", nullable=False)