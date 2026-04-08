FROM python:3.11-slim

WORKDIR /mlflow

RUN pip install --no-cache-dir mlflow==2.16.2

CMD ["sh", "-c", "mlflow server --host 0.0.0.0 --port 5000 --backend-store-uri ${MLFLOW_BACKEND_STORE_URI} --artifacts-destination ${MLFLOW_ARTIFACT_ROOT}"]

