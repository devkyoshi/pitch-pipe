.PHONY: help install env redis redis-stop redis-logs api worker migrate migrate-down migrate-create test test-file lint format

PYTHON     := python3
PIP        := pip3
VENV       := .venv
VENV_BIN   := $(VENV)/bin
ACTIVATE   := . $(VENV_BIN)/activate

help:
	@echo ""
	@echo "Veo3 Lead Gen Pipeline — local dev commands"
	@echo ""
	@echo "  make install          Create venv and install dependencies"
	@echo "  make env              Copy .env.example → .env (skip if .env exists)"
	@echo "  make redis            Start Redis container on :6379"
	@echo "  make redis-stop       Stop and remove Redis container"
	@echo "  make redis-logs       Tail Redis container logs"
	@echo "  make api              Start FastAPI dev server on :8000"
	@echo "  make worker           Start Celery worker"
	@echo "  make migrate          Run all pending Alembic migrations"
	@echo "  make migrate-down     Roll back the last migration"
	@echo "  make migrate-create   Create a new empty migration  (NAME=your_name)"
	@echo "  make test             Run full pytest suite"
	@echo "  make test-file        Run one test file            (FILE=tests/test_webhook.py)"
	@echo "  make lint             Run ruff linter"
	@echo "  make format           Auto-format with ruff"
	@echo ""

# ── Setup ────────────────────────────────────────────────────────────────────

install:
	$(PYTHON) -m venv $(VENV)
	$(ACTIVATE) && $(PIP) install --upgrade pip
	$(ACTIVATE) && $(PIP) install -r requirements.txt
	@echo "\n✓ Virtualenv ready. Activate with:  source $(VENV_BIN)/activate"

env:
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "✓ .env created from .env.example — fill in your API keys"; \
	else \
		echo "✓ .env already exists — skipping"; \
	fi

# ── Services ─────────────────────────────────────────────────────────────────

redis:
	@if docker ps -a --format '{{.Names}}' | grep -q '^redis$$'; then \
		docker start redis; \
	else \
		docker run -d --name redis -p 6379:6379 redis:7-alpine; \
	fi

redis-stop:
	docker stop redis && docker rm redis

redis-logs:
	docker logs -f redis

api:
	$(ACTIVATE) && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

worker:
	$(ACTIVATE) && celery -A app.tasks.pipeline_task.app_celery worker --loglevel=info --concurrency=2

# ── Database ─────────────────────────────────────────────────────────────────

migrate:
	$(ACTIVATE) && alembic upgrade head

migrate-down:
	$(ACTIVATE) && alembic downgrade -1

migrate-create:
	@if [ -z "$(NAME)" ]; then echo "Usage: make migrate-create NAME=your_migration_name" && exit 1; fi
	$(ACTIVATE) && alembic revision --autogenerate -m "$(NAME)"

# ── Tests ────────────────────────────────────────────────────────────────────

test:
	$(ACTIVATE) && pytest tests/ -v

test-file:
	@if [ -z "$(FILE)" ]; then echo "Usage: make test-file FILE=tests/test_webhook.py" && exit 1; fi
	$(ACTIVATE) && pytest $(FILE) -v

# ── Code quality ─────────────────────────────────────────────────────────────

lint:
	$(ACTIVATE) && ruff check app/ tests/

format:
	$(ACTIVATE) && ruff format app/ tests/
