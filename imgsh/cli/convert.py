from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from imgsh.cli import exit_with_error
from imgsh.config import DEFAULT_OCR_ENGINE, DEFAULT_OCR_FORMAT, DEFAULT_QUALITY
from imgsh.core.errors import ImgshError
from imgsh.core.processor import ImageProcessor
from imgsh.utils.file_utils import ensure_input_file
from imgsh.utils.validation import validate_ocr_options, validate_quality


def register(app: typer.Typer) -> None:
    @app.command("convert")
    def convert_command(
        input_path: Annotated[Path, typer.Argument(help="Input image path.")],
        output_format: Annotated[
            str, typer.Option("--format", help="Target format: jpg, png, webp.")
        ],
        out: Annotated[
            Path | None, typer.Option("--out", help="Output file path (or output directory).")
        ] = None,
        quality: Annotated[
            int, typer.Option("--quality", help="JPEG/WebP quality (1-100).")
        ] = DEFAULT_QUALITY,
        preserve_exif: Annotated[
            bool,
            typer.Option(
                "--preserve-exif/--strip-exif", help="Preserve source metadata (EXIF)."
            ),
        ] = True,
        overwrite: Annotated[
            bool,
            typer.Option("--overwrite/--no-overwrite", help="Allow replacing existing output files."),
        ] = False,
        ocr: Annotated[
            bool, typer.Option("--ocr", help="Run OCR and write sidecar output.")
        ] = False,
        ocr_engine: Annotated[
            str, typer.Option("--engine", help="OCR engine. Only 'textract' is supported in v1.")
        ] = DEFAULT_OCR_ENGINE,
        ocr_out: Annotated[
            Path | None, typer.Option("--ocr-out", help="OCR output path.")
        ] = None,
        ocr_format: Annotated[
            str, typer.Option("--ocr-format", help="OCR output format: txt or json.")
        ] = DEFAULT_OCR_FORMAT,
        lang: Annotated[str, typer.Option("--lang", help="OCR language hint (default: en).")] = "en",
    ) -> None:
        try:
            ensure_input_file(input_path)
            validate_quality(quality)
            if ocr:
                validate_ocr_options(engine=ocr_engine, output_format=ocr_format)

            processor = ImageProcessor()
            result = processor.convert(
                input_path=input_path,
                out=out,
                output_format=output_format,
                quality=quality,
                preserve_exif=preserve_exif,
                overwrite=overwrite,
                ocr=ocr,
                ocr_engine=ocr_engine,
                ocr_out=ocr_out,
                ocr_format=ocr_format,
                lang=lang,
            )
            typer.echo(f"Saved image: {result.output_path}")
            if result.ocr_path:
                typer.echo(f"Saved OCR: {result.ocr_path}")
        except ImgshError as error:
            exit_with_error(error)
