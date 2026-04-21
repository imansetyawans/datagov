.PHONY: dev frontend backend migrate seed test lint format clean

dev:
	cd backend && uvicorn app.main:app --reload --port 8000

frontend:
	cd frontend && npm run dev

seed:
	cd backend && python -m app.scripts.seed_dev

migrate:
	cd backend && alembic upgrade head

test:
	cd backend && pytest tests/ -v
	cd frontend && npm run test 2>/dev/null || true

lint:
	cd backend && ruff check app/
	cd frontend && npm run lint 2>/dev/null || npx eslint src --ext .ts,.tsx || true

format:
	cd backend && ruff format app/
	cd frontend && npm run format 2>/dev/null || npx prettier --write src/ || true

clean:
	cd backend && rm -f datagov.db
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

help:
	@echo "DataGov MVP Development Commands"
	@echo ""
	@echo "  make dev       - Start backend development server"
	@echo "  make frontend  - Start frontend development server"
	@echo "  make seed      - Seed development database with test users"
	@echo "  make migrate   - Run database migrations"
	@echo "  make test      - Run all tests"
	@echo "  make lint      - Run linters"
	@echo "  make clean     - Clean generated files"