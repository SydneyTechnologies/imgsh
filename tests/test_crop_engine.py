from __future__ import annotations

import unittest

from PIL import Image

from imgsh.core.crop_engine import crop_image
from imgsh.core.errors import ImgshError


class CropEngineTests(unittest.TestCase):
    def test_crop_image_returns_expected_region(self) -> None:
        image = Image.new("RGB", (100, 80), color=(10, 20, 30))

        cropped = crop_image(image=image, x=15, y=10, width=25, height=30)

        self.assertEqual(cropped.size, (25, 30))
        self.assertEqual(cropped.getpixel((0, 0)), (10, 20, 30))

    def test_crop_image_raises_for_out_of_bounds_box(self) -> None:
        image = Image.new("RGB", (50, 40), color=(255, 255, 255))

        with self.assertRaises(ImgshError):
            crop_image(image=image, x=45, y=20, width=10, height=10)


if __name__ == "__main__":
    unittest.main()
