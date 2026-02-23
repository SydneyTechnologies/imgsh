from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageOps


def auto_orient(image: Image.Image) -> Image.Image:
    # Respect EXIF orientation before any resizing.
    return ImageOps.exif_transpose(image)


def get_exif_bytes(image: Image.Image) -> bytes | None:
    exif_bytes = image.info.get("exif")
    if isinstance(exif_bytes, bytes):
        return exif_bytes
    return None


def save_image(
    image: Image.Image,
    output_path: Path,
    pillow_format: str,
    quality: int,
    exif_bytes: bytes | None,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    save_kwargs: dict[str, object] = {}
    if pillow_format in {"JPEG", "WEBP"}:
        save_kwargs["quality"] = quality
    if exif_bytes:
        save_kwargs["exif"] = exif_bytes

    try:
        image.save(output_path, format=pillow_format, **save_kwargs)
    except TypeError:
        # Some format/pillow combinations reject EXIF args.
        save_kwargs.pop("exif", None)
        image.save(output_path, format=pillow_format, **save_kwargs)
