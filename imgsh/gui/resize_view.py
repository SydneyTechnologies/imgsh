from __future__ import annotations

import math
from pathlib import Path

from PIL import Image

from imgsh.core.errors import ImgshError
from imgsh.core.processor import ImageProcessor
from imgsh.utils.validation import validate_crop_box, validate_quality, validate_resize_dimensions


class ResizeView:
    PREVIEW_SIZE = 420

    def __init__(self, dpg_module) -> None:
        self.dpg = dpg_module
        self.processor = ImageProcessor()
        self.input_path: Path | None = None

        self.texture_registry_tag = "imgsh_texture_registry"
        self.preview_texture_tag = "imgsh_preview_texture"
        self.preview_drawlist_tag = "imgsh_preview_drawlist"
        self.preview_handlers_tag = "imgsh_preview_handlers"
        self.path_text_tag = "imgsh_path_text"
        self.status_tag = "imgsh_status"
        self.crop_info_tag = "imgsh_crop_info"
        self.crop_detail_tag = "imgsh_crop_detail"

        self.width_tag = "imgsh_width"
        self.height_tag = "imgsh_height"
        self.fit_tag = "imgsh_fit"
        self.keep_aspect_tag = "imgsh_keep_aspect"
        self.crop_enabled_tag = "imgsh_crop_enabled"
        self.crop_x_tag = "imgsh_crop_x"
        self.crop_y_tag = "imgsh_crop_y"
        self.crop_width_tag = "imgsh_crop_width"
        self.crop_height_tag = "imgsh_crop_height"
        self.format_tag = "imgsh_format"
        self.quality_tag = "imgsh_quality"
        self.output_tag = "imgsh_output"
        self.overwrite_tag = "imgsh_overwrite"
        self.exif_tag = "imgsh_exif"
        self.file_dialog_tag = "imgsh_file_dialog"

        self.source_image_size: tuple[int, int] | None = None
        # (left, top, width, height) in preview drawlist coordinates
        self.preview_image_rect: tuple[float, float, float, float] | None = None
        # (x, y, width, height) in source image pixel coordinates
        self.crop_box: tuple[int, int, int, int] | None = None

        self.is_drawing_crop = False
        self.draw_start_image_point: tuple[float, float] | None = None
        self._syncing_crop_inputs = False

    def build(self) -> None:
        dpg = self.dpg

        with dpg.texture_registry(tag=self.texture_registry_tag, show=False):
            dpg.add_dynamic_texture(
                width=self.PREVIEW_SIZE,
                height=self.PREVIEW_SIZE,
                default_value=[0.0] * (self.PREVIEW_SIZE * self.PREVIEW_SIZE * 4),
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

        with dpg.window(label="Imgsh", width=1000, height=760):
            with dpg.group(horizontal=True):
                dpg.add_button(label="Open Image", callback=lambda: dpg.show_item(self.file_dialog_tag))
                dpg.add_text("No file selected", tag=self.path_text_tag)

            with dpg.group(horizontal=True):
                with dpg.group(horizontal=True):
                    dpg.add_text("Width")
                    dpg.add_input_int(
                        label="",
                        default_value=1200,
                        min_value=0,
                        min_clamped=True,
                        width=120,
                        tag=self.width_tag,
                    )
                with dpg.group(horizontal=True):
                    dpg.add_text("Height")
                    dpg.add_input_int(
                        label="",
                        default_value=0,
                        min_value=0,
                        min_clamped=True,
                        width=120,
                        tag=self.height_tag,
                    )
                with dpg.group(horizontal=True):
                    dpg.add_text("Keep Aspect")
                    dpg.add_checkbox(label="", default_value=True, tag=self.keep_aspect_tag)
                with dpg.group(horizontal=True):
                    dpg.add_text("Fit")
                    dpg.add_combo(
                        items=["contain", "cover", "exact"],
                        default_value="contain",
                        label="",
                        width=120,
                        tag=self.fit_tag,
                    )
                with dpg.group(horizontal=True):
                    dpg.add_text("Format")
                    dpg.add_combo(
                        items=["jpg", "png", "webp"],
                        default_value="jpg",
                        label="",
                        width=120,
                        tag=self.format_tag,
                    )
                with dpg.group(horizontal=True):
                    dpg.add_text("Quality")
                    dpg.add_slider_int(
                        label="",
                        default_value=90,
                        min_value=1,
                        max_value=100,
                        width=180,
                        tag=self.quality_tag,
                    )

            with dpg.group(horizontal=True):
                with dpg.group(horizontal=True):
                    dpg.add_text("Enable Crop")
                    dpg.add_checkbox(
                        label="",
                        default_value=False,
                        tag=self.crop_enabled_tag,
                        callback=self._on_crop_toggle,
                    )
                dpg.add_button(label="Reset Crop", callback=self._reset_crop)
                dpg.add_text("Crop disabled.", tag=self.crop_info_tag, wrap=520)

            with dpg.group(horizontal=True):
                with dpg.group(horizontal=True):
                    crop_x_label = dpg.add_text("Left X")
                    dpg.add_input_int(
                        label="",
                        default_value=0,
                        min_value=0,
                        min_clamped=True,
                        width=110,
                        tag=self.crop_x_tag,
                        callback=self._on_crop_input_changed,
                    )
                with dpg.tooltip(crop_x_label):
                    dpg.add_text("Distance from the image's left edge (pixels).")
                with dpg.group(horizontal=True):
                    crop_y_label = dpg.add_text("Top Y")
                    dpg.add_input_int(
                        label="",
                        default_value=0,
                        min_value=0,
                        min_clamped=True,
                        width=110,
                        tag=self.crop_y_tag,
                        callback=self._on_crop_input_changed,
                    )
                with dpg.tooltip(crop_y_label):
                    dpg.add_text("Distance from the image's top edge (pixels).")
                with dpg.group(horizontal=True):
                    crop_width_label = dpg.add_text("Width")
                    dpg.add_input_int(
                        label="",
                        default_value=0,
                        min_value=1,
                        min_clamped=True,
                        width=110,
                        tag=self.crop_width_tag,
                        callback=self._on_crop_input_changed,
                    )
                with dpg.tooltip(crop_width_label):
                    dpg.add_text("Selected width in pixels.")
                with dpg.group(horizontal=True):
                    crop_height_label = dpg.add_text("Height")
                    dpg.add_input_int(
                        label="",
                        default_value=0,
                        min_value=1,
                        min_clamped=True,
                        width=110,
                        tag=self.crop_height_tag,
                        callback=self._on_crop_input_changed,
                    )
                with dpg.tooltip(crop_height_label):
                    dpg.add_text("Selected height in pixels.")

            dpg.add_text(
                "Crop coordinates are in original image pixels (origin is top-left at 0,0)."
            )
            dpg.add_text("", tag=self.crop_detail_tag, wrap=940)

            with dpg.group(horizontal=True):
                with dpg.group(horizontal=True):
                    dpg.add_text("Output Path")
                    dpg.add_input_text(
                        label="",
                        hint="Optional file path",
                        width=460,
                        tag=self.output_tag,
                    )
                with dpg.group(horizontal=True):
                    dpg.add_text("Overwrite")
                    dpg.add_checkbox(label="", default_value=False, tag=self.overwrite_tag)
                with dpg.group(horizontal=True):
                    dpg.add_text("Preserve EXIF")
                    dpg.add_checkbox(label="", default_value=True, tag=self.exif_tag)
                dpg.add_button(label="Export", callback=self._export_image)

            dpg.add_text("", tag=self.status_tag, wrap=940)
            dpg.add_separator()
            dpg.add_text(
                "Preview (drag on image to create crop area, then fine-tune with Left X / Top Y / Width / Height)"
            )
            dpg.add_drawlist(
                width=self.PREVIEW_SIZE,
                height=self.PREVIEW_SIZE,
                tag=self.preview_drawlist_tag,
            )

        with dpg.handler_registry(tag=self.preview_handlers_tag):
            dpg.add_mouse_down_handler(button=dpg.mvMouseButton_Left, callback=self._on_mouse_down)
            dpg.add_mouse_move_handler(callback=self._on_mouse_move)
            dpg.add_mouse_release_handler(button=dpg.mvMouseButton_Left, callback=self._on_mouse_release)

        self._set_crop_inputs_enabled(False)
        self._render_preview_scene()

    def _on_file_selected(self, sender, app_data, user_data) -> None:
        _ = sender, user_data
        file_path = Path(app_data["file_path_name"])
        self.input_path = file_path
        self.crop_box = None
        self.is_drawing_crop = False
        self.draw_start_image_point = None
        self.dpg.set_value(self.path_text_tag, str(file_path))
        self._set_status("")
        self._update_preview(file_path)

    def _update_preview(self, input_path: Path) -> None:
        try:
            with Image.open(input_path) as image:
                source_width, source_height = image.size
                preview = image.convert("RGBA")
                preview.thumbnail((self.PREVIEW_SIZE, self.PREVIEW_SIZE), Image.Resampling.LANCZOS)

                canvas = Image.new("RGBA", (self.PREVIEW_SIZE, self.PREVIEW_SIZE), (0, 0, 0, 255))
                offset_x = (self.PREVIEW_SIZE - preview.width) // 2
                offset_y = (self.PREVIEW_SIZE - preview.height) // 2
                canvas.paste(preview, (offset_x, offset_y))

                pixels = [channel / 255.0 for pixel in canvas.getdata() for channel in pixel]
                self.source_image_size = (source_width, source_height)
                self.preview_image_rect = (
                    float(offset_x),
                    float(offset_y),
                    float(preview.width),
                    float(preview.height),
                )
        except Exception as exc:
            self._set_status(f"Preview failed: {exc}")
            return

        self.dpg.set_value(self.preview_texture_tag, pixels)
        self._sync_crop_inputs_from_box()
        self._render_preview_scene()

    def _on_crop_toggle(self, sender, app_data, user_data) -> None:
        _ = sender, user_data
        enabled = bool(app_data)
        self.is_drawing_crop = False
        self.draw_start_image_point = None
        self._set_crop_inputs_enabled(enabled)
        self._sync_crop_inputs_from_box()
        self._render_preview_scene()

    def _set_crop_inputs_enabled(self, enabled: bool) -> None:
        for tag in (self.crop_x_tag, self.crop_y_tag, self.crop_width_tag, self.crop_height_tag):
            if self.dpg.does_item_exist(tag):
                self.dpg.configure_item(tag, enabled=enabled)

    def _reset_crop(self, sender=None, app_data=None, user_data=None) -> None:
        _ = sender, app_data, user_data
        self.crop_box = None
        self.is_drawing_crop = False
        self.draw_start_image_point = None
        self._sync_crop_inputs_from_box()
        self._render_preview_scene()

    def _crop_enabled(self) -> bool:
        if not self.dpg.does_item_exist(self.crop_enabled_tag):
            return False
        return bool(self.dpg.get_value(self.crop_enabled_tag))

    def _preview_to_image_point(self, local_x: float, local_y: float) -> tuple[float, float] | None:
        if self.source_image_size is None or self.preview_image_rect is None:
            return None

        image_left, image_top, image_width, image_height = self.preview_image_rect
        image_right = image_left + image_width
        image_bottom = image_top + image_height
        if local_x < image_left or local_x > image_right or local_y < image_top or local_y > image_bottom:
            return None

        source_width, source_height = self.source_image_size
        x = ((local_x - image_left) / image_width) * source_width
        y = ((local_y - image_top) / image_height) * source_height
        x = min(max(x, 0.0), float(source_width))
        y = min(max(y, 0.0), float(source_height))
        return x, y

    def _image_to_preview_rect(self, crop_box: tuple[int, int, int, int]) -> tuple[float, float, float, float] | None:
        if self.source_image_size is None or self.preview_image_rect is None:
            return None

        crop_x, crop_y, crop_width, crop_height = crop_box
        source_width, source_height = self.source_image_size
        image_left, image_top, image_width, image_height = self.preview_image_rect

        left = image_left + (crop_x / source_width) * image_width
        top = image_top + (crop_y / source_height) * image_height
        right = image_left + ((crop_x + crop_width) / source_width) * image_width
        bottom = image_top + ((crop_y + crop_height) / source_height) * image_height
        return left, top, right - left, bottom - top

    def _normalize_crop_box(
        self,
        start: tuple[float, float],
        current: tuple[float, float],
    ) -> tuple[int, int, int, int] | None:
        if self.source_image_size is None:
            return None

        source_width, source_height = self.source_image_size
        start_x, start_y = start
        current_x, current_y = current

        left_f = min(start_x, current_x)
        top_f = min(start_y, current_y)
        right_f = max(start_x, current_x)
        bottom_f = max(start_y, current_y)

        left = max(0, min(source_width - 1, math.floor(left_f)))
        top = max(0, min(source_height - 1, math.floor(top_f)))
        right = max(left + 1, min(source_width, math.ceil(right_f)))
        bottom = max(top + 1, min(source_height, math.ceil(bottom_f)))

        width = right - left
        height = bottom - top
        if width <= 0 or height <= 0:
            return None
        return left, top, width, height

    def _clamp_crop_box(self, crop_box: tuple[int, int, int, int]) -> tuple[int, int, int, int] | None:
        if self.source_image_size is None:
            return None

        source_width, source_height = self.source_image_size
        x, y, width, height = crop_box
        x = max(0, min(x, source_width - 1))
        y = max(0, min(y, source_height - 1))
        width = max(1, width)
        height = max(1, height)

        if x + width > source_width:
            width = source_width - x
        if y + height > source_height:
            height = source_height - y

        if width <= 0 or height <= 0:
            return None
        return x, y, width, height

    def _sync_crop_inputs_from_box(self) -> None:
        self._syncing_crop_inputs = True
        try:
            if self.crop_box is None:
                if self.dpg.does_item_exist(self.crop_x_tag):
                    self.dpg.set_value(self.crop_x_tag, 0)
                if self.dpg.does_item_exist(self.crop_y_tag):
                    self.dpg.set_value(self.crop_y_tag, 0)
                if self.dpg.does_item_exist(self.crop_width_tag):
                    self.dpg.set_value(self.crop_width_tag, 0)
                if self.dpg.does_item_exist(self.crop_height_tag):
                    self.dpg.set_value(self.crop_height_tag, 0)
            else:
                x, y, width, height = self.crop_box
                self.dpg.set_value(self.crop_x_tag, x)
                self.dpg.set_value(self.crop_y_tag, y)
                self.dpg.set_value(self.crop_width_tag, width)
                self.dpg.set_value(self.crop_height_tag, height)
        finally:
            self._syncing_crop_inputs = False

    def _on_crop_input_changed(self, sender, app_data, user_data) -> None:
        _ = sender, app_data, user_data
        if self._syncing_crop_inputs or not self._crop_enabled() or self.source_image_size is None:
            return

        x = int(self.dpg.get_value(self.crop_x_tag))
        y = int(self.dpg.get_value(self.crop_y_tag))
        width = int(self.dpg.get_value(self.crop_width_tag))
        height = int(self.dpg.get_value(self.crop_height_tag))

        clamped = self._clamp_crop_box((x, y, width, height))
        self.crop_box = clamped
        self._sync_crop_inputs_from_box()
        self._render_preview_scene()

    def _mouse_local_to_preview(self, allow_outside: bool) -> tuple[float, float] | None:
        dpg = self.dpg
        if not dpg.does_item_exist(self.preview_drawlist_tag):
            return None

        rect_min_x, rect_min_y = dpg.get_item_rect_min(self.preview_drawlist_tag)
        rect_max_x, rect_max_y = dpg.get_item_rect_max(self.preview_drawlist_tag)
        mouse_x, mouse_y = dpg.get_mouse_pos()

        is_inside = rect_min_x <= mouse_x <= rect_max_x and rect_min_y <= mouse_y <= rect_max_y
        if not is_inside and not allow_outside:
            return None

        local_x = mouse_x - rect_min_x
        local_y = mouse_y - rect_min_y

        if allow_outside:
            local_x = min(max(local_x, 0.0), float(self.PREVIEW_SIZE))
            local_y = min(max(local_y, 0.0), float(self.PREVIEW_SIZE))

        return local_x, local_y

    def _on_mouse_down(self, sender, app_data, user_data) -> None:
        _ = sender, app_data, user_data
        if self.input_path is None or not self._crop_enabled():
            return

        local_point = self._mouse_local_to_preview(allow_outside=False)
        if local_point is None:
            return

        image_point = self._preview_to_image_point(*local_point)
        if image_point is None:
            return

        self.is_drawing_crop = True
        self.draw_start_image_point = image_point
        self.crop_box = self._normalize_crop_box(image_point, image_point)
        self._sync_crop_inputs_from_box()
        self._render_preview_scene()

    def _on_mouse_move(self, sender, app_data, user_data) -> None:
        _ = sender, app_data, user_data
        if not self.is_drawing_crop or self.draw_start_image_point is None:
            return
        if not self.dpg.is_mouse_button_down(self.dpg.mvMouseButton_Left):
            return

        local_point = self._mouse_local_to_preview(allow_outside=True)
        if local_point is None:
            return

        image_point = self._preview_to_image_point(*local_point)
        if image_point is None:
            return

        self.crop_box = self._normalize_crop_box(self.draw_start_image_point, image_point)
        self._sync_crop_inputs_from_box()
        self._render_preview_scene()

    def _on_mouse_release(self, sender, app_data, user_data) -> None:
        _ = sender, app_data, user_data
        if not self.is_drawing_crop:
            return
        self.is_drawing_crop = False
        self.draw_start_image_point = None
        self._render_preview_scene()

    def _render_preview_scene(self) -> None:
        dpg = self.dpg
        if not dpg.does_item_exist(self.preview_drawlist_tag):
            return

        dpg.delete_item(self.preview_drawlist_tag, children_only=True)
        dpg.draw_image(
            self.preview_texture_tag,
            (0, 0),
            (self.PREVIEW_SIZE, self.PREVIEW_SIZE),
            parent=self.preview_drawlist_tag,
        )

        if self._crop_enabled() and self.crop_box is not None:
            preview_rect = self._image_to_preview_rect(self.crop_box)
            if preview_rect is not None:
                left, top, width, height = preview_rect
                right = left + width
                bottom = top + height
                dpg.draw_rectangle(
                    pmin=(left, top),
                    pmax=(right, bottom),
                    color=(0, 255, 150, 255),
                    fill=(0, 255, 150, 45),
                    thickness=2.0,
                    parent=self.preview_drawlist_tag,
                )

        self._update_crop_info_text()

    def _update_crop_info_text(self) -> None:
        if not self.dpg.does_item_exist(self.crop_info_tag):
            return

        detail_message = ""
        if not self._crop_enabled():
            message = "Crop disabled."
            detail_message = ""
        elif self.crop_box is None:
            message = "Crop enabled. Drag on preview to create a selection."
            detail_message = "After dragging, adjust Left X / Top Y / Width / Height for exact placement."
        else:
            crop_x, crop_y, crop_width, crop_height = self.crop_box
            crop_right = crop_x + crop_width
            crop_bottom = crop_y + crop_height
            message = (
                f"Crop box: top-left ({crop_x}, {crop_y}), "
                f"bottom-right ({crop_right}, {crop_bottom})"
            )

            if self.source_image_size is not None:
                source_width, source_height = self.source_image_size
                left_pct = (crop_x / source_width) * 100.0
                top_pct = (crop_y / source_height) * 100.0
                right_pct = (crop_right / source_width) * 100.0
                bottom_pct = (crop_bottom / source_height) * 100.0
                detail_message = (
                    f"Selection size: {crop_width}x{crop_height}px on {source_width}x{source_height}px image "
                    f"(L {left_pct:.1f}%, T {top_pct:.1f}%, R {right_pct:.1f}%, B {bottom_pct:.1f}%)."
                )
            else:
                detail_message = f"Selection size: {crop_width}x{crop_height}px."
        self.dpg.set_value(self.crop_info_tag, message)
        if self.dpg.does_item_exist(self.crop_detail_tag):
            self.dpg.set_value(self.crop_detail_tag, detail_message)

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
        crop_box = self.crop_box if self._crop_enabled() else None

        if self._crop_enabled() and crop_box is None:
            self._set_status("Draw a crop region before exporting.")
            return

        out_path = Path(output_value) if output_value else None

        try:
            if crop_box is not None:
                crop_x, crop_y, crop_width, crop_height = crop_box
                validate_crop_box(x=crop_x, y=crop_y, width=crop_width, height=crop_height)
            validate_resize_dimensions(width=width, height=height, fit=fit)
            validate_quality(quality)
            result = self.processor.resize(
                input_path=self.input_path,
                out=out_path,
                width=width,
                height=height,
                keep_aspect=keep_aspect,
                fit=fit,
                crop_box=crop_box,
                quality=quality,
                output_format=output_format,
                preserve_exif=preserve_exif,
                overwrite=overwrite,
                ocr=False,
            )
            self._set_status(f"Exported: {result.output_path}")
        except ImgshError as exc:
            self._set_status(f"Error: {exc}")

    def _set_status(self, message: str) -> None:
        self.dpg.set_value(self.status_tag, message)
