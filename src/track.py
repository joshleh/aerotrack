from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

import cv2
import numpy as np
import supervision as sv

from src.utils import (
    annotate_frame,
    get_inference_imgsz,
    get_inference_device,
    get_track_max_frames,
    load_yolo_model,
    save_json,
)


def _transcode_for_browser(video_path: str) -> str:
    ffmpeg_binary = shutil.which("ffmpeg")
    if ffmpeg_binary is None:
        return video_path

    source_path = Path(video_path)
    transcoded_path = source_path.with_name(f"{source_path.stem}_browser{source_path.suffix}")

    command = [
        ffmpeg_binary,
        "-y",
        "-i",
        str(source_path),
        "-an",
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-movflags",
        "+faststart",
        str(transcoded_path),
    ]

    try:
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except (OSError, subprocess.CalledProcessError):
        if transcoded_path.exists():
            transcoded_path.unlink()
        return video_path

    transcoded_path.replace(source_path)
    return str(source_path)


def track_video(
    video_path: str,
    output_video_path: str,
    output_json_path: str,
    model_path: str | None = None,
    conf: float = 0.25,
    iou: float = 0.45,
) -> dict[str, Any]:
    model = load_yolo_model(model_path)
    tracker = sv.ByteTrack()
    device = get_inference_device()
    imgsz = get_inference_imgsz()
    max_frames = get_track_max_frames()

    capture = cv2.VideoCapture(video_path)
    if not capture.isOpened():
        raise FileNotFoundError(f"Unable to open video: {video_path}")

    fps = capture.get(cv2.CAP_PROP_FPS) or 30.0
    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

    Path(output_video_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_json_path).parent.mkdir(parents=True, exist_ok=True)

    writer = cv2.VideoWriter(
        output_video_path,
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (width, height),
    )

    frame_results: list[dict[str, Any]] = []
    frame_index = 0

    while True:
        if max_frames is not None and frame_index >= max_frames:
            break

        success, frame = capture.read()
        if not success:
            break

        predict_kwargs = {"conf": conf, "iou": iou, "verbose": False}
        if device:
            predict_kwargs["device"] = device
        if imgsz:
            predict_kwargs["imgsz"] = imgsz
        result = model.predict(frame, **predict_kwargs)[0]
        detections = sv.Detections.from_ultralytics(result)
        tracked = tracker.update_with_detections(detections)

        frame_objects: list[dict[str, Any]] = []
        if tracked.xyxy is not None and len(tracked.xyxy) > 0:
            class_ids = tracked.class_id if tracked.class_id is not None else np.zeros(len(tracked.xyxy), dtype=int)
            confidences = tracked.confidence if tracked.confidence is not None else np.zeros(len(tracked.xyxy), dtype=float)
            tracker_ids = tracked.tracker_id if tracked.tracker_id is not None else np.full(len(tracked.xyxy), -1)

            for bbox, class_id, confidence, track_id in zip(
                tracked.xyxy,
                class_ids,
                confidences,
                tracker_ids,
            ):
                class_index = int(class_id)
                class_label = result.names.get(class_index, str(class_index))
                frame_objects.append(
                    {
                        "track_id": int(track_id),
                        "bbox": [round(float(value), 2) for value in bbox.tolist()],
                        "class_id": class_index,
                        "class_label": class_label,
                        "confidence": round(float(confidence), 4),
                    }
                )

        writer.write(annotate_frame(frame, frame_objects))
        frame_results.append({"frame_index": frame_index, "objects": frame_objects})
        frame_index += 1

    capture.release()
    writer.release()
    output_video_path = _transcode_for_browser(output_video_path)

    payload = {
        "video_path": video_path,
        "annotated_video_path": output_video_path,
        "frames": frame_results,
    }
    save_json(payload, output_json_path)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Run YOLOv8 + ByteTrack on a video file.")
    parser.add_argument("--video", required=True, help="Path to the input video.")
    parser.add_argument("--output-video", required=True, help="Path for the annotated video.")
    parser.add_argument("--output-json", required=True, help="Path for frame-wise tracking JSON.")
    parser.add_argument("--model", default=None, help="Optional model path override.")
    parser.add_argument("--conf", type=float, default=0.25, help="Detection confidence threshold.")
    parser.add_argument("--iou", type=float, default=0.45, help="Detection IoU threshold.")
    args = parser.parse_args()

    result = track_video(
        video_path=args.video,
        output_video_path=args.output_video,
        output_json_path=args.output_json,
        model_path=args.model,
        conf=args.conf,
        iou=args.iou,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
