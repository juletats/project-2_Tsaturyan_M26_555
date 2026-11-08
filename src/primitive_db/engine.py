import shlex

from prettytable import PrettyTable

from primitive_db.core import (
    create_table,
    delete,
    drop_table,
    info,
    insert,
    list_tables,
    select,
    update,
)
from primitive_db.parser import (
    convert_types,
    parse_set,
    parse_value,
    parse_values,
    parse_where,
)
from primitive_db.utils import (
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)

META_FILE = "db_meta.json"

MENU_TITLE = "***<База данных>***"

MENU_SECTIONS = (
    ("Управление таблицами", (
        "<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу",
        "<command> list_tables - показать список всех таблиц",
        "<command> drop_table <имя_таблицы> - удалить таблицу",
    )),
    ("Операции с данными", (
        "<command> insert into <имя_таблицы> values (..) - создать запись",
        "<command> select from <имя_таблицы> where .. - прочитать по условию",
        "<command> select from <имя_таблицы> - прочитать все записи",
        "<command> update <имя_таблицы> set .. where .. - обновить запись",
        "<command> delete from <имя_таблицы> where .. - удалить запись",
        "<command> info <имя_таблицы> - информация о таблице",
    )),
    ("Общие команды", (
        "<command> exit - выход из программы",
        "<command> help - справочная информация",
    )),
)


def print_help():
    """ Печатает меню всех доступных команд."""
    print(f"\n{MENU_TITLE}")
    for title, lines in MENU_SECTIONS:
        print(f"\n{title}:")
        for line in lines:
            print(line)


def format_columns(columns):
    """ Форматирует столбцы в строку вида: 'ID:int, name:str'"""
    parts = [f"{name}:{col_type}" for name, col_type in columns.items()]
    return ", ".join(parts)


def format_ids(rows):
    """ Форматирует ID записей в строку вида: '1, 2'"""
    return ", ".join(str(row["ID"]) for row in rows)


def print_table(data, columns):
    """ Выводит данные в виде красивой таблицы через PrettyTable."""
    if not data:
        print("Записи не найдены.")
        return

    col_names = list(columns.keys())
    table = PrettyTable()
    table.field_names = col_names

    for row in data:
        table_row = [row.get(col, "") for col in col_names]
        table.add_row(table_row)

    print(table)


def find_keyword(args, keyword):
    """ Возвращает индекс ключевого слова или None."""
    for i, token in enumerate(args):
        if token == keyword:
            return i
    return None


def load_table(metadata, table_name):
    """ Загружает схему и данные таблицы, приводя значения к типам схемы.
        Возвращает (columns, table_data) или строку с ошибкой.
    """
    if table_name not in metadata:
        return f'Ошибка: Таблица "{table_name}" не существует.'

    columns = metadata[table_name]["columns"]
    return columns, convert_types(load_table_data(table_name), columns)


def parse_values_arg(user_input):
    """ Извлекает значения из команды insert, сохраняя кавычки исходной строки.
        Возвращает список строк или сообщение об ошибке.
    """
    paren_idx = user_input.find("(")
    if paren_idx == -1:
        return ("Некорректное значение: заключите значения в скобки. "
                "Попробуйте снова.")

    try:
        values = parse_values(user_input[paren_idx:])
    except ValueError:
        return ("Некорректное значение: неверный формат значений. "
                "Попробуйте снова.")

    if not values:
        return "Некорректное значение: укажите значения. Попробуйте снова."

    return values


def convert_set_values(set_clause, columns, table_name):
    """ Переобразует значения set-условия к типам столбцов схемы. """
    converted = {}
    for col_name, value in set_clause.items():
        if col_name not in columns:
            return (f'Некорректное значение: столбец "{col_name}" '
                    f'не существует в таблице "{table_name}". '
                    "Попробуйте снова.")
        try:
            converted[col_name] = parse_value(value, columns[col_name])
        except (ValueError, TypeError):
            return (f"Некорректное значение: {value} "
                    f"не может быть преобразовано в "
                    f"{columns[col_name]}. "
                    "Попробуйте снова.")
    return converted


def handle_create_table(metadata, args):
    """Обрабатывает create_table. Возвращает метаданные."""
    if not args:
        print("Некорректное значение: укажите имя "
              "таблицы и столбцы. Попробуйте снова.")
        return metadata

    table_name = args[0]
    if not args[1:]:
        print("Некорректное значение: укажите хотя бы "
              "один столбец. Попробуйте снова.")
        return metadata

    result = create_table(metadata, table_name, args[1:])
    if isinstance(result, str):
        print(result)
        return metadata

    columns_str = format_columns(result[table_name]["columns"])
    print(f'Таблица "{table_name}" успешно создана '
          f'со столбцами: {columns_str}')
    save_metadata(META_FILE, result)
    return result


def handle_drop_table(metadata, args):
    """Обрабатывает drop_table. Возвращает метаданные."""
    if not args:
        print("Некорректное значение: укажите имя таблицы. Попробуйте снова.")
        return metadata

    table_name = args[0]
    result = drop_table(metadata, table_name)
    if isinstance(result, str):
        print(result)
        return metadata

    print(f'Таблица "{table_name}" успешно удалена.')
    save_metadata(META_FILE, result)
    return result


def handle_list_tables(metadata):
    """Обрабатывает list_tables."""
    tables = list_tables(metadata)
    if not tables:
        print("Таблицы отсутствуют.")
        return

    for table in tables:
        print(f"- {table}")


def handle_insert(metadata, args, user_input):
    """Обрабатывает insert into <таблица> values (..)"""
    if len(args) < 4 or args[0] != "into" or args[2] != "values":
        print("Некорректное значение: используйте формат "
              "'insert into <table> values (..)'. "
              "Попробуйте снова.")
        return

    table_name = args[1]
    values = parse_values_arg(user_input)
    if isinstance(values, str):
        print(values)
        return

    result = insert(metadata, table_name, values)
    if isinstance(result, str):
        print(result)
        return

    save_table_data(table_name, result)
    print(f'Запись с ID={result[-1]["ID"]} успешно добавлена '
          f'в таблицу "{table_name}".')


def handle_select(metadata, args):
    """Обрабатывает select from <таблица> [where ..]"""
    if len(args) < 2 or args[0] != "from":
        print("Некорректное значение: используйте формат "
              "'select from <table> [where ...]'. "
              "Попробуйте снова.")
        return

    where_clause = None
    if len(args) >= 4 and args[2] == "where":
        where_clause = parse_where(" ".join(args[3:]))
        if isinstance(where_clause, str):
            print(where_clause)
            return

    loaded = load_table(metadata, args[1])
    if isinstance(loaded, str):
        print(loaded)
        return

    columns, table_data = loaded
    print_table(select(table_data, where_clause), columns)


def handle_update(metadata, args):
    """Обрабатывает update <таблица> set .. where .."""
    if not args:
        print("Некорректное значение: укажите имя таблицы. "
              "Попробуйте снова.")
        return

    table_name = args[0]
    set_idx = find_keyword(args, "set")
    if set_idx is None:
        print("Некорректное значение: используйте 'set'. "
              "Попробуйте снова.")
        return

    where_idx = find_keyword(args, "where")
    if where_idx is None:
        print("Некорректное значение: используйте 'where'. "
              "Попробуйте снова.")
        return

    set_clause = parse_set(" ".join(args[set_idx + 1:where_idx]))
    if isinstance(set_clause, str):
        print(set_clause)
        return

    where_clause = parse_where(" ".join(args[where_idx + 1:]))
    if isinstance(where_clause, str):
        print(where_clause)
        return

    loaded = load_table(metadata, table_name)
    if isinstance(loaded, str):
        print(loaded)
        return

    columns, table_data = loaded
    converted = convert_set_values(set_clause, columns, table_name)
    if isinstance(converted, str):
        print(converted)
        return

    matched = select(table_data, where_clause)
    result = update(table_data, converted, where_clause)
    if isinstance(result, str):
        print(result)
        return

    if not matched:
        print("Записи не найдены.")
        return

    save_table_data(table_name, result)
    print(f'Запись с ID={format_ids(matched)} в таблице '
          f'"{table_name}" успешно обновлена.')


def handle_delete(metadata, args):
    """Обрабатывает delete from <таблица> where .."""
    if len(args) < 2 or args[0] != "from":
        print("Некорректное значение: используйте формат "
              "'delete from <table> where ...'. "
              "Попробуйте снова.")
        return

    table_name = args[1]
    where_idx = find_keyword(args, "where")
    if where_idx is None:
        print("Некорректное значение: используйте 'where'. "
              "Попробуйте снова.")
        return

    where_clause = parse_where(" ".join(args[where_idx + 1:]))
    if isinstance(where_clause, str):
        print(where_clause)
        return

    loaded = load_table(metadata, table_name)
    if isinstance(loaded, str):
        print(loaded)
        return

    _columns, table_data = loaded
    matched = select(table_data, where_clause)
    result = delete(table_data, where_clause)
    if isinstance(result, str):
        print(result)
        return

    if not matched:
        print("Записи не найдены.")
        return

    save_table_data(table_name, result)
    print(f'Запись с ID={format_ids(matched)} успешно удалена '
          f'из таблицы "{table_name}".')


def handle_info(args):
    """Обрабатывает info <таблица>."""
    if not args:
        print("Некорректное значение: укажите имя таблицы. "
              "Попробуйте снова.")
        return

    result = info(args[0])
    if result:
        print(result)


def read_command():
    """Читает команду пользователя. Возвращает None при EOF."""
    print(">>> Введите команду: ", end="")
    try:
        return input()
    except EOFError:
        print()
        return None


def run():
    """Основной цикл программы."""
    print_help()
    metadata = load_metadata(META_FILE)

    while True:
        user_input = read_command()
        if user_input is None:
            break
        if not user_input.strip():
            continue

        try:
            args = shlex.split(user_input)
        except ValueError:
            print(f"Некорректное значение: {user_input}. "
                  "Попробуйте снова.")
            continue

        if not args:
            continue

        command, rest = args[0], args[1:]

        if command == "create_table":
            metadata = handle_create_table(metadata, rest)
        elif command == "drop_table":
            metadata = handle_drop_table(metadata, rest)
        elif command == "list_tables":
            handle_list_tables(metadata)
        elif command == "insert":
            handle_insert(metadata, rest, user_input)
        elif command == "select":
            handle_select(metadata, rest)
        elif command == "update":
            handle_update(metadata, rest)
        elif command == "delete":
            handle_delete(metadata, rest)
        elif command == "info":
            handle_info(rest)
        elif command == "help":
            print_help()
        elif command == "exit":
            break
        else:
            print(f"Функции {command} нет. Попробуйте снова.")
