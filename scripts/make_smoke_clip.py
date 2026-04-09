from __future__ import annotations

import argparse
from pathlib import Path

try:
    import cv2
except ModuleNotFoundError as exc:
    raise SystemExit(
        "OpenCV is required to run scripts/make_smoke_clip.py. "
        "Install project dependencies first or run the script from the API container."
    ) from exc


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create a short smoke-test video by repeating a single image frame."
    )
    parser.add_argument("--image", required=True, help="Path to the source image.")
    parser.add_argument("--output", required=True, help="Path to the output video file.")
    parser.add_argument("--frames", type=int, default=10, help="Number of frames to emit.")
    parser.add_argument("--fps", type=float, default=5.0, help="Frames per second for the output video.")
    args = parser.parse_args()

    image_path = Path(args.image)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    frame = cv2.imread(str(image_path))
    if frame is None:
        raise FileNotFoundError(f"Unable to read image: {image_path}")

    height, width = frame.shape[:2]
    writer = cv2.VideoWriter(
        str(output_path),
        cv2.VideoWriter_fourcc(*"mp4v"),
        args.fps,
        (width, height),
    )

    for _ in range(args.frames):
        writer.write(frame)
    writer.release()

    print(output_path)


if __name__ == "__main__":
    main()
