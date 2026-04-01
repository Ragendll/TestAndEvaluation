from digital_company_ai_support.models.department import Department
from digital_company_ai_support.models.ticket import Ticket
from digital_company_ai_support.models.ticket_priority import TicketPriority
from digital_company_ai_support.services.iticket_classifier import ITicketClassifier


class RoutingService:

    def __init__(self, classifier: ITicketClassifier) -> None:
        self._classifier = classifier

    def enrich(self, ticket: Ticket) -> None:
        ticket.department = self._classifier.predictDepartment(ticket.text)
        ticket.priority = self._predictPriority(ticket.text)
        ticket.recommendedAction = self._buildRecommendation(ticket.department)

    def _predictPriority(self, text: str) -> TicketPriority:
        lowerText = (text or "").lower()

        if any(x in lowerText for x in ["срочно", "простой", "прод", "production"]):
            return TicketPriority.Critical

        if any(x in lowerText for x in ["не работает", "упал", "down"]):
            return TicketPriority.High

        return TicketPriority.Normal

    def _buildRecommendation(self, department: Department) -> str:
        if department == Department.Support:
            return "Собрать логи/скриншоты, уточнить шаги воспроизведения, назначить инженера 1-й линии."
        if department == Department.It:
            return "Проверить доступность сервисов, DNS/сеть/сертификаты, мониторинг, при необходимости эскалация DevOps."
        if department == Department.Sales:
            return "Уточнить потребность, подготовить КП/счёт, зафиксировать контакт и срок ответа."
        if department == Department.Hr:
            return "Запросить данные кандидата/сотрудника, применить регламент HR-заявок."
        if department == Department.Finance:
            return "Запросить реквизиты/документы, проверить закрывающие, сверить суммы."
        return "Уточнить детали обращения и выбрать процесс обработки."