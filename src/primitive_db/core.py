from primitive_db.parser import parse_value
from primitive_db.utils import load_metadata, load_table_data

VALID_TYPES = {"int", "str", "bool"}


def check_columns(columns_strs):
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


def create_table(metadata, table_name, columns_strs):
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


def drop_table(metadata, table_name):
    """ Проверяет существование таблицы. Если таблицы нет, выводит ошибку.
        Удаляет информацию о таблице из metadata и возвращает обновленный словарь.
        (dict | str)
        """
    if table_name not in metadata:
        return f'Ошибка: Таблица "{table_name}" не существует.'

    del metadata[table_name]
    return metadata


def list_tables(metadata):
    """Возвращает список имён таблиц."""
    return list(metadata.keys())


def insert(metadata, table_name, values):
    """Проверяет, существует ли таблица.
       Проверяет, что количество переданных значений соответствует
       количеству столбцов (минус ID).
       Валидирует типы данных для каждого значения в соответствии со схемой в metadata.
       Генерирует новый ID (например, max(IDs) + 1 или len(data) + 1).
       Добавляет новую запись (в виде словаря) в данные таблицы и возвращает их.
    """
    if table_name not in metadata:
        return f'Ошибка: Таблица "{table_name}" не существует.'

    columns = metadata[table_name]["columns"]
    # ID не учитывается при проверке количества значений
    data_columns = {k: v for k, v in columns.items() if k != "ID"}

    if len(values) != len(data_columns):
        return (f"Некорректное значение: ожидалось "
                f"{len(data_columns)} значений, получено {len(values)}. "
                "Попробуйте снова.")

    data_col_names = list(data_columns.keys())
    converted_values = []
    for val, col_name in zip(values, data_col_names):
        col_type = data_columns[col_name]
        try:
            converted_values.append(parse_value(val, col_type))
        except (ValueError, TypeError):
            return (f"Некорректное значение: {val} "
                    f"не может быть преобразовано в {col_type}. "
                    "Попробуйте снова.")

    data = load_table_data(table_name)
    new_id = max((row.get("ID", 0) for row in data), default=0) + 1

    new_row = {"ID": new_id}
    new_row.update(zip(data_col_names, converted_values))

    data.append(new_row)
    return data


def select(table_data, where_clause=None):
    """ Если where_clause не задан, возвращает все данные.
        Если задан (например, {'age': 28}),
        фильтрует и возвращает только подходящие записи."""
    if not table_data:
        return []

    if where_clause is None:
        return table_data

    result = []
    for row in table_data:
        match = True
        for col_name, value in where_clause.items():
            if row.get(col_name) != value:
                match = False
                break
        if match:
            result.append(row)
    return result


def update(table_data, set_clause, where_clause):
    """ Находит записи по where_clause.
        Обновляет в найденных записях поля согласно set_clause.
        Возвращает измененные данные
    """
    if not table_data:
        return "Ошибка: Таблица пуста."

    for row in table_data:
        match = True
        for col_name, value in where_clause.items():
            if row.get(col_name) != value:
                match = False
                break
        if match:
            for col_name, new_value in set_clause.items():
                row[col_name] = new_value

    return table_data


def delete(table_data, where_clause):
    """ Находит записи по where_clause и удаляет их.
        Возвращает измененные данные.
    """
    if not table_data:
        return "Ошибка: Таблица пуста."

    remaining = []
    for row in table_data:
        match = True
        for col_name, value in where_clause.items():
            if row.get(col_name) != value:
                match = False
                break
        if not match:
            remaining.append(row)
    return remaining


def info(table_name):
    """Возвращает информацию о таблице или None если таблица не найдена."""
    metadata = load_metadata("db_meta.json")
    if table_name not in metadata:
        return f'Ошибка: Таблица "{table_name}" не существует.'

    columns = metadata[table_name]["columns"]
    columns_str = ", ".join(f"{name}:{col_type}"
                            for name, col_type in columns.items())
    data = load_table_data(table_name)
    count = len(data)

    return (f'Таблица: {table_name}\n'
            f'Столбцы: {columns_str}\n'
            f'Количество записей: {count}')
