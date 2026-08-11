"""
ui/hud.py

Widget responsible for animating the central ASCII HUD. It owns a
frame counter and a timer; the actual character composition lives in
ascii_art/friday_hud.py so this file stays purely about wiring the
animation into Textual's render loop.
"""

from __future__ import annotations

from textual.widgets import Static

from ascii_art.friday_hud import render_hud
from core import config


class HUD(Static):
    """Centered, responsive, gently-animated F.R.I.D.A.Y. HUD."""

    FRAME_INTERVAL = 0.5  # seconds; kept slow -> premium, not flashy

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._frame = 0

    def on_mount(self) -> None:
        self.set_interval(self.FRAME_INTERVAL, self._advance_frame)
        self.call_after_refresh(self._redraw)

    def on_resize(self) -> None:
        self._redraw()

    def _advance_frame(self) -> None:
        self._frame += 1
        self._redraw()

    def _redraw(self) -> None:
        width = max(self.size.width, 20)
        height = max(self.size.height, 10)
        compact = (
            width < config.COMPACT_WIDTH_THRESHOLD
            or height < config.MIN_HEIGHT_THRESHOLD
        )
        art = render_hud(width, height, self._frame, compact=compact)
        self.update(art)
