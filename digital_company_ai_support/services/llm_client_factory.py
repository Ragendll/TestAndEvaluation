from openai import OpenAI


def create_openai_client(api_key: str, base_url: str, timeout_seconds: float, max_retries: int) -> OpenAI:
    """
    OpenAI-совместимый клиент с кастомным base_url.
    """
    return OpenAI(
        api_key=api_key,
        base_url=base_url,
        timeout=timeout_seconds,
        max_retries=max_retries,
    )