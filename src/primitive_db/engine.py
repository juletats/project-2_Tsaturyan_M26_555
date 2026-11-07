import shlex

from primitive_db.core import create_table, drop_table, list_tables
from primitive_db.utils import load_metadata, save_metadata

META_FILE = "db_meta.json"


def print_help():
    """Prints the help message for the current mode."""

    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")

    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def format_columns(columns: dict):
    """Форматирует столбцы в строку вида: 'ID:int, name:str'"""
    parts = [f"{name}:{col_type}" for name, col_type in columns.items()]
    return ", ".join(parts)


def run():
    """Основной цикл программы."""
    print("\n***База данных***")
    print("\nФункции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> "
          "<столбец2:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация")

    metadata = load_metadata(META_FILE)

    while True:
        print(">>>Введите команду: ", end="")
        try:
            user_input = input()
        except EOFError:
            print()
            break

        if not user_input.strip():
            continue

        try:
            args = shlex.split(user_input)
        except ValueError:
            print(f"Некорректное значение:{user_input}. "
                  "Попробуйте снова.")
            continue

        if not args:
            continue

        command = args[0]
        rest = args[1:]

        if command == "create_table":
            if len(rest) < 1:
                print("Некорректное значение: укажите имя "
                      "таблицы и столбцы. Попробуйте снова.")
                continue

            table_name = rest[0]
            columns_strs = rest[1:]

            if not columns_strs:
                print("Некорректное значение: укажите хотя бы "
                      "один столбец. Попробуйте снова.")
                continue

            result = create_table(metadata, table_name, columns_strs)
            if isinstance(result, str):
                # Выводим сообщение с ошибкой
                print(result)
            else:
                metadata = result
                table_info = metadata[table_name]
                columns_str = format_columns(table_info["columns"])
                msg = f'Таблица "{table_name}" успешно создана '
                msg += f'со столбцами: {columns_str}'
                print(msg)
                save_metadata(META_FILE, metadata)

        elif command == "drop_table":
            if len(rest) < 1:
                print("Некорректное значение: укажите имя таблицы. Попробуйте снова.")
                continue

            table_name = rest[0]
            result = drop_table(metadata, table_name)
            if isinstance(result, str):
                print(result)
            else:
                metadata = result
                print(f'Таблица "{table_name}" успешно удалена.')
                save_metadata(META_FILE, metadata)

        elif command == "list_tables":
            tables = list_tables(metadata)
            if tables:
                for table in tables:
                    print(f"- {table}")
            else:
                print("Таблицы отсутствуют.")

        elif command == "help":
            print_help()

        elif command == "exit":
            break

        else:
            print(f"Функции {command} нет. Попробуйте снова.")
