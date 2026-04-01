from digital_company_ai_support.models.department import Department
from digital_company_ai_support.services.iticket_classifier import ITicketClassifier


class KeywordTicketClassifier(ITicketClassifier):
    """
    Простой детерминированный классификатор по ключевым словам.
    Нужен для тестов и baseline-оценки (без LLM и без сети).
    """

    def __init__(self) -> None:
        self._keywords: dict[Department, list[str]] = {
            Department.Support: ["не работает", "ошибка", "баг", "упал", "500", "доступ", "логин"],
            Department.Sales: ["счёт", "счет", "коммерчес", "кп", "тариф", "оплата", "купить", "лид", "прайс"],
            Department.Hr: ["отпуск", "больнич", "кадры", "собесед", "резюме", "найм", "ваканси", "интервью"],
            Department.It: ["vpn", "сервер", "devops", "k8s", "сеть", "dns", "ssl", "tls", "домен"],
            Department.Finance: ["акт", "закрывающ", "сверка", "налог", "бух", "счет-фактур", "счёт-фактур"],
        }

    def predictDepartment(self, text: str) -> Department:
        if not text or not text.strip():
            return Department.Unknown

        lower = text.lower()
        best = Department.Unknown
        best_score = 0

        for dep, words in self._keywords.items():
            score = sum(1 for w in words if w in lower)
            if score > best_score:
                best_score = score
                best = dep

        return best if best_score > 0 else Department.Unknown