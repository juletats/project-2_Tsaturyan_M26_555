import shlex

PUNCTUATION = "(),"


def parse_values(values_str):
    """Парсит список значений вида '("John Doe", 28, true)' в список строк.
    Скобки и запятые как разделители, кавычки сохраняют пробелы.
    """
    lexer = shlex.shlex(values_str, posix=True, punctuation_chars=PUNCTUATION)
    lexer.whitespace_split = True
    return [token for token in lexer if token not in PUNCTUATION]


def parse_value(value_str, col_type):
    """Парсит значение в соответствии с типом столбца.
    Выбрасывается ValueError, если тип неизвестен или значение ему не соответствует.
    """
    if col_type == "int":
        try:
            return int(value_str)
        except (TypeError, ValueError):
            raise ValueError(
                f"{value_str} не может быть преобразовано в int"
            ) from None
    elif col_type == "bool":
        if value_str.lower() not in ("true", "false", "1", "0", "yes", "no"):
            raise ValueError(f"{value_str} не может быть bool")
        return value_str.lower() in ("true", "1", "yes")
    elif col_type == "str":
        return value_str.strip('"').strip("'")
    else:
        raise ValueError(f"неизвестный тип '{col_type}'")


def parse_literal(value_str):
    """Определяет тип литерала: строка в кавычках, bool, int или float."""
    if (value_str.startswith('"') and value_str.endswith('"')) or (
            value_str.startswith("'") and value_str.endswith("'")
    ):
        return value_str[1:-1]  # строка
    elif value_str.lower() in ("true", "false"):
        return value_str.lower() == "true"
    else:
        try:
            return int(value_str)
        except ValueError:
            try:
                return float(value_str)
            except ValueError:
                return value_str


def split_condition(condition_str, keyword):
    """Разбирает условие 'столбец = значение' на пару (имя, значение).

    Возвращает пару или строку с ошибкой.
    """
    if "=" not in condition_str:
        return (f"Некорректное значение: {keyword} ожидает формат "
                "'столбец = значение'. Попробуйте снова.")

    col_name, value_str = condition_str.split("=", 1)
    col_name = col_name.strip()
    value_str = value_str.strip()

    if not col_name:
        return "Некорректное значение: укажите имя столбца. Попробуйте снова."

    if not value_str:
        return "Некорректное значение: укажите значение. Попробуйте снова."

    return col_name, value_str


def parse_where(where_str):
    """Парсит where условие вида 'age = 28' в словарь {'age': 28}.

    Возвращает словарь или строку с ошибкой.
    """
    parsed = split_condition(where_str, "where")
    if isinstance(parsed, str):
        return parsed

    col_name, value_str = parsed
    return {col_name: parse_literal(value_str)}


def parse_set(set_str):
    """Парсит set условие вида 'age = 29' в словарь {'age': '29'}.

    Значения возвращаются как строки для последующей конвертации по схеме.
    Возвращает словарь или строку с ошибкой.
    """
    parsed = split_condition(set_str, "set")
    if isinstance(parsed, str):
        return parsed

    col_name, value_str = parsed
    return {col_name: value_str}


def convert_types(data, columns):
    """Конвертирует строковые значения данных в правильные типы по схеме."""
    col_names = list(columns.keys())
    converted = []
    for row in data:
        if isinstance(row, dict):
            converted.append(row)
        else:
            new_row = {}
            for i, col_name in enumerate(col_names):
                new_row[col_name] = parse_value(str(row[i]), columns[col_name])
            converted.append(new_row)
    return converted
