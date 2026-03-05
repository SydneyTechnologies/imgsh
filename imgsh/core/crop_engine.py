from __future__ import annotations

from PIL import Image

from imgsh.utils.validation import validate_crop_bounds, validate_crop_box


def crop_image(image: Image.Image, x: int, y: int, width: int, height: int) -> Image.Image:
    validate_crop_box(x=x, y=y, width=width, height=height)
    image_width, image_height = image.size
    validate_crop_bounds(
        x=x,
        y=y,
        width=width,
        height=height,
        image_width=image_width,
        image_height=image_height,
    )
    return image.crop((x, y, x + width, y + height))
