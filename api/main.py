from __future__ import annotations

from fastapi import FastAPI

from api.routes.detect import router as detect_router
from api.routes.track import router as track_router

app = FastAPI(
    title="aerotrack API",
    description="Aerial object detection and multi-object tracking for drone video.",
    version="0.1.0",
)

app.include_router(detect_router)
app.include_router(track_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

