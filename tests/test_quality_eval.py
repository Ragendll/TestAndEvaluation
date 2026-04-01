from pathlib import Path

from digital_company_ai_support.evaluation import load_dataset, evaluate_classifier
from digital_company_ai_support.services.keyword_ticket_classifier import KeywordTicketClassifier


def test_quality_on_dataset_keyword_classifier():
    dataset_path = Path(__file__).resolve().parents[1] / "dataset.json"
    items = load_dataset(str(dataset_path))

    result = evaluate_classifier(KeywordTicketClassifier(), items)

    # Порог можно менять. Для текущего dataset должен быть высоким.
    assert result["total"] >= 30
    assert result["accuracy"] >= 0.80