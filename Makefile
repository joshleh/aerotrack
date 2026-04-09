PYTHON ?= python3
COMPOSE ?= docker-compose
API_URL ?= http://localhost:8000
MLFLOW_URL ?= http://localhost:5001
IMAGE ?=
VIDEO ?=

.PHONY: up down logs health detect-smoke track-smoke train-smoke test

up:
	$(COMPOSE) up --build

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f

health:
	curl -sS $(API_URL)/health

detect-smoke:
	curl -sS -X POST $(API_URL)/detect -F "file=@$(IMAGE)"

track-smoke:
	curl -sS -X POST $(API_URL)/track -F "file=@$(VIDEO)"

train-smoke:
	$(COMPOSE) exec api python -m src.train --data data/visdrone/VisDrone.yaml --epochs 1 --imgsz 640 --batch 2 --mlflow-tracking-uri http://mlflow:5000

test:
	$(PYTHON) -m unittest discover -s tests -p 'test_*.py' -v
