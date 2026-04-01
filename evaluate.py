import argparse
from pathlib import Path

from digital_company_ai_support.config import settings
from digital_company_ai_support.evaluation import load_dataset, evaluate_classifier, format_report
from digital_company_ai_support.services.llm_client_factory import create_openai_client
from digital_company_ai_support.services.llm_ticket_classifier import LlmTicketClassifier


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default="dataset.json")
    args = parser.parse_args()

    dataset_path = Path(args.dataset)
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset not found: {dataset_path.resolve()}")

    items = load_dataset(str(dataset_path))

    # Будем использовать реальную LLM (нужны переменные окружения / .env)
    settings.validate()

    client = create_openai_client(
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url,
        timeout_seconds=settings.llm_timeout_seconds,
        max_retries=settings.llm_max_retries,
    )

    classifier = LlmTicketClassifier(client=client, model=settings.llm_model)

    result = evaluate_classifier(classifier, items)
    print(format_report(result))


if __name__ == "__main__":
    main()