from __future__ import annotations

from pathlib import Path

from imgtool.core.errors import ImgToolError

LANG_CODE_MAP = {
    "en": "eng",
}


def _load_textract():
    try:
        import textract  # type: ignore
    except ImportError as exc:
        raise ImgToolError(
            "OCR engine 'textract' is not installed. Install with: pip install \"imgtool[ocr]\""
        ) from exc
    return textract


def extract_text_with_textract(input_path: Path, lang: str) -> str:
    textract = _load_textract()
    language = LANG_CODE_MAP.get(lang.lower(), lang)

    try:
        data = textract.process(str(input_path), language=language)
    except TypeError:
        # Not all textract parsers accept language.
        data = textract.process(str(input_path))
    except Exception as exc:
        raise ImgToolError(f"OCR failed for '{input_path}': {exc}") from exc

    if isinstance(data, bytes):
        return data.decode("utf-8", errors="replace")
    return str(data)
