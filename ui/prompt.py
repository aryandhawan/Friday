"""
ui/prompt.py

The interactive prompt line. Typing, backspace, left/right and Enter
all come for free from Textual's Input widget; this subclass adds
Up/Down history recall on top of that.
"""

from __future__ import annotations

from textual import events
from textual.widgets import Input


class PromptInput(Input):
    """Single-line prompt input with shell-style history recall."""

    def __init__(self, **kwargs) -> None:
        kwargs.setdefault("placeholder", "Enter your prompt here...")
        super().__init__(**kwargs)
        self._history: list[str] = []
        self._history_index: int = 0

    def remember(self, text: str) -> None:
        text = text.strip()
        if text and (not self._history or self._history[-1] != text):
            self._history.append(text)
        self._history_index = len(self._history)

    async def on_key(self, event: events.Key) -> None:
        if event.key == "up":
            if self._history:
                self._history_index = max(0, self._history_index - 1)
                self.value = self._history[self._history_index]
                self.cursor_position = len(self.value)
            event.stop()
            event.prevent_default()
        elif event.key == "down":
            if self._history:
                self._history_index = min(len(self._history), self._history_index + 1)
                if self._history_index < len(self._history):
                    self.value = self._history[self._history_index]
                else:
                    self.value = ""
                self.cursor_position = len(self.value)
            event.stop()
            event.prevent_default()
        # Everything else (typing, backspace, left/right, enter) is
        # left to Input's own default handling.
