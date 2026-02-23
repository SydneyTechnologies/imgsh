from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from imgsh.cli import exit_with_error
from imgsh.config import DEFAULT_FIT, DEFAULT_OCR_ENGINE, DEFAULT_OCR_FORMAT, DEFAULT_QUALITY
from imgsh.core.errors import ImgshError
from imgsh.core.format_engine import resolve_output_format
from imgsh.core.processor import ImageProcessor
from imgsh.utils.file_utils import ensure_input_dir, iter_image_files
from imgsh.utils.validation import validate_ocr_options, validate_quality, validate_resize_dimensions


def _render_name_pattern(
    pattern: str,
    stem: str,
    extension: str,
    width: int | None,
    height: int | None,
    index: int,
) -> str:
    try:
        return pattern.format(
            stem=stem,
            ext=extension.lstrip("."),
            width=width or "auto",
            height=height or "auto",
            index=index,
        )
    except KeyError as exc:
        raise ImgshError(
            f"Invalid placeholder in --name-pattern: {exc}. "
            "Supported placeholders: {stem}, {ext}, {width}, {height}, {index}"
        ) from exc


def register(app: typer.Typer) -> None:
    @app.command("batch-resize")
    def batch_resize_command(
        input_dir: Annotated[Path, typer.Argument(help="Input directory containing images.")],
        width: Annotated[int | None, typer.Option("--width", help="Target width in pixels.")] = None,
        height: Annotated[
            int | None, typer.Option("--height", help="Target height in pixels.")
        ] = None,
        keep_aspect: Annotated[
            bool, typer.Option("--keep-aspect/--no-keep-aspect", help="Maintain aspect ratio.")
        ] = True,
        fit: Annotated[
            str, typer.Option("--fit", help="Resize mode: contain, cover, exact.")
        ] = DEFAULT_FIT,
        out: Annotated[
            Path | None, typer.Option("--out", help="Output directory.")
        ] = None,
        recursive: Annotated[
            bool, typer.Option("--recursive/--no-recursive", help="Traverse subdirectories.")
        ] = False,
        name_pattern: Annotated[
            str,
            typer.Option(
                "--name-pattern",
                help="Filename pattern (without extension). Supports {stem},{ext},{width},{height},{index}.",
            ),
        ] = "{stem}_imgsh",
        quality: Annotated[
            int, typer.Option("--quality", help="JPEG/WebP quality (1-100).")
        ] = DEFAULT_QUALITY,
        output_format: Annotated[
            str | None, typer.Option("--format", help="Output format: jpg, png, webp.")
        ] = None,
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
        ocr_format: Annotated[
            str, typer.Option("--ocr-format", help="OCR output format: txt or json.")
        ] = DEFAULT_OCR_FORMAT,
        lang: Annotated[str, typer.Option("--lang", help="OCR language hint (default: en).")] = "en",
    ) -> None:
        try:
            ensure_input_dir(input_dir)
            validate_resize_dimensions(width=width, height=height, fit=fit)
            validate_quality(quality)
            if ocr:
                validate_ocr_options(engine=ocr_engine, output_format=ocr_format)

            input_files = list(iter_image_files(input_dir=input_dir, recursive=recursive))
            if not input_files:
                raise ImgshError("No supported images found in the input directory.")

            processor = ImageProcessor()
            processed = 0
            failed = 0

            for index, input_path in enumerate(input_files, start=1):
                try:
                    _, extension = resolve_output_format(output_format, None, input_path)
                    output_stem = _render_name_pattern(
                        pattern=name_pattern,
                        stem=input_path.stem,
                        extension=extension,
                        width=width,
                        height=height,
                        index=index,
                    )

                    if out:
                        if recursive:
                            relative_parent = input_path.relative_to(input_dir).parent
                            target_dir = out / relative_parent
                        else:
                            target_dir = out
                    else:
                        target_dir = input_path.parent

                    output_path = target_dir / f"{output_stem}{extension}"
                    result = processor.resize(
                        input_path=input_path,
                        out=output_path,
                        width=width,
                        height=height,
                        keep_aspect=keep_aspect,
                        fit=fit,
                        quality=quality,
                        output_format=output_format,
                        preserve_exif=preserve_exif,
                        overwrite=overwrite,
                        ocr=ocr,
                        ocr_engine=ocr_engine,
                        ocr_out=None,
                        ocr_format=ocr_format,
                        lang=lang,
                    )
                    processed += 1
                    typer.echo(f"[ok] {input_path} -> {result.output_path}")
                except ImgshError as error:
                    failed += 1
                    typer.secho(f"[fail] {input_path}: {error}", fg=typer.colors.YELLOW, err=True)

            typer.echo(f"Batch complete. Processed: {processed}, Failed: {failed}")
            if failed:
                raise typer.Exit(code=1)
        except ImgshError as error:
            exit_with_error(error)
