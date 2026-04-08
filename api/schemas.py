from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class Detection(BaseModel):
    bbox: list[float] = Field(..., description="[x1, y1, x2, y2]")
    class_id: int
    class_label: str
    confidence: float


class DetectResponse(BaseModel):
    detections: list[Detection]


class TrackedObject(BaseModel):
    track_id: int
    bbox: list[float] = Field(..., description="[x1, y1, x2, y2]")
    class_id: int
    class_label: str
    confidence: float


class FrameTrackingResult(BaseModel):
    frame_index: int
    objects: list[TrackedObject]


class TrackResponse(BaseModel):
    frames: list[FrameTrackingResult]
    annotated_video_path: str | None = None
    metadata: dict[str, Any] | None = None

