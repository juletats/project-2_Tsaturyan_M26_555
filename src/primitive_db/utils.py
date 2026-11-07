import json
from pathlib import Path


def load_metadata(filepath: str):
    """Загружает метаданные из JSON-файла.
    Если файл не найден, возвращает пустой словарь.
    """
    path = Path(filepath)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_metadata(filepath: str, data: dict):
    """Сохраняет метаданные в JSON-файл."""
    path = Path(filepath)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
