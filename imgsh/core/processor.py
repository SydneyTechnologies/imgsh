from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from PIL import Image

from imgsh.config import DEFAULT_OCR_ENGINE, DEFAULT_OCR_FORMAT, DEFAULT_QUALITY
from imgsh.core.errors import ImgshError
from imgsh.core.format_engine import resolve_output_format
from imgsh.core.metadata import auto_orient, get_exif_bytes, save_image
from imgsh.core.ocr_engine import extract_text_with_textract
from imgsh.core.resize_engine import resize_image
from imgsh.utils.file_utils import ensure_not_exists_unless_overwrite, resolve_single_output_path


@dataclass
class ProcessResult:
    output_path: Path
    ocr_path: Path | None = None


class ImageProcessor:
    def resize(
        self,
        input_path: Path,
        out: Path | None,
        width: int | None,
        height: int | None,
        keep_aspect: bool,
        fit: str,
        quality: int = DEFAULT_QUALITY,
        output_format: str | None = None,
        preserve_exif: bool = True,
        overwrite: bool = False,
        ocr: bool = False,
        ocr_engine: str = DEFAULT_OCR_ENGINE,
        ocr_out: Path | None = None,
        ocr_format: str = DEFAULT_OCR_FORMAT,
        lang: str = "en",
    ) -> ProcessResult:
        pillow_format, extension = resolve_output_format(output_format, out, input_path)
        output_path = resolve_single_output_path(
            input_path=input_path,
            out=out,
            extension=extension,
            default_suffix="_imgsh",
        )
        ensure_not_exists_unless_overwrite(output_path, overwrite=overwrite)

        with Image.open(input_path) as source_image:
            oriented = auto_orient(source_image)
            resized = resize_image(
                image=oriented,
                width=width,
                height=height,
                keep_aspect=keep_aspect,
                fit=fit,
            )
            exif_bytes = get_exif_bytes(source_image) if preserve_exif else None
            save_image(
                image=resized,
                output_path=output_path,
                pillow_format=pillow_format,
                quality=quality,
                exif_bytes=exif_bytes,
            )

        ocr_path: Path | None = None
        if ocr:
            ocr_path = self.extract_text(
                input_path=output_path,
                out=ocr_out,
                engine=ocr_engine,
                output_format=ocr_format,
                lang=lang,
                overwrite=overwrite,
            )
        return ProcessResult(output_path=output_path, ocr_path=ocr_path)

    def convert(
        self,
        input_path: Path,
        out: Path | None,
        output_format: str,
        quality: int = DEFAULT_QUALITY,
        preserve_exif: bool = True,
        overwrite: bool = False,
        ocr: bool = False,
        ocr_engine: str = DEFAULT_OCR_ENGINE,
        ocr_out: Path | None = None,
        ocr_format: str = DEFAULT_OCR_FORMAT,
        lang: str = "en",
    ) -> ProcessResult:
        pillow_format, extension = resolve_output_format(output_format, out, input_path)
        output_path = resolve_single_output_path(
            input_path=input_path,
            out=out,
            extension=extension,
            default_suffix="_converted",
        )
        ensure_not_exists_unless_overwrite(output_path, overwrite=overwrite)

        with Image.open(input_path) as source_image:
            oriented = auto_orient(source_image)
            exif_bytes = get_exif_bytes(source_image) if preserve_exif else None
            save_image(
                image=oriented,
                output_path=output_path,
                pillow_format=pillow_format,
                quality=quality,
                exif_bytes=exif_bytes,
            )

        ocr_path: Path | None = None
        if ocr:
            ocr_path = self.extract_text(
                input_path=output_path,
                out=ocr_out,
                engine=ocr_engine,
                output_format=ocr_format,
                lang=lang,
                overwrite=overwrite,
            )
        return ProcessResult(output_path=output_path, ocr_path=ocr_path)

    def extract_text(
        self,
        input_path: Path,
        out: Path | None,
        engine: str = DEFAULT_OCR_ENGINE,
        output_format: str = DEFAULT_OCR_FORMAT,
        lang: str = "en",
        overwrite: bool = False,
    ) -> Path:
        if engine != "textract":
            raise ImgshError(f"Unsupported OCR engine '{engine}'. Only 'textract' is supported.")
        if output_format not in {"txt", "json"}:
            raise ImgshError(f"Unsupported OCR output format '{output_format}'. Use txt or json.")

        text = extract_text_with_textract(input_path=input_path, lang=lang)

        if out:
            if (out.exists() and out.is_dir()) or out.suffix == "":
                output_path = out / f"{input_path.stem}.{output_format}"
            else:
                output_path = out.with_suffix(f".{output_format}")
        else:
            output_path = input_path.with_suffix(f".{output_format}")
        ensure_not_exists_unless_overwrite(output_path, overwrite=overwrite)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if output_format == "txt":
            output_path.write_text(text, encoding="utf-8")
        else:
            payload = {
                "engine": engine,
                "source_file": str(input_path),
                "language": lang,
                "text": text,
            }
            output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return output_path
