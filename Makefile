.DEFAULT_GOAL := help
SHELL := bash

.PHONY:run check test help

ALEMBIC_CONFIG = src/configs/alembic.ini

# Запускаем проект
run:
	uv run uvicorn src.app:app --reload

# Проверяем линтером
check:
	@echo Running project linters...
	uv run ruff check src

# Делаем автоформат
format:
	@echo Running project formaters...
	uv run ruff format src


# Запускаем тесты
test:
	uv run pytest

test-coverage:
	uv run coverage run -m pytest

test-coverage-report:
	uv run coverage report --show-missing

check-alembic:
	@command -v alembic >/dev/null 2>&1 || { echo "Alembic is not installed. Run 'make install'."; exit 1; }

revision: check-alembic
	alembic -c $(ALEMBIC_CONFIG) revision -m '$(msg)' --autogenerate

upgrade: check-alembic
	alembic -c $(ALEMBIC_CONFIG) upgrade head

downgrade: check-alembic
	alembic -c $(ALEMBIC_CONFIG) downgrade -1

# Список команд
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
