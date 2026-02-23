from __future__ import annotations

DEFAULT_QUALITY = 90
DEFAULT_FIT = "contain"
DEFAULT_OCR_ENGINE = "textract"
DEFAULT_OCR_FORMAT = "txt"

SUPPORTED_FORMATS = {
    "jpg": "JPEG",
    "jpeg": "JPEG",
    "png": "PNG",
    "webp": "WEBP",
}

DEFAULT_EXTENSION_FOR_FORMAT = {
    "JPEG": ".jpg",
    "PNG": ".png",
    "WEBP": ".webp",
}

SUPPORTED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
}

FIT_MODES = {"contain", "cover", "exact"}
OCR_ENGINES = {"textract"}
OCR_FORMATS = {"txt", "json"}
