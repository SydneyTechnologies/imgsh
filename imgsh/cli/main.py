from __future__ import annotations

import typer

from imgsh.cli.batch import register as register_batch_command
from imgsh.cli.convert import register as register_convert_command
from imgsh.cli.extract_text import register as register_extract_text_command
from imgsh.cli.gui_cmd import register as register_gui_command
from imgsh.cli.resize import register as register_resize_command

app = typer.Typer(
    help="Imgsh: privacy-first local image processing.",
    no_args_is_help=True,
    add_completion=False,
    context_settings={"help_option_names": ["-h", "--help"]},
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
