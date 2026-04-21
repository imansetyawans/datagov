.PHONY: dev worker migrate seed test lint format clean

dev:
	uvicorn app.main:app --reload --port 8000

worker:
	celery -A app.workers.celery_app worker --loglevel=info

migrate:
	alembic upgrade head

seed:
	python -m app.scripts.seed_dev

test:
	pytest tests/ -v --cov=app --cov-report=term-missing

lint:
	ruff check app/
	ruff format --check app/

format:
	ruff format app/
	black app/

clean:
	rm -f datagov.db
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete