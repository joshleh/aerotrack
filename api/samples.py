from __future__ import annotations

from pathlib import Path

from fastapi import HTTPException


def get_sample_root() -> Path:
    return (Path(__file__).resolve().parent.parent / "examples" / "sample_media").resolve()


def resolve_sample_path(sample_path: str) -> Path:
    sample_root = get_sample_root()
    resolved_path = (sample_root / sample_path).resolve()

    try:
        resolved_path.relative_to(sample_root)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail="Sample not found.") from exc

    if not resolved_path.exists() or not resolved_path.is_file():
        raise HTTPException(status_code=404, detail="Sample not found.")

    return resolved_path
