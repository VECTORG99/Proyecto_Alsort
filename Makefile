.PHONY: dev-backend dev-frontend dev build-backend build-frontend build test-backend test-frontend test lint-backend lint-frontend lint clean docker-up docker-down install install-backend install-frontend

# === Development ===

dev-backend:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	cd frontend && npm run dev

dev:
	@echo "Run in separate terminals: make dev-backend & make dev-frontend"

# === Build ===

build-backend:
	docker build -t alsort-backend -f Dockerfile.backend .

build-frontend:
	docker build -t alsort-frontend -f Dockerfile.frontend .

build: build-backend build-frontend

# === Test ===

test-backend:
	cd backend && python -m pytest -v

test-frontend:
	cd frontend && npm run typecheck

test: test-backend test-frontend

# === Lint ===

lint-backend:
	cd backend && ruff check .

lint-frontend:
	cd frontend && npm run lint

lint: lint-backend lint-frontend

# === Docker ===

docker-up:
	docker compose up --build

docker-down:
	docker compose down

# === Install ===

install-backend:
	cd backend && pip install -r requirements.txt

install-frontend:
	cd frontend && npm install

install: install-backend install-frontend

# === Clean ===

clean:
	rm -rf frontend/dist .pytest_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
