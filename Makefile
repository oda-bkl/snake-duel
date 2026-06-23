.PHONY: help \
        install install-backend install-frontend \
        dev dev-backend dev-frontend \
        test test-backend test-frontend \
        lint lint-backend lint-frontend \
        format format-backend format-frontend \
        build

# ── Default target ────────────────────────────────────────────────────────────

help:
	@grep -E '^[a-zA-Z_-]+:.*?##' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-22s\033[0m %s\n", $$1, $$2}'

# ── Install ───────────────────────────────────────────────────────────────────

install: install-backend install-frontend  ## Install all dependencies

install-backend:  ## Install Python dependencies (uv)
	cd backend && uv sync

install-frontend:  ## Install Node dependencies (npm)
	cd frontend && npm install

# ── Dev servers ───────────────────────────────────────────────────────────────

dev-backend:  ## Start the FastAPI dev server on :8000
	cd backend && uv run uvicorn main:app --reload --port 8000

dev-frontend:  ## Start the Vite dev server on :8080
	cd frontend && npm run dev

# ── Tests ─────────────────────────────────────────────────────────────────────

test: test-backend test-frontend  ## Run all tests

test-backend:  ## Run Python tests (pytest)
	cd backend && uv run pytest tests/ -v

test-frontend:  ## Run frontend tests (vitest)
	cd frontend && npm run test

# ── Lint ──────────────────────────────────────────────────────────────────────

lint: lint-backend lint-frontend  ## Lint everything

lint-backend:  ## Lint Python with ruff
	cd backend && uv run ruff check .

lint-frontend:  ## Lint TypeScript with eslint
	cd frontend && npm run lint

# ── Format ────────────────────────────────────────────────────────────────────

format: format-backend format-frontend  ## Format everything

format-backend:  ## Format Python with ruff
	cd backend && uv run ruff format .

format-frontend:  ## Format TypeScript/CSS with prettier
	cd frontend && npm run format

# ── Build ─────────────────────────────────────────────────────────────────────

build:  ## Build the frontend for production
	cd frontend && npm run build
