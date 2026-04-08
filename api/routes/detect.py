from __future__ import annotations

import cv2
import numpy as np
from fastapi import APIRouter, File, HTTPException, UploadFile

from api.schemas import DetectResponse
from src.utils import (
    get_inference_device,
    get_runtime_thresholds,
    load_yolo_model,
    parse_yolo_result,
)

router = APIRouter(tags=["detect"])


@router.post("/detect", response_model=DetectResponse)
async def detect(file: UploadFile = File(...)) -> DetectResponse:
    contents = await file.read()
    image_array = np.frombuffer(contents, dtype=np.uint8)
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    if image is None:
        raise HTTPException(status_code=400, detail="Uploaded file is not a valid image.")

    model = load_yolo_model()
    confidence, iou = get_runtime_thresholds()
    predict_kwargs = {"conf": confidence, "iou": iou, "verbose": False}
    device = get_inference_device()
    if device:
        predict_kwargs["device"] = device
    result = model.predict(image, **predict_kwargs)[0]
    return DetectResponse(detections=parse_yolo_result(result))
