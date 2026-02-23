from __future__ import annotations

from pathlib import Path

from imgtool.config import DEFAULT_EXTENSION_FOR_FORMAT, SUPPORTED_FORMATS
from imgtool.core.errors import ImgToolError


def supported_format_list() -> str:
    return ", ".join(sorted(set(SUPPORTED_FORMATS)))


def resolve_output_format(
    requested_format: str | None,
    output_path: Path | None,
    input_path: Path,
) -> tuple[str, str]:
    """
    Resolve Pillow output format and preferred extension.
    Precedence: explicit --format > --out suffix > input suffix.
    """
    if requested_format:
        key = requested_format.lower().lstrip(".")
    elif output_path and output_path.suffix:
        key = output_path.suffix.lower().lstrip(".")
    else:
        key = input_path.suffix.lower().lstrip(".")

    if key not in SUPPORTED_FORMATS:
        raise ImgToolError(
            f"Unsupported format '{key}'. Supported formats: {supported_format_list()}"
        )

    pillow_format = SUPPORTED_FORMATS[key]
    extension = DEFAULT_EXTENSION_FOR_FORMAT[pillow_format]
    return pillow_format, extension
