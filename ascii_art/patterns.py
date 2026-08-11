"""
ascii_art/patterns.py

Small reusable ASCII pattern generators that aren't the main HUD --
currently just the DATA STREAM waveform strip.
"""

from __future__ import annotations

import math

from rich.text import Text

from ui import theme

_LEVELS = " .:-=+*#%@"


def render_waveform(width: int, height: int, tick: int) -> Text:
    """
    A deterministic, animated bar-style waveform built from stacked
    terminal characters (no image/canvas), `height` rows tall.
    """
    width = max(width, 10)
    height = max(height, 3)
    text = Text()

    # One pseudo-amplitude per column, blending a few sine waves so
    # it reads as organic rather than a single clean sine.
    amplitudes = []
    for x in range(width):
        v = (
            math.sin((x * 0.35) + tick * 0.4) * 0.5
            + math.sin((x * 0.13) - tick * 0.25) * 0.3
            + math.sin((x * 0.61) + tick * 0.15) * 0.2
        )
        amplitudes.append((v + 1) / 2)  # normalize to 0..1

    for row in range(height):
        row_threshold = 1 - (row + 1) / height
        line = Text()
        for x, amp in enumerate(amplitudes):
            if amp >= row_threshold:
                level_index = min(len(_LEVELS) - 1, int(amp * (len(_LEVELS) - 1)))
                char = _LEVELS[level_index] if _LEVELS[level_index] != " " else ":"
                color = theme.COLOR_HUD_ACCENT if amp > 0.75 else theme.COLOR_HUD_MAIN
                line.append(char, style=color)
            else:
                line.append(" ")
        text.append(line)
        if row != height - 1:
            text.append("\n")
    return text
