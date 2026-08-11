"""
core/backend.py

The one file that knows about both the UI's PromptResult type and the
real agent pipeline. Everything else (ui/, core/controller.py) stays
backend-agnostic.
"""
from __future__ import annotations

from core.controller import PromptResult
from pipeline import process_command


async def respond(text: str, log) -> PromptResult:
    reply_lines = await process_command(text, log=log)
    return PromptResult(
        user_text=text,
        reply_lines=reply_lines,
        backend_connected=True,
    )
