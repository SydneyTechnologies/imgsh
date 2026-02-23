from __future__ import annotations

from pathlib import Path

from PIL import Image

from imgtool.core.errors import ImgToolError
from imgtool.core.processor import ImageProcessor
from imgtool.utils.validation import validate_quality, validate_resize_dimensions


class ResizeView:
    def __init__(self, dpg_module) -> None:
        self.dpg = dpg_module
        self.processor = ImageProcessor()
        self.input_path: Path | None = None

        self.texture_registry_tag = "imgtool_texture_registry"
        self.preview_texture_tag = "imgtool_preview_texture"
        self.preview_image_tag = "imgtool_preview_image"
        self.path_text_tag = "imgtool_path_text"
        self.status_tag = "imgtool_status"

        self.width_tag = "imgtool_width"
        self.height_tag = "imgtool_height"
        self.fit_tag = "imgtool_fit"
        self.keep_aspect_tag = "imgtool_keep_aspect"
        self.format_tag = "imgtool_format"
        self.quality_tag = "imgtool_quality"
        self.output_tag = "imgtool_output"
        self.overwrite_tag = "imgtool_overwrite"
        self.exif_tag = "imgtool_exif"
        self.file_dialog_tag = "imgtool_file_dialog"

    def build(self) -> None:
        dpg = self.dpg

        with dpg.texture_registry(tag=self.texture_registry_tag, show=False):
            dpg.add_static_texture(
                width=1,
                height=1,
                default_value=[0.0, 0.0, 0.0, 1.0],
                tag=self.preview_texture_tag,
            )

        with dpg.file_dialog(
            show=False,
            directory_selector=False,
            callback=self._on_file_selected,
            tag=self.file_dialog_tag,
            width=700,
            height=500,
        ):
            dpg.add_file_extension("Images{.jpg,.jpeg,.png,.webp}", color=(150, 255, 150, 255))
            dpg.add_file_extension(".*")

        with dpg.window(label="ImgTool", width=980, height=700):
            with dpg.group(horizontal=True):
                dpg.add_button(label="Open Image", callback=lambda: dpg.show_item(self.file_dialog_tag))
                dpg.add_text("No file selected", tag=self.path_text_tag)

            with dpg.group(horizontal=True):
                dpg.add_input_int(
                    label="Width",
                    default_value=1200,
                    min_value=0,
                    min_clamped=True,
                    width=120,
                    tag=self.width_tag,
                )
                dpg.add_input_int(
                    label="Height",
                    default_value=0,
                    min_value=0,
                    min_clamped=True,
                    width=120,
                    tag=self.height_tag,
                )
                dpg.add_checkbox(label="Keep Aspect", default_value=True, tag=self.keep_aspect_tag)
                dpg.add_combo(
                    items=["contain", "cover", "exact"],
                    default_value="contain",
                    label="Fit",
                    width=120,
                    tag=self.fit_tag,
                )
                dpg.add_combo(
                    items=["jpg", "png", "webp"],
                    default_value="jpg",
                    label="Format",
                    width=120,
                    tag=self.format_tag,
                )
                dpg.add_slider_int(
                    label="Quality",
                    default_value=90,
                    min_value=1,
                    max_value=100,
                    width=180,
                    tag=self.quality_tag,
                )

            with dpg.group(horizontal=True):
                dpg.add_input_text(
                    label="Output Path",
                    hint="Optional file path",
                    width=460,
                    tag=self.output_tag,
                )
                dpg.add_checkbox(label="Overwrite", default_value=False, tag=self.overwrite_tag)
                dpg.add_checkbox(label="Preserve EXIF", default_value=True, tag=self.exif_tag)
                dpg.add_button(label="Export", callback=self._export_image)

            dpg.add_text("", tag=self.status_tag, wrap=940)
            dpg.add_separator()
            dpg.add_text("Preview")
            dpg.add_image(self.preview_texture_tag, width=420, height=420, tag=self.preview_image_tag)

    def _on_file_selected(self, sender, app_data, user_data) -> None:
        _ = sender, user_data
        file_path = Path(app_data["file_path_name"])
        self.input_path = file_path
        self.dpg.set_value(self.path_text_tag, str(file_path))
        self._set_status("")
        self._update_preview(file_path)

    def _update_preview(self, input_path: Path) -> None:
        try:
            with Image.open(input_path) as image:
                preview = image.convert("RGBA")
                preview.thumbnail((420, 420), Image.Resampling.LANCZOS)
                width, height = preview.size
                pixels = [
                    channel / 255.0 for pixel in preview.getdata() for channel in pixel  # RGBA floats
                ]
        except Exception as exc:
            self._set_status(f"Preview failed: {exc}")
            return

        dpg = self.dpg
        if dpg.does_item_exist(self.preview_texture_tag):
            dpg.delete_item(self.preview_texture_tag)
        with dpg.texture_registry(tag=self.texture_registry_tag, show=False):
            dpg.add_static_texture(
                width=width,
                height=height,
                default_value=pixels,
                tag=self.preview_texture_tag,
            )
        dpg.configure_item(
            self.preview_image_tag,
            texture_tag=self.preview_texture_tag,
            width=width,
            height=height,
        )

    def _export_image(self) -> None:
        if self.input_path is None:
            self._set_status("Select an image first.")
            return

        dpg = self.dpg
        width_value = dpg.get_value(self.width_tag)
        height_value = dpg.get_value(self.height_tag)
        width = width_value if width_value > 0 else None
        height = height_value if height_value > 0 else None
        keep_aspect = bool(dpg.get_value(self.keep_aspect_tag))
        fit = str(dpg.get_value(self.fit_tag))
        output_format = str(dpg.get_value(self.format_tag))
        quality = int(dpg.get_value(self.quality_tag))
        output_value = str(dpg.get_value(self.output_tag)).strip()
        overwrite = bool(dpg.get_value(self.overwrite_tag))
        preserve_exif = bool(dpg.get_value(self.exif_tag))

        out_path = Path(output_value) if output_value else None

        try:
            validate_resize_dimensions(width=width, height=height, fit=fit)
            validate_quality(quality)
            result = self.processor.resize(
                input_path=self.input_path,
                out=out_path,
                width=width,
                height=height,
                keep_aspect=keep_aspect,
                fit=fit,
                quality=quality,
                output_format=output_format,
                preserve_exif=preserve_exif,
                overwrite=overwrite,
                ocr=False,
            )
            self._set_status(f"Exported: {result.output_path}")
        except ImgToolError as exc:
            self._set_status(f"Error: {exc}")

    def _set_status(self, message: str) -> None:
        self.dpg.set_value(self.status_tag, message)
