.PHONY: install dev backend frontend backend-tests backend-integration-tests frontend-tests test docker-build docker-run

install:
	cd backend && uv sync --all-extras
	cd frontend && npm install

dev:
	trap 'kill 0' SIGINT; \
	$(MAKE) backend & \
	$(MAKE) frontend & \
	wait

backend:
	cd backend && uv run python main.py

frontend:
	cd frontend && npm run dev

backend-tests:
	cd backend && uv run pytest tests/

backend-integration-tests:
	cd backend && uv run pytest tests_integration/

frontend-tests:
	cd frontend && npm test

test: backend-tests backend-integration-tests frontend-tests

docker-build:
	docker build -t snake-duel .

docker-run:
	docker run -p 8000:8000 snake-duel
