from __future__ import annotations

import logging
import tempfile
from functools import partial
from pathlib import Path

from fastapi import APIRouter, File, UploadFile
from fastapi.concurrency import run_in_threadpool

from api.artifacts import artifact_url_for_path
from api.schemas import TrackResponse
from src.track import track_video
from src.utils import get_env, get_runtime_thresholds

router = APIRouter(tags=["track"])
logger = logging.getLogger(__name__)


@router.post("/track", response_model=TrackResponse)
async def track(file: UploadFile = File(...)) -> TrackResponse:
    logger.info("Starting tracking for upload: %s", file.filename)
    output_root = Path(get_env("AEROTRACK_OUTPUT_DIR"))
    output_root.mkdir(parents=True, exist_ok=True)
    confidence, iou = get_runtime_thresholds()

    with tempfile.TemporaryDirectory() as temp_dir:
        input_path = Path(temp_dir) / file.filename
        input_path.write_bytes(await file.read())

        stem = input_path.stem
        output_video = output_root / f"{stem}_tracked.mp4"
        output_json = output_root / f"{stem}_tracked.json"

        payload = await run_in_threadpool(
            partial(
                track_video,
                video_path=str(input_path),
                output_video_path=str(output_video),
                output_json_path=str(output_json),
                conf=confidence,
                iou=iou,
            )
        )

    response = TrackResponse(
        frames=payload["frames"],
        annotated_video_path=payload["annotated_video_path"],
        metadata={
            "source_filename": file.filename,
            "annotated_video_url": artifact_url_for_path(payload["annotated_video_path"]),
        },
    )
    logger.info("Completed tracking for upload: %s", file.filename)
    return response
