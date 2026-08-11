"""
ascii_art/friday_logo.py

Hand-built block-letter glyphs (not a filtered image) for the
F.R.I.D.A.Y. wordmark, rendered purely from terminal characters.
"""

from __future__ import annotations

_GLYPH_H = 5

_GLYPHS: dict[str, list[str]] = {
    "F": [
        "#####",
        "#....",
        "####.",
        "#....",
        "#....",
    ],
    "R": [
        "####.",
        "#...#",
        "####.",
        "#..#.",
        "#...#",
    ],
    "I": [
        "#####",
        "..#..",
        "..#..",
        "..#..",
        "#####",
    ],
    "D": [
        "####.",
        "#...#",
        "#...#",
        "#...#",
        "####.",
    ],
    "A": [
        ".###.",
        "#...#",
        "#####",
        "#...#",
        "#...#",
    ],
    "Y": [
        "#...#",
        ".#.#.",
        "..#..",
        "..#..",
        "..#..",
    ],
    ".": [
        ".....",
        ".....",
        ".....",
        ".....",
        "..#..",
    ],
}

_WORD = "F.R.I.D.A.Y"


def build_logo(scale: int = 1) -> list[str]:
    """
    Return the F.R.I.D.A.Y. wordmark as a list of equal-length ASCII
    rows, built from the glyph table above (each glyph 5 wide x 5
    tall, one blank column of spacing between glyphs).

    `scale` repeats each character horizontally/vertically for a
    larger banner on bigger terminals; 1 is the compact size.
    """
    rows = ["" for _ in range(_GLYPH_H)]
    for ch in _WORD:
        glyph = _GLYPHS.get(ch, _GLYPHS["."])
        for i in range(_GLYPH_H):
            rows[i] += glyph[i] + " "

    if scale <= 1:
        return rows

    scaled: list[str] = []
    for row in rows:
        wide_row = "".join(c * scale for c in row)
        for _ in range(scale):
            scaled.append(wide_row)
    return scaled


def logo_dimensions(scale: int = 1) -> tuple[int, int]:
    rows = build_logo(scale)
    height = len(rows)
    width = max((len(r) for r in rows), default=0)
    return width, height
