from __future__ import annotations

import argparse
import json

import cv2

from src.utils import get_inference_device, load_yolo_model, parse_yolo_result


def main() -> None:
    parser = argparse.ArgumentParser(description="Run YOLOv8 inference on a single image.")
    parser.add_argument("--image", required=True, help="Path to the input image.")
    parser.add_argument("--model", default=None, help="Optional model path override.")
    parser.add_argument("--conf", type=float, default=0.25, help="Confidence threshold.")
    parser.add_argument("--iou", type=float, default=0.45, help="IoU threshold.")
    args = parser.parse_args()

    image = cv2.imread(args.image)
    if image is None:
        raise FileNotFoundError(f"Unable to read image: {args.image}")

    model = load_yolo_model(args.model)
    predict_kwargs = {"conf": args.conf, "iou": args.iou, "verbose": False}
    device = get_inference_device()
    if device:
        predict_kwargs["device"] = device
    result = model.predict(image, **predict_kwargs)[0]
    print(json.dumps(parse_yolo_result(result), indent=2))


if __name__ == "__main__":
    main()
