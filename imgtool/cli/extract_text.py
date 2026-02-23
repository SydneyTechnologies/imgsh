from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from imgtool.cli import exit_with_error
from imgtool.config import DEFAULT_OCR_ENGINE, DEFAULT_OCR_FORMAT
from imgtool.core.errors import ImgToolError
from imgtool.core.processor import ImageProcessor
from imgtool.utils.file_utils import ensure_input_file
from imgtool.utils.validation import validate_ocr_options


def register(app: typer.Typer) -> None:
    @app.command("extract-text")
    def extract_text_command(
        input_path: Annotated[Path, typer.Argument(help="Input image path.")],
        ocr_engine: Annotated[
            str, typer.Option("--engine", help="OCR engine. Only 'textract' is supported in v1.")
        ] = DEFAULT_OCR_ENGINE,
        out: Annotated[
            Path | None, typer.Option("--ocr-out", help="OCR output path.")
        ] = None,
        ocr_format: Annotated[
            str, typer.Option("--ocr-format", help="OCR output format: txt or json.")
        ] = DEFAULT_OCR_FORMAT,
        lang: Annotated[str, typer.Option("--lang", help="OCR language hint (default: en).")] = "en",
        overwrite: Annotated[
            bool,
            typer.Option("--overwrite/--no-overwrite", help="Allow replacing existing output files."),
        ] = False,
    ) -> None:
        try:
            ensure_input_file(input_path)
            validate_ocr_options(engine=ocr_engine, output_format=ocr_format)
            processor = ImageProcessor()
            output_path = processor.extract_text(
                input_path=input_path,
                out=out,
                engine=ocr_engine,
                output_format=ocr_format,
                lang=lang,
                overwrite=overwrite,
            )
            typer.echo(f"Saved OCR: {output_path}")
        except ImgToolError as error:
            exit_with_error(error)
