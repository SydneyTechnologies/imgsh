from __future__ import annotations

import typer

from imgsh.cli import exit_with_error
from imgsh.core.errors import ImgshError


def register(app: typer.Typer) -> None:
    @app.command("gui")
    def gui_command() -> None:
        try:
            from imgsh.gui.app import launch_gui
        except ImportError:
            exit_with_error(
                ImgshError(
                    "GUI dependencies are not installed. Install with: poetry install --extras \"gui\" "
                    "(or pip install \"imgsh[gui]\")."
                )
            )

        try:
            launch_gui()
        except ImgshError as error:
            exit_with_error(error)
