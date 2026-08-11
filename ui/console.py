"""
ui/console.py

The bottom-left [ TERMINAL CONSOLE ] log and the bottom-right
[ SHORTCUTS ] reference panel.
"""

from __future__ import annotations

import time

from rich.text import Text
from textual.widgets import RichLog, Static

from core import config
from ui import theme

_LABEL_WIDTH = max(len("F.R.I.D.A.Y."), len("SYSTEM"), len("USER"))


class TerminalConsole(RichLog):
    """Timestamped system/user/AI log, styled like the reference console."""

    def __init__(self, **kwargs) -> None:
        kwargs.setdefault("wrap", True)
        kwargs.setdefault("highlight", False)
        kwargs.setdefault("markup", False)
        super().__init__(**kwargs)
        self.add_class("panel")
        self.border_title = " TERMINAL CONSOLE "

    @staticmethod
    def _timestamp() -> str:
        return time.strftime("[%H:%M:%S]")

    def _write_line(self, label: str, body: str, color: str) -> None:
        prefix = Text(f"{self._timestamp()} {label:<{_LABEL_WIDTH}} > ", style=theme.COLOR_TEXT_DIM)
        prefix.append(body, style=color)
        self.write(prefix)

    def write_system(self, message: str) -> None:
        self._write_line("SYSTEM", message, theme.COLOR_TEXT)

    def write_user(self, message: str) -> None:
        # User-typed text gets a crisp near-white accent so it's
        # instantly scannable against the SYSTEM/F.R.I.D.A.Y. blue tones.
        self._write_line("USER", message, theme.COLOR_USER_TEXT)

    def write_friday(self, lines: list[str]) -> None:
        if not lines:
            return
        self._write_line("F.R.I.D.A.Y.", lines[0], theme.COLOR_HUD_ACCENT)
        pad = " " * (len(self._timestamp()) + 1 + _LABEL_WIDTH + 3)
        for extra in lines[1:]:
            self.write(Text(f"{pad}{extra}", style=theme.COLOR_HUD_ACCENT))


class ShortcutsPanel(Static):
    """[ SHORTCUTS ] -- static reference list, no live data needed."""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_class("panel")
        self.border_title = " SHORTCUTS "

    def on_mount(self) -> None:
        text = Text()
        key_width = max(len(k) for k, _ in config.SHORTCUTS) + 4
        for i, (key, desc) in enumerate(config.SHORTCUTS):
            text.append(f"{key:<{key_width}}", style=theme.COLOR_TEXT_BRIGHT)
            text.append(desc, style=theme.COLOR_TEXT)
            if i != len(config.SHORTCUTS) - 1:
                text.append("\n")
        self.update(text)
