from abc import ABC, abstractmethod
from typing import Iterable

from digital_company_ai_support.models.ticket import Ticket


class ITicketRepository(ABC):
    @abstractmethod
    def getAll(self) -> Iterable[Ticket]:
        raise NotImplementedError

    @abstractmethod
    def get(self, ticketId: int) -> Ticket | None:
        raise NotImplementedError

    @abstractmethod
    def create(self, ticket: Ticket) -> Ticket:
        raise NotImplementedError