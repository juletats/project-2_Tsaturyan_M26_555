import time
from functools import wraps


def handle_db_errors(func):
    """Централизованно перехватывает исключения операций с базой данных.

    Сообщение об ошибке печатается здесь, функция возвращает None.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print("Ошибка: Файл данных не найден. "
                  "Возможно, база данных не инициализирована.")
        except KeyError as e:
            print(f"Ошибка: Таблица или столбец {e} не найден.")
        except ValueError as e:
            print(f"Ошибка валидации: {e}")
        except Exception as e:
            print(f"Произошла непредвиденная ошибка: {e}")
        return None

    return wrapper


def confirm_action(action_name):
    """Фабрика декораторов, запрашивающих подтверждение опасной операции.

    Если пользователь ввёл не "y", операция отменяется и возвращается None.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            question = (f'Вы уверены, что хотите выполнить '
                        f'"{action_name}"? [y/n]: ')
            try:
                answer = input(question)
            except EOFError:
                print()
                answer = ""

            if answer.strip().lower() != "y":
                print("Операция отменена.")
                return None

            return func(*args, **kwargs)

        return wrapper

    return decorator


def log_time(func):
    """ Замеряет время выполнения функции и печатает его в консоль."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.monotonic()
        result = func(*args, **kwargs)
        elapsed = time.monotonic() - start
        print(f"Функция {func.__name__} выполнилась за {elapsed:.3f} секунд.")
        return result

    return wrapper


def create_cacher():
    """ Создаёт функцию кэширования, хранящую кэш в замыкании.
        Возвращает cache_result(key, value_func): при повторном вызове с тем же
        ключом значение берётся из кэша, иначе вычисляется value_func.
    """
    cache = {}

    def cache_result(key, value_func):
        if key not in cache:
            cache[key] = value_func()
        return cache[key]

    def clear():
        """ Очищает кэш — используется после изменения данных."""
        cache.clear()

    cache_result.clear = clear
    return cache_result
