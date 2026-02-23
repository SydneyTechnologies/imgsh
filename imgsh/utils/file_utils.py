from __future__ import annotations

from pathlib import Path
from typing import Iterable

from imgsh.config import SUPPORTED_EXTENSIONS
from imgsh.core.errors import ImgshError


def ensure_input_file(path: Path) -> None:
    if not path.exists():
        raise ImgshError(f"File not found: {path}")
    if not path.is_file():
        raise ImgshError(f"Expected a file, got: {path}")


def ensure_input_dir(path: Path) -> None:
    if not path.exists():
        raise ImgshError(f"Directory not found: {path}")
    if not path.is_dir():
        raise ImgshError(f"Expected a directory, got: {path}")


def ensure_not_exists_unless_overwrite(path: Path, overwrite: bool) -> None:
    if path.exists() and not overwrite:
        raise ImgshError(
            f"Output already exists: {path}. Use --overwrite to replace existing files."
        )


def resolve_single_output_path(
    input_path: Path,
    out: Path | None,
    extension: str,
    default_suffix: str,
) -> Path:
    if out is None:
        return input_path.with_name(f"{input_path.stem}{default_suffix}{extension}")

    # If user gave a directory-like path, place file inside it.
    if out.exists() and out.is_dir():
        return out / f"{input_path.stem}{extension}"
    if out.suffix == "":
        return out / f"{input_path.stem}{extension}"
    return out.with_suffix(extension)


def iter_image_files(input_dir: Path, recursive: bool) -> Iterable[Path]:
    pattern = "**/*" if recursive else "*"
    files = sorted(
        path
        for path in input_dir.glob(pattern)
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    )
    return files
