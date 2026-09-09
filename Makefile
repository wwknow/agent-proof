.PHONY: test run docker-up docker-down

test:
	PYTHONPATH=packages/agentproof_verifier:. pytest -q

run:
	PYTHONPATH=packages/agentproof_verifier python -m server.server

docker-up:
	docker compose up --build

docker-down:
	docker compose down
