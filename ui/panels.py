"""
ui/panels.py

The dashboard panels that flank the HUD, plus the two bottom-row
panels (console/shortcuts titles are handled in console.py / app.py).
Every panel is a bordered Static whose `border_title` sits directly
on the dashed border line, e.g. "[ SYSTEM STATUS ]", matching the
reference image's fieldset-style panel captions.
"""

from __future__ import annotations

from rich.text import Text
from textual.widgets import Static

from ascii_art.patterns import render_waveform
from core import config
from ui import theme


def _kv_lines(rows: list[tuple[str, str]], label_width: int = 18) -> Text:
    text = Text()
    for i, (label, value) in enumerate(rows):
        text.append(f"{label:<{label_width}}", style=theme.COLOR_TEXT_DIM)
        text.append(f"{value}\n" if i != len(rows) - 1 else value, style=theme.COLOR_TEXT)
    return text


def _bracket_bar(fraction: float, width: int = 11) -> str:
    """A clean horizontal progress bar using solid/empty block cells."""
    filled = max(0, min(width, round(fraction * width)))
    return "\u2588" * filled + "\u2591" * (width - filled)


class Panel(Static):
    """Generic bordered dashboard panel with a border-line title."""

    def __init__(
        self,
        title: str,
        content_fn,
        refresh_seconds: float = 2.0,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.add_class("panel")
        self.border_title = f" {title} "
        self._content_fn = content_fn
        self._refresh_seconds = refresh_seconds
        self._tick = 0

    def on_mount(self) -> None:
        self._redraw()
        if self._refresh_seconds > 0:
            self.set_interval(self._refresh_seconds, self._advance)

    def _advance(self) -> None:
        self._tick += 1
        self._redraw()

    def _redraw(self) -> None:
        self.update(self._content_fn(self._tick))


class SystemStatusPanel(Panel):
    """[ SYSTEM STATUS ] -- includes a live session uptime field."""

    def __init__(self, **kwargs) -> None:
        super().__init__("SYSTEM STATUS", self._content, refresh_seconds=1.0, **kwargs)
        self._ticks = 0

    def _advance(self) -> None:
        self._ticks += 1
        self._redraw()

    def _content(self, tick: int) -> Text:
        h, rem = divmod(self._ticks, 3600)
        m, s = divmod(rem, 60)
        rows = []
        for label, value in config.SYSTEM_STATUS_FIELDS:
            if label == "UPTIME":
                value = f"{h:02d}:{m:02d}:{s:02d}"
            rows.append((label, value))
        return _kv_lines(rows)


def core_modules_content(tick: int) -> Text:
    return _kv_lines(config.CORE_MODULES)


def diagnostics_content(tick: int) -> Text:
    return _kv_lines(config.DIAGNOSTICS_FIELDS)


def signal_strength_content(tick: int) -> Text:
    text = Text()
    for i, (label, fraction) in enumerate(config.SIGNAL_STRENGTH_FIELDS):
        pct = round(fraction * 100)
        text.append(f"{label:<13}", style=theme.COLOR_TEXT_DIM)
        text.append(_bracket_bar(fraction), style=theme.COLOR_HUD_MAIN)
        text.append(f" {pct:>3}%", style=theme.COLOR_TEXT)
        if i != len(config.SIGNAL_STRENGTH_FIELDS) - 1:
            text.append("\n")
    return text


def threat_level_content(tick: int) -> Text:
    """A single, simple status indicator -- no decorative bar/scale."""
    text = Text()
    text.append("\u25cf ", style=theme.COLOR_OK)
    text.append("STATUS: ", style=theme.COLOR_TEXT_DIM)
    text.append("SECURE", style=f"bold {theme.COLOR_OK}")
    return text


class DataStreamPanel(Panel):
    """[ DATA STREAM ] -- animated waveform strip plus packet stats."""

    WAVEFORM_HEIGHT = 5

    def __init__(self, **kwargs) -> None:
        super().__init__("DATA STREAM", self._content, refresh_seconds=0.4, **kwargs)

    def _content(self, tick: int) -> Text:
        width = max(self.size.width - 2, 20)
        text = Text()
        text.append(render_waveform(width, self.WAVEFORM_HEIGHT, tick))
        text.append("\n\n")
        text.append(_kv_lines(config.DATA_STREAM_FIELDS))
        return text
