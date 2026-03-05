from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from PIL import Image
from typer.testing import CliRunner

from imgsh.cli.main import app


class CropCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.runner = CliRunner()

    def test_crop_command_writes_expected_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            input_path = tmp_path / "input.png"
            output_path = tmp_path / "cropped.png"
            Image.new("RGB", (120, 90), color=(22, 33, 44)).save(input_path)

            result = self.runner.invoke(
                app,
                [
                    "crop",
                    str(input_path),
                    "--x",
                    "10",
                    "--y",
                    "8",
                    "--width",
                    "50",
                    "--height",
                    "40",
                    "--out",
                    str(output_path),
                ],
            )

            self.assertEqual(result.exit_code, 0, result.output)
            self.assertTrue(output_path.exists())
            with Image.open(output_path) as cropped:
                self.assertEqual(cropped.size, (50, 40))

    def test_crop_command_rejects_out_of_bounds_box(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            input_path = tmp_path / "input.png"
            Image.new("RGB", (80, 60), color=(22, 33, 44)).save(input_path)

            result = self.runner.invoke(
                app,
                [
                    "crop",
                    str(input_path),
                    "--x",
                    "70",
                    "--y",
                    "40",
                    "--width",
                    "20",
                    "--height",
                    "30",
                ],
            )

            self.assertEqual(result.exit_code, 1)
            self.assertIn("out of bounds", result.output)


if __name__ == "__main__":
    unittest.main()
