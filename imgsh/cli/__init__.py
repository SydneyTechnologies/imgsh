from __future__ import annotations

import typer

from imgsh.core.errors import ImgshError


def exit_with_error(error: ImgshError) -> None:
    typer.secho(f"Error: {error}", fg=typer.colors.RED, err=True)
    raise typer.Exit(code=1)
