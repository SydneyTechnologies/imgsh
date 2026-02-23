from __future__ import annotations

import typer

from imgtool.core.errors import ImgToolError


def exit_with_error(error: ImgToolError) -> None:
    typer.secho(f"Error: {error}", fg=typer.colors.RED, err=True)
    raise typer.Exit(code=1)
