from __future__ import annotations

from imgtool.core.errors import ImgToolError
from imgtool.gui.resize_view import ResizeView


def launch_gui() -> None:
    try:
        import dearpygui.dearpygui as dpg  # type: ignore
    except ImportError as exc:
        raise ImgToolError(
            "DearPyGui is not installed. Install with: pip install \"imgtool[gui]\""
        ) from exc

    view = ResizeView(dpg_module=dpg)
    dpg.create_context()
    try:
        view.build()
        dpg.create_viewport(title="ImgTool", width=1000, height=760)
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.start_dearpygui()
    finally:
        dpg.destroy_context()
