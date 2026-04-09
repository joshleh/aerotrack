PYTHON ?= python3
COMPOSE ?= docker-compose
API_URL ?= http://localhost:8000
MLFLOW_URL ?= http://localhost:5001
IMAGE ?=
VIDEO ?=
OUTPUT ?= outputs/smoke.mp4

.PHONY: up down logs health detect-smoke track-smoke train-smoke make-smoke-clip make-smoke-clip-api test

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

make-smoke-clip:
	$(PYTHON) scripts/make_smoke_clip.py --image $(IMAGE) --output $(OUTPUT)

make-smoke-clip-api:
	$(COMPOSE) exec api python scripts/make_smoke_clip.py --image $(IMAGE) --output $(OUTPUT)

test:
	$(PYTHON) -m unittest discover -s tests -p 'test_*.py' -v
