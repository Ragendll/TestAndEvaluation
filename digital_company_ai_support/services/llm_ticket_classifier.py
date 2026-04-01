import json
import logging
import re
from typing import Any, Optional

from digital_company_ai_support.models.department import Department
from digital_company_ai_support.services.iticket_classifier import ITicketClassifier
from digital_company_ai_support.services.errors import LlmUnavailableError

logger = logging.getLogger(__name__)


class LlmTicketClassifier(ITicketClassifier):
    def __init__(self, client: Any, model: str) -> None:
        self._client = client
        self._model = model

    def predictDepartment(self, text: str) -> Department:
        if not text or not text.strip():
            return Department.Unknown

        prompt = self._buildPrompt(text)

        # 1) Попытка JSON mode
        try:
            resp = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": "Ты классификатор обращений. Всегда возвращай только JSON по заданному формату и строго один department из списка."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0,
                response_format={"type": "json_object"},
                max_tokens=200,
            )
            content = (resp.choices[0].message.content or "").strip()
            dept = self._parseDepartment(content)
            return dept
        except Exception as e:
            # ВАЖНО: логируем, но не глушим проблему
            logger.exception("LLM call failed (json mode). base_url/model issue? %s", e)

        # 2) Фолбэк без response_format
        try:
            resp = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": "Ты классификатор обращений. Всегда возвращай только JSON по заданному формату и строго один department из списка."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0,
                max_tokens=200,
            )
            content = (resp.choices[0].message.content or "").strip()
            dept = self._parseDepartment(content)
            return dept

            # Если модель ответила, но не тем форматом — это тоже ошибка интеграции
            # raise LlmUnavailableError(f"LLM returned unparseable response: {content[:200]}")

        except Exception as e:
            logger.exception("LLM call failed (fallback mode). %s", e)
            raise LlmUnavailableError("LLM unavailable or error during request") from e

    def _buildPrompt(self, text: str) -> str:
        return (
            "Твоя задача: определить ОДИН отдел для обращения пользователя.\n"
            "Верни строго JSON без лишнего текста.\n"
            'Формат: {"department":"<Support|Sales|Hr|It|Finance|Unknown>","confidence":0.0}\n'
            "Значение department должно быть РОВНО одним из: Support, Sales, Hr, It, Finance, Unknown.\n\n"

            "Критерии отделов (очень важно):\n"
            "1) Support — проблемы в продукте/приложении для пользователя:\n"
            "   - логин/аккаунт/сброс пароля, ошибка 500/400 в приложении, баг интерфейса, кнопка не работает,\n"
            "   - оплата/транзакция/подписка не проходит (со стороны приложения), доступ к функциям.\n"
            "   Примеры: «Ошибка 500 при входе», «кнопка сохранить не работает», «оплата не проходит».\n\n"

            "2) It — инфраструктура/DevOps/сеть/серверная часть:\n"
            "   - VPN, DNS, домены, SSL/TLS сертификаты, сервер/хост/база, k8s/деплой, мониторинг,\n"
            "   - «не резолвится», «рукопожатие TLS», «деплой упал», «k8s ругается», «сервис не доступен на сервере».\n"
            "   Примеры: «VPN не подключается», «DNS не резолвится», «сертификат истёк», «деплой упал».\n\n"

            "3) Sales — покупка/цены/тарифы/коммерческое предложение:\n"
            "   - КП, прайс, стоимость, расчёт, выставить счёт на покупку тарифа/подписки.\n\n"

            "4) Finance — бухгалтерия и закрывающие документы:\n"
            "   - акт, закрывающие, счет-фактура, сверка, налоги, бухгалтерия.\n\n"

            "5) Hr — кадры/отпуск/больничный/найм:\n"
            "   - отпуск, больничный, оформление сотрудника, резюме, собеседование, вакансия.\n\n"

            "6) Unknown — слишком общее/непонятно куда/без темы:\n"
            "   - «спасибо», «подскажите», «вопрос общего характера», «не уверен куда обратиться».\n\n"

            "Правила выбора при конфликте (ключевые):\n"
            "A) Если в тексте есть явные признаки инфраструктуры/DevOps (VPN/DNS/SSL/TLS/сервер/k8s/деплой/домен/сеть)\n"
            "   — выбирай It, даже если встречаются слова «упал», «не работает», «срочно».\n"
            "B) Если проблема описана как пользовательская в продукте (логин, аккаунт, ошибка 500 в приложении,\n"
            "   баг интерфейса, оплата в приложении) — выбирай Support.\n"
            "C) Фраза «упал сервис авторизации»:\n"
            "   - если это про пользователей/логин/ошибка 500 в приложении → Support;\n"
            "   - если это про инфраструктуру/деплой/k8s/сервер/мониторинг → It.\n"
            "D) Выбирай Unknown только если нет достаточных признаков ни одного отдела.\n\n"

            "Верни только JSON.\n\n"
            f"Текст обращения:\n{text}"
        )

    def _parseDepartment(self, content: str) -> Department:
        data = self._tryLoadJson(content)
        if data and "department" in data:
            return self._safeDepartment(data["department"])

        json_obj = self._extractJsonObject(content)
        data = self._tryLoadJson(json_obj) if json_obj else None
        if data and "department" in data:
            return self._safeDepartment(data["department"])

        return self._safeDepartment(content)

    def _tryLoadJson(self, s: str) -> Optional[dict]:
        try:
            return json.loads(s)
        except Exception:
            return None

    def _extractJsonObject(self, s: str) -> Optional[str]:
        start = s.find("{")
        end = s.rfind("}")
        if start == -1 or end == -1 or end <= start:
            return None
        return s[start : end + 1]

    def _safeDepartment(self, value: str) -> Department:
        raw = (value or "").strip()

        # Попытка прямого Enum (например "It")
        try:
            return Department(raw)
        except Exception:
            pass

        low = raw.lower()
        low = re.sub(r"[^a-z]+", "", low)

        mapping = {
            "support": Department.Support,
            "sales": Department.Sales,
            "hr": Department.Hr,
            "it": Department.It,
            "finance": Department.Finance,
            "unknown": Department.Unknown,
        }
        return mapping.get(low, Department.Unknown)