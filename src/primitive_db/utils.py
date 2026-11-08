import json
import os

from primitive_db.constants import DATA_DIR


def load_metadata(filepath: str):
    """Загружает метаданные из JSON-файла.
    Если файл не найден, возвращает пустой словарь.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_metadata(filepath: str, data: dict):
    """Сохраняет метаданные в JSON-файл."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_data_path(table_name: str):
    """Возвращает путь к файлу данных таблицы."""
    return os.path.join(DATA_DIR, f"{table_name}.json")


def load_table_data(table_name: str):
    """Загружает данные таблицы из JSON-файла.
    Если файл не найден, возвращает пустой список.
    """
    try:
        with open(get_data_path(table_name), "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_table_data(table_name: str, data: list):
    """Сохраняет данные таблицы в JSON-файл, создавая директорию при необходимости."""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(get_data_path(table_name), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
