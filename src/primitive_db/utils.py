import json
from pathlib import Path

DATA_DIR = "data"


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


def get_data_path(table_name: str):
    """Возвращает путь к файлу данных таблицы."""
    return Path(DATA_DIR) / f"{table_name}.json"


def load_table_data(table_name: str):
    """Загружает данные таблицы из JSON-файла.
    Если файл не найден, возвращает пустой список.
    """
    path = get_data_path(table_name)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_table_data(table_name: str, data: list):
    """Сохраняет данные таблицы в JSON-файл."""
    path = get_data_path(table_name)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
