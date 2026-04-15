import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

from digital_company_ai_support.models.department import Department
from digital_company_ai_support.services.iticket_classifier import ITicketClassifier


@dataclass(frozen=True)
class DatasetItem:
    text: str
    expected: Department


def load_dataset(path: str) -> List[DatasetItem]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    items: List[DatasetItem] = []
    for row in raw:
        items.append(DatasetItem(text=row["text"], expected=Department(row["expectedDepartment"])))
    return items


def _labels() -> List[Department]:
    return [
        Department.Support,
        Department.Sales,
        Department.Hr,
        Department.It,
        Department.Finance,
        Department.Unknown,
    ]


def evaluate_classifier(classifier: ITicketClassifier, items: List[DatasetItem]) -> Dict:
    """
    Возвращает:
    - accuracy
    - confusion[expected][predicted] = count
    - per_class: precision/recall/f1/support
    """
    labels = _labels()
    confusion: Dict[str, Dict[str, int]] = {
        label.value: {p.value: 0 for p in labels} for label in labels
    }

    correct = 0
    for it in items:
        pred = classifier.predictDepartment(it.text)
        if pred == it.expected:
            correct += 1
        confusion[it.expected.value][pred.value] += 1

    total = len(items)
    accuracy = correct / total if total else 0.0

    per_class = {}
    for c in labels:
        prec, rec, f1, support = _class_metrics(confusion, c.value)
        per_class[c.value] = {
            "precision": prec,
            "recall": rec,
            "f1": f1,
            "support": support,
        }

    return {
        "total": total,
        "correct": correct,
        "accuracy": accuracy,
        "confusion": confusion,
        "per_class": per_class,
    }


def _class_metrics(confusion: Dict[str, Dict[str, int]], cls: str) -> Tuple[float, float, float, int]:
    tp = confusion[cls][cls]
    support = sum(confusion[cls].values())  # actual count
    fp = sum(confusion[other][cls] for other in confusion.keys() if other != cls)
    fn = sum(confusion[cls][other] for other in confusion[cls].keys() if other != cls)

    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
    return precision, recall, f1, support


def format_report(result: dict) -> str:
    confusion = result["confusion"]
    per_class = result.get("per_class", {})

    labels = list(confusion.keys())  # ожидаемые классы (строки)

    def predicted_count(cls: str) -> int:
        # сколько раз модель вообще выдала этот класс (сумма по столбцу)
        return sum(confusion[exp].get(cls, 0) for exp in labels)

    lines = []
    lines.append(f"Проверено обращений: {result['total']}")
    lines.append(f"Правильно определено: {result['correct']} ({result['accuracy']:.2%})")
    lines.append("")
    lines.append("Как понимать цифры:")
    lines.append("- точность (precision): если модель сказала «X», как часто она права")
    lines.append("- полнота (recall): из всех настоящих «X» сколько модель нашла")
    lines.append("- F1: баланс точности и полноты (1.0 хорошо, 0.0 плохо)")
    lines.append("- n: сколько примеров этого класса в датасете")
    lines.append("")

    lines.append("Итог по каждому отделу:")
    for cls in labels:
        row = confusion[cls]
        total_actual = sum(row.values())
        correct = row.get(cls, 0)

        # топ ошибок (с чем путает этот класс)
        mistakes = [(k, v) for k, v in row.items() if k != cls and v > 0]
        mistakes.sort(key=lambda x: x[1], reverse=True)

        m = per_class.get(cls, {})
        precision = m.get("precision", 0.0)
        recall = m.get("recall", 0.0)
        f1 = m.get("f1", 0.0)

        line = (
            f"- {cls}: угадано {correct}/{total_actual} "
            f"(полнота {recall:.0%}), "
            f"точность {precision:.0%}, F1 {f1:.2f}, "
            f"модель сказала «{cls}» {predicted_count(cls)} раз"
        )

        if mistakes:
            line += ". Чаще всего путает с: " + ", ".join([f"{k} ({v})" for k, v in mistakes[:3]])
        lines.append(line)

    lines.append("")
    lines.append("Таблица ошибок (ожидали → предсказала):")
    for exp in labels:
        lines.append(f"- {exp}: {confusion[exp]}")

    return "\n".join(lines)