from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.responses import FileResponse

from api.artifacts import resolve_artifact_path
from api.routes.detect import router as detect_router
from api.routes.track import router as track_router
from api.ui import render_homepage

app = FastAPI(
    title="aerotrack API",
    description="Aerial object detection and multi-object tracking for drone video.",
    version="0.1.0",
)

app.include_router(detect_router)
app.include_router(track_router)


@app.get("/")
def homepage():
    return render_homepage()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/metadata")
def metadata() -> dict[str, str]:
    return {
        "name": "aerotrack",
        "version": app.version,
        "api_host": os.getenv("API_HOST", "0.0.0.0"),
        "api_port": os.getenv("API_PORT", "8000"),
        "model_path": os.getenv("AEROTRACK_MODEL_PATH", "unset"),
        "device": os.getenv("AEROTRACK_DEVICE", "unset"),
        "mlflow_ui_url": os.getenv("MLFLOW_UI_URL", ""),
    }


@app.get("/artifacts/{artifact_path:path}")
def artifact(artifact_path: str) -> FileResponse:
    artifact_file = resolve_artifact_path(artifact_path)
    return FileResponse(path=artifact_file, filename=artifact_file.name)
