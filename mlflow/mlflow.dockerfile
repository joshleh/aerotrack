FROM python:3.11-slim

LABEL org.opencontainers.image.title="aerotrack-mlflow"
LABEL org.opencontainers.image.description="MLflow tracking server for aerotrack experiments and model artifacts."
LABEL org.opencontainers.image.source="https://github.com/joshleh/aerotrack"

WORKDIR /mlflow

RUN pip install --no-cache-dir mlflow==2.16.2

CMD ["sh", "-c", "mlflow server --host 0.0.0.0 --port 5000 --backend-store-uri ${MLFLOW_BACKEND_STORE_URI} --artifacts-destination ${MLFLOW_ARTIFACT_ROOT}"]
