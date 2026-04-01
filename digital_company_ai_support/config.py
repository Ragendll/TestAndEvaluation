import os
from dotenv import load_dotenv
load_dotenv()
class Settings:

    def __init__(self) -> None:
        self.llm_base_url: str = os.getenv("LLM_BASE_URL")
        self.llm_api_key: str = os.getenv("LLM_API_KEY")
        self.llm_model: str = os.getenv("LLM_MODEL")

        self.llm_timeout_seconds: float = float(os.getenv("LLM_TIMEOUT", "60"))
        self.llm_max_retries: int = int(os.getenv("LLM_MAX_RETRIES", "2"))

    def validate(self) -> None:
        if not self.llm_api_key:
            raise RuntimeError(
                "Не задан LLM_API_KEY. Установите переменную окружения LLM_API_KEY=<key>."
            )


settings = Settings()