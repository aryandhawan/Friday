"""
core/controller.py

PromptController is the single seam between the UI and "whatever
answers the prompt". `responder` is async and takes (text, log) so a
real backend can report progress (planning, building, etc.) into the
UI's console as it goes, not just return one final reply.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Awaitable, Callable, Optional

LogFn = Callable[[str], None]


@dataclass
class PromptResult:
    """What the controller hands back to the UI for one submitted prompt."""

    user_text: str
    reply_lines: list[str]
    backend_connected: bool


class PromptController:
    """
    Owns the request/response cycle for a submitted prompt.

    `responder` is an injectable async callable so a real backend can be
    dropped in later with zero changes to the UI layer:

        controller = PromptController(responder=my_ai_backend.respond)

    If no responder is supplied, the built-in placeholder response is
    used, which never calls out to any network or API.
    """

    def __init__(
        self,
        responder: Optional[Callable[[str, LogFn], Awaitable[PromptResult]]] = None,
    ) -> None:
        self._responder = responder
        self.backend_connected = responder is not None

    async def handle_prompt(self, text: str, log: Optional[LogFn] = None) -> PromptResult:
        text = text.strip()
        log = log or (lambda _msg: None)
        if self._responder is not None:
            return await self._responder(text, log)
        return self._placeholder_response(text)

    # -- placeholder path (no backend, no network, no API keys) -----
    def _placeholder_response(self, text: str) -> PromptResult:
        return PromptResult(
            user_text=text,
            reply_lines=[
                "AI BACKEND NOT CONNECTED",
                "INPUT RECEIVED SUCCESSFULLY",
            ],
            backend_connected=False,
        )
