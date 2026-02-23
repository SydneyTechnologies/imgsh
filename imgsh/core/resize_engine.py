from __future__ import annotations

from PIL import Image, ImageOps

from imgsh.core.errors import ImgshError

LANCZOS = Image.Resampling.LANCZOS


def resize_image(
    image: Image.Image,
    width: int | None,
    height: int | None,
    keep_aspect: bool,
    fit: str,
) -> Image.Image:
    if width is None and height is None:
        raise ImgshError("At least one of --width or --height is required for resize.")

    original_width, original_height = image.size

    if fit == "cover":
        if width is None or height is None:
            raise ImgshError("Fit mode 'cover' requires both --width and --height.")
        return ImageOps.fit(image, (width, height), method=LANCZOS)

    if fit == "exact":
        target_width = width or original_width
        target_height = height or original_height
        return image.resize((target_width, target_height), resample=LANCZOS)

    # contain mode
    if keep_aspect:
        if width is None:
            ratio = height / original_height
            width = max(1, int(round(original_width * ratio)))
        if height is None:
            ratio = width / original_width
            height = max(1, int(round(original_height * ratio)))

        if width is not None and height is not None:
            return ImageOps.contain(image, (width, height), method=LANCZOS)

    target_width = width or original_width
    target_height = height or original_height
    return image.resize((target_width, target_height), resample=LANCZOS)
