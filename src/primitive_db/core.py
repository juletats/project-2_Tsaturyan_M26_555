VALID_TYPES = {"int", "str", "bool"}


def check_columns(columns_strs: list[str]):
    """Проверять корректность типов данных (только int, str, bool).
        Возвращает список (имя столбца, тип данных)"""
    columns = []
    for col in columns_strs:
        if ":" not in col:
            raise ValueError(col)
        name, col_type = col.split(":", 1)
        if col_type not in VALID_TYPES:
            raise ValueError(col_type)
        columns.append((name, col_type))
    return columns


def create_table(metadata: dict, table_name: str, columns_strs: list[str]):
    """ Она должна принимать текущие метаданные, имя таблицы и список столбцов.
        Автоматически добавлять столбец ID:int в начало списка столбцов.
        Проверять, не существует ли уже таблица с таким именем.
        Если да, выводить ошибку.
        Проверять корректность типов данных (только int, str, bool).
        В случае успеха, обновлять словарь metadata и возвращать его. (dict | str) """
    if table_name in metadata:
        return f'Ошибка: Таблица "{table_name}" уже существует.'

    try:
        columns = check_columns(columns_strs)
    except ValueError as e:
        return f'Некорректное значение: {e}. Попробуйте снова.'

    # Проверяем, есть ли уже столбец ID
    has_id = any(name == "ID" for name, _ in columns)

    if has_id:
        all_columns = columns
    else:
        all_columns = [("ID", "int")] + columns

    metadata[table_name] = {
        "columns": {name: col_type for name, col_type in all_columns},
    }
    return metadata


def drop_table(metadata: dict, table_name: str):
    """ Проверяет существование таблицы. Если таблицы нет, выводит ошибку.
        Удаляет информацию о таблице из metadata и возвращает обновленный словарь.
        (dict | str)
        """
    if table_name not in metadata:
        return f'Ошибка: Таблица "{table_name}" не существует.'

    del metadata[table_name]
    return metadata


def list_tables(metadata: dict):
    """Возвращает список имён таблиц."""
    return list(metadata.keys())
