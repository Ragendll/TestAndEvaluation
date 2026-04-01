from abc import ABC, abstractmethod

from digital_company_ai_support.models.department import Department


class ITicketClassifier(ABC):
    @abstractmethod
    def predictDepartment(self, text: str) -> Department:
        raise NotImplementedError