from __future__ import annotations

import argparse
import shutil
import struct
from pathlib import Path


CLASS_NAMES = [
    "pedestrian",
    "people",
    "bicycle",
    "car",
    "van",
    "truck",
    "tricycle",
    "awning-tricycle",
    "bus",
    "motor",
]


def get_image_size(image_path: Path) -> tuple[int, int]:
    with image_path.open("rb") as handle:
        signature = handle.read(26)

    if signature.startswith(b"\211PNG\r\n\032\n"):
        width, height = struct.unpack(">II", signature[16:24])
        return width, height

    if signature[:2] == b"\xff\xd8":
        with image_path.open("rb") as handle:
            handle.read(2)
            while True:
                marker_start = handle.read(1)
                if marker_start != b"\xff":
                    raise ValueError(f"Invalid JPEG marker in {image_path}")

                marker = handle.read(1)
                while marker == b"\xff":
                    marker = handle.read(1)

                if marker in {
                    b"\xc0",
                    b"\xc1",
                    b"\xc2",
                    b"\xc3",
                    b"\xc5",
                    b"\xc6",
                    b"\xc7",
                    b"\xc9",
                    b"\xca",
                    b"\xcb",
                    b"\xcd",
                    b"\xce",
                    b"\xcf",
                }:
                    handle.read(2)
                    handle.read(1)
                    height, width = struct.unpack(">HH", handle.read(4))
                    return width, height

                if marker in {b"\xd8", b"\xd9"}:
                    continue

                segment_length = struct.unpack(">H", handle.read(2))[0]
                handle.seek(segment_length - 2, 1)

    raise ValueError(f"Unsupported image format: {image_path}")


def ensure_empty_dir(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def resolve_image_path(image_dir: Path, stem: str) -> Path | None:
    for suffix in (".jpg", ".png"):
        candidate = image_dir / f"{stem}{suffix}"
        if candidate.exists():
            return candidate
    return None


def convert_annotations(source_dir: Path, target_dir: Path) -> None:
    annotations_dir = source_dir / "annotations"
    image_dir = source_dir / "images"

    for annotation_path in sorted(annotations_dir.glob("*.txt")):
        image_path = resolve_image_path(image_dir, annotation_path.stem)
        if image_path is None:
            continue

        try:
            width, height = get_image_size(image_path)
        except ValueError:
            continue

        yolo_lines: list[str] = []
        for line in annotation_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue

            parts = [part.strip() for part in line.split(",")]
            while parts and parts[-1] == "":
                parts.pop()
            if len(parts) < 8:
                continue

            x, y, w, h, score, category, truncation, occlusion = map(int, parts[:8])
            if category == 0 or score == 0:
                continue

            x_center = (x + w / 2.0) / width
            y_center = (y + h / 2.0) / height
            norm_w = w / width
            norm_h = h / height
            class_id = category - 1
            yolo_lines.append(
                f"{class_id} {x_center:.6f} {y_center:.6f} {norm_w:.6f} {norm_h:.6f}"
            )

        (target_dir / annotation_path.name).write_text("\n".join(yolo_lines), encoding="utf-8")


def write_dataset_yaml(yolo_dir: Path) -> None:
    yaml_lines = [
        f"path: {yolo_dir.as_posix()}",
        "train: images/train",
        "val: images/val",
        "test: images/test",
        "names:",
    ]
    yaml_lines.extend(f"  {idx}: {name}" for idx, name in enumerate(CLASS_NAMES))
    (yolo_dir / "VisDrone.yaml").write_text("\n".join(yaml_lines) + "\n", encoding="utf-8")


def prepare_dataset(root_dir: Path) -> None:
    data_dir = root_dir / "data"
    raw_dir = data_dir / "raw"
    yolo_dir = data_dir / "visdrone"

    split_map = {
        "train": raw_dir / "VisDrone2019-DET-train",
        "val": raw_dir / "VisDrone2019-DET-val",
        "test": raw_dir / "VisDrone2019-DET-test-dev",
    }

    missing_splits = [str(path) for path in split_map.values() if not path.exists()]
    if missing_splits:
        missing_text = "\n".join(missing_splits)
        raise FileNotFoundError(
            "Missing extracted VisDrone splits. Expected directories:\n"
            f"{missing_text}"
        )

    for split in ("train", "val", "test"):
        ensure_empty_dir(yolo_dir / "images" / split)
    for split in ("train", "val"):
        ensure_empty_dir(yolo_dir / "labels" / split)

    for split, source_dir in split_map.items():
        source_images = source_dir / "images"
        target_images = yolo_dir / "images" / split
        for image_path in sorted(source_images.glob("*")):
            if image_path.is_file():
                shutil.copy2(image_path, target_images / image_path.name)

    for split in ("train", "val"):
        convert_annotations(split_map[split], yolo_dir / "labels" / split)

    write_dataset_yaml(yolo_dir)
    print(f"Prepared YOLO dataset at {yolo_dir}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare the VisDrone dataset in YOLO format.")
    parser.add_argument(
        "--root",
        default=Path(__file__).resolve().parents[1],
        type=Path,
        help="Repository root containing the data/ directory.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    prepare_dataset(args.root.resolve())


if __name__ == "__main__":
    main()
