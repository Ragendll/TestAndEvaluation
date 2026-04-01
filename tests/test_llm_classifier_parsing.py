from digital_company_ai_support.models.department import Department
from digital_company_ai_support.services.llm_ticket_classifier import LlmTicketClassifier


class _Msg:
    def __init__(self, content: str) -> None:
        self.content = content


class _Choice:
    def __init__(self, content: str) -> None:
        self.message = _Msg(content)


class _Resp:
    def __init__(self, content: str) -> None:
        self.choices = [_Choice(content)]


class FakeChatCompletions:
    def __init__(self, content_to_return: str, raise_on_json_mode: bool = False) -> None:
        self._content = content_to_return
        self._raise_on_json_mode = raise_on_json_mode

    def create(self, **kwargs):
        # симулируем, что response_format может не поддерживаться
        if self._raise_on_json_mode and "response_format" in kwargs:
            raise RuntimeError("response_format not supported")
        return _Resp(self._content)


class FakeChat:
    def __init__(self, content_to_return: str, raise_on_json_mode: bool = False) -> None:
        self.completions = FakeChatCompletions(content_to_return, raise_on_json_mode=raise_on_json_mode)


class FakeOpenAIClient:
    def __init__(self, content_to_return: str, raise_on_json_mode: bool = False) -> None:
        self.chat = FakeChat(content_to_return, raise_on_json_mode=raise_on_json_mode)


def test_llm_classifier_parses_clean_json():
    client = FakeOpenAIClient('{"department":"It","confidence":0.9}')
    clf = LlmTicketClassifier(client=client, model="Qwen3-VL-32B-Thinking-GGUF")
    dept = clf.predictDepartment("VPN не подключается")
    assert dept == Department.It


def test_llm_classifier_parses_json_inside_text():
    client = FakeOpenAIClient('Вот ответ:\n{"department":"Finance","confidence":0.7}\nСпасибо!')
    clf = LlmTicketClassifier(client=client, model="Qwen3-VL-32B-Thinking-GGUF")
    dept = clf.predictDepartment("Нужны закрывающие документы")
    assert dept == Department.Finance


def test_llm_classifier_fallback_when_json_mode_not_supported():
    # Сервер "не поддерживает response_format" -> код должен упасть в fallback
    client = FakeOpenAIClient('{"department":"Support","confidence":0.8}', raise_on_json_mode=True)
    clf = LlmTicketClassifier(client=client, model="Qwen3-VL-32B-Thinking-GGUF")
    dept = clf.predictDepartment("Ошибка 500, не работает логин")
    assert dept == Department.Support