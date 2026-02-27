from __future__ import annotations

from imgsh.config import FIT_MODES, OCR_ENGINES, OCR_FORMATS
from imgsh.core.errors import ImgshError


def validate_positive(name: str, value: int | None) -> None:
    if value is not None and value <= 0:
        raise ImgshError(f"{name} must be greater than 0. Got: {value}")


def validate_quality(quality: int) -> None:
    if quality < 1 or quality > 100:
        raise ImgshError(f"--quality must be between 1 and 100. Got: {quality}")


def validate_fit_mode(fit: str) -> None:
    if fit not in FIT_MODES:
        raise ImgshError(f"Invalid --fit '{fit}'. Supported values: contain, cover, exact")


def validate_resize_dimensions(width: int | None, height: int | None, fit: str) -> None:
    validate_positive("--width", width)
    validate_positive("--height", height)
    validate_fit_mode(fit)

    if width is None and height is None:
        if fit == "cover":
            raise ImgshError("Fit mode 'cover' requires both --width and --height.")
        return
    if fit in {"cover", "exact"} and (width is None or height is None):
        raise ImgshError(f"Fit mode '{fit}' requires both --width and --height.")


def validate_ocr_options(engine: str, output_format: str) -> None:
    if engine not in OCR_ENGINES:
        raise ImgshError(f"Unsupported OCR engine '{engine}'. Supported values: textract")
    if output_format not in OCR_FORMATS:
        raise ImgshError(f"Unsupported --ocr-format '{output_format}'. Supported values: txt, json")
