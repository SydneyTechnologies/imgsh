from __future__ import annotations

import unittest

from imgsh.core.errors import ImgshError
from imgsh.utils.validation import validate_crop_bounds, validate_crop_box


class ValidationTests(unittest.TestCase):
    def test_validate_crop_box_rejects_negative_coordinates(self) -> None:
        with self.assertRaises(ImgshError):
            validate_crop_box(x=-1, y=0, width=10, height=10)

    def test_validate_crop_box_rejects_non_positive_dimensions(self) -> None:
        with self.assertRaises(ImgshError):
            validate_crop_box(x=0, y=0, width=0, height=10)

    def test_validate_crop_bounds_rejects_box_past_image_edge(self) -> None:
        with self.assertRaises(ImgshError):
            validate_crop_bounds(
                x=20,
                y=20,
                width=90,
                height=10,
                image_width=100,
                image_height=60,
            )

    def test_validate_crop_bounds_accepts_valid_box(self) -> None:
        validate_crop_bounds(
            x=20,
            y=20,
            width=40,
            height=30,
            image_width=100,
            image_height=60,
        )


if __name__ == "__main__":
    unittest.main()
