.PHONY: install lint format run build clean

## Установка зависимостей
install:
	uv sync

## Проверка стиля кода (ruff)
lint:
	uv run ruff check .

## Проверка стиля с автоисправлением
format:
	uv run ruff check . --fix

## Запуск базы данных
run:
	uv run database

## Сборка пакета
build:
	uv build

## Удаление артефактов сборки и кэша
clean:
	rm -rf build dist
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
