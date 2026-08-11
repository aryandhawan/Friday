"""
ascii_art/friday_hud.py

Composes the central F.R.I.D.A.Y. identity display: a single clean
HUD ring made from evenly-spaced terminal characters, four small
cardinal tick marks, one slowly rotating scan highlight, and the
F.R.I.D.A.Y. wordmark + subtitle centered inside. This intentionally
replaces the old dense multi-ring / digit-textured / coordinate-callout
composition -- the goal is a quiet, professional focal point rather
than a busy dashboard. Still composed with radius/angle math against a
character grid, not a filtered bitmap, an SVG, or a canvas drawing.
"""

from __future__ import annotations

import math

from rich.text import Text

from ascii_art.friday_logo import build_logo
from ui import theme

_SUBTITLE = "AUTONOMOUS AI AGENT"

# Vertical cells are roughly twice as tall as they are wide, so we
# stretch y-distance to keep the ring circular rather than oval.
_ASPECT = 2.15

_RING_CHAR = "."
_TICK_COUNT = 48
_SCAN_WIDTH_DEG = 16


def render_hud(width: int, height: int, frame: int, compact: bool = False) -> Text:
    """
    Build one animated frame of the central HUD as a Rich Text block.

    `frame` is an increasing tick counter from the caller's animation
    timer; it drives a slowly rotating scan highlight and a slow
    brightness pulse on the wordmark, kept gentle so the composition
    stays calm rather than flickering.
    """
    width = max(width, 24)
    height = max(height, 14)

    grid = [[" "] * width for _ in range(height)]
    style_grid: list[list[str]] = [["dim"] * width for _ in range(height)]

    cx = width / 2.0
    cy = height / 2.0
    max_r = min(cx, cy * _ASPECT) * 0.90
    scan_angle = (frame * 3) % 360
    pulse_phase = (frame % 16)
    pulse_on = pulse_phase < 8

    # -- Outer ring: one clean band of evenly spaced dots -----------------
    ring_r = max_r
    for tick_i in range(_TICK_COUNT):
        angle = (360.0 / _TICK_COUNT) * tick_i
        rad = math.radians(angle)
        x = int(round(cx + math.cos(rad) * ring_r))
        y = int(round(cy + math.sin(rad) * ring_r / _ASPECT))
        if not (0 <= x < width and 0 <= y < height):
            continue
        delta = min(abs(angle - scan_angle), 360 - abs(angle - scan_angle))
        if delta < _SCAN_WIDTH_DEG / 2:
            grid[y][x] = "#"
            style_grid[y][x] = "bright"
        else:
            grid[y][x] = _RING_CHAR
            style_grid[y][x] = "main" if tick_i % 4 == 0 else "dim"

    # -- Inner ring: faint, sparse, purely to suggest depth ----------------
    if not compact:
        inner_r = max_r * 0.55
        inner_ticks = _TICK_COUNT // 2
        for tick_i in range(inner_ticks):
            angle = (360.0 / inner_ticks) * tick_i
            if tick_i % 3 != 0:
                continue
            rad = math.radians(angle)
            x = int(round(cx + math.cos(rad) * inner_r))
            y = int(round(cy + math.sin(rad) * inner_r / _ASPECT))
            if 0 <= x < width and 0 <= y < height and grid[y][x] == " ":
                grid[y][x] = "."
                style_grid[y][x] = "dim"

    # -- Four small cardinal ticks just outside the ring -------------------
    for deg in (0, 90, 180, 270):
        rad = math.radians(deg)
        x = int(round(cx + math.cos(rad) * (ring_r + 1.5)))
        y = int(round(cy + math.sin(rad) * (ring_r + 1.5) / _ASPECT))
        if 0 <= x < width and 0 <= y < height:
            grid[y][x] = "+"
            style_grid[y][x] = "dim"

    # -- Center wordmark + subtitle, overlaid last so it always reads clean
    logo_scale = 2 if (not compact and width > 100 and height > 38) else 1
    logo_rows = build_logo(scale=logo_scale)
    logo_h = len(logo_rows)

    # Vertical: center the whole block (logo + blank + subtitle) on cy.
    block_h = logo_h + 1 + 1  # logo rows + blank gap + subtitle
    logo_start_y = int(round(cy - block_h / 2))

    # Horizontal: center the logo as a single block using ONE shared
    # start_x for every row, based on the overall bounding box of all
    # lit '#' pixels across the whole wordmark. Using a per-row midpoint
    # here would shift each row independently (since glyph rows differ
    # in how far left/right their own '#'s fall), breaking vertical
    # alignment between letters and making the wordmark look scattered.
    all_positions = [j for row_text in logo_rows for j, c in enumerate(row_text) if c == "#"]
    logo_px_center = (min(all_positions) + max(all_positions)) / 2.0 if all_positions else 0.0
    logo_start_x = int(round(cx - logo_px_center))

    wordmark_style = "wordmark_pulse" if pulse_on else "wordmark"
    for i, row_text in enumerate(logo_rows):
        y = logo_start_y + i
        if not (0 <= y < height):
            continue
        for j, ch in enumerate(row_text):
            if ch != "#":
                continue
            x = logo_start_x + j
            if 0 <= x < width:
                grid[y][x] = "#"
                style_grid[y][x] = wordmark_style

    subtitle_y = logo_start_y + logo_h + 1
    _stamp_centered(grid, style_grid, width, subtitle_y, _SUBTITLE, cx, "subtitle")

    return _grid_to_text(grid, style_grid)


def _stamp_centered(grid, style_grid, width, y, text, cx, style_name):
    if not (0 <= y < len(grid)):
        return
    start_x = int(cx - len(text) / 2)
    for i, ch in enumerate(text):
        x = start_x + i
        if 0 <= x < width:
            grid[y][x] = ch
            style_grid[y][x] = style_name


_STYLE_COLORS = {
    "dim": theme.COLOR_TEXT_DIMMEST,
    "text": theme.COLOR_TEXT,
    "main": theme.COLOR_HUD_MAIN,
    "accent": theme.COLOR_HUD_ACCENT,
    "bright": theme.COLOR_HUD_ACCENT,
    "wordmark": theme.COLOR_HUD_MAIN,
    "wordmark_pulse": theme.COLOR_HUD_ACCENT,
    "subtitle": theme.COLOR_TEXT_DIM,
}


def _grid_to_text(grid: list[list[str]], style_grid: list[list[str]]) -> Text:
    out = Text()
    for y, row in enumerate(grid):
        line = "".join(row)
        styles = style_grid[y]
        run_style = _STYLE_COLORS.get(styles[0], theme.COLOR_TEXT_DIMMEST)
        run_start = 0
        for x in range(1, len(line)):
            color = _STYLE_COLORS.get(styles[x], theme.COLOR_TEXT_DIMMEST)
            if color != run_style:
                out.append(line[run_start:x], style=run_style)
                run_start = x
                run_style = color
        out.append(line[run_start:], style=run_style)
        if y != len(grid) - 1:
            out.append("\n")
    return out
