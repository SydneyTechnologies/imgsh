from __future__ import annotations

import typer

from imgtool.cli.batch import register as register_batch_command
from imgtool.cli.convert import register as register_convert_command
from imgtool.cli.extract_text import register as register_extract_text_command
from imgtool.cli.gui_cmd import register as register_gui_command
from imgtool.cli.resize import register as register_resize_command

app = typer.Typer(
    help="ImgTool: privacy-first local image processing.",
    no_args_is_help=True,
    add_completion=False,
)

register_resize_command(app)
register_batch_command(app)
register_convert_command(app)
register_extract_text_command(app)
register_gui_command(app)


def run() -> None:
    app()


if __name__ == "__main__":
    run()
