from __future__ import annotations

import typer

from imgtool.cli import exit_with_error
from imgtool.core.errors import ImgToolError


def register(app: typer.Typer) -> None:
    @app.command("gui")
    def gui_command() -> None:
        try:
            from imgtool.gui.app import launch_gui
        except ImportError:
            exit_with_error(
                ImgToolError(
                    "GUI dependencies are not installed. Install with: pip install \"imgtool[gui]\""
                )
            )

        try:
            launch_gui()
        except ImgToolError as error:
            exit_with_error(error)
