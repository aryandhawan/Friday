"""
ui/app.py

Assembles the Deep Ocean AI Terminal layout:

    header (compact, top)
    ------------------------------------------------------------
    [ SYSTEM STATUS ] |                        | [ DIAGNOSTICS ]
    [ CORE MODULES  ] |   F.R.I.D.A.Y. HUD     | [ SIGNAL STR. ]
    [ DATA STREAM   ] |   (identity + ring)     | [ THREAT STAT]
    ------------------------------------------------------------
    [ TERMINAL CONSOLE                    ] | [ SHORTCUTS      ]
    ------------------------------------------------------------
    > Enter your prompt here...
"""

from __future__ import annotations

from rich.text import Text
from textual import events
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import RichLog, Static

from core import backend, config
from core.controller import PromptController
from textual import work
from ui import theme
from ui.console import ShortcutsPanel, TerminalConsole
from ui.hud import HUD
from ui.panels import (
    DataStreamPanel,
    Panel,
    SystemStatusPanel,
    core_modules_content,
    diagnostics_content,
    signal_strength_content,
    threat_level_content,
)
from ui.prompt import PromptInput


class BootScreen(Screen):
    """Plays the boot sequence once, then hands off to MainScreen."""

    DEFAULT_CSS = f"""
    BootScreen {{
        align: center middle;
        background: {theme.COLOR_BACKGROUND};
    }}
    #boot_log {{
        width: 62;
        height: auto;
        color: {theme.COLOR_HUD_MAIN};
    }}
    """

    def compose(self) -> ComposeResult:
        yield RichLog(id="boot_log", wrap=False, highlight=False, markup=False)

    def on_mount(self) -> None:
        self._lines = list(config.BOOT_SEQUENCE)
        self._index = 0
        self.set_interval(0.3, self._play_next, pause=False)

    def _play_next(self) -> None:
        log = self.query_one("#boot_log", RichLog)
        if self._index < len(self._lines):
            log.write(f"[ {self._lines[self._index]} ]")
            self._index += 1
        else:
            self.app.switch_screen(MainScreen())


class Header(Static):
    """Plain top status row: identity + AI core / system / mode + version."""

    def on_mount(self) -> None:
        self._ticks = 0
        self._redraw()
        self.set_interval(1.0, self._advance)

    def _advance(self) -> None:
        self._ticks += 1
        self._redraw()

    def _redraw(self) -> None:
        blink_on = self._ticks % 2 == 0
        text = Text()
        text.append(">> ", style=theme.COLOR_TEXT_DIM)
        text.append(config.APP_FULL_NAME, style=f"bold {theme.COLOR_TEXT_BRIGHT}")
        text.append("          ")
        text.append("AI CORE: ", style=theme.COLOR_TEXT_DIM)
        text.append(config.AI_CORE_STATUS, style=theme.COLOR_HUD_MAIN)
        text.append("   |   ", style=theme.COLOR_TEXT_DIMMEST)
        text.append("\u25cf " if blink_on else "\u25cb ", style=theme.COLOR_STATUS_ONLINE)
        text.append("SYSTEM: ", style=theme.COLOR_TEXT_DIM)
        text.append(config.SYSTEM_STATUS, style=theme.COLOR_HUD_MAIN)
        text.append("   |   ", style=theme.COLOR_TEXT_DIMMEST)
        text.append("MODE: ", style=theme.COLOR_TEXT_DIM)
        text.append(config.TERMINAL_MODE, style=theme.COLOR_HUD_MAIN)
        text.append("          ")
        text.append("VERSION: ", style=theme.COLOR_TEXT_DIMMEST)
        text.append(config.VERSION, style=theme.COLOR_TEXT_DIM)
        self.update(text)


class MainScreen(Screen):
    """The primary F.R.I.D.A.Y. terminal screen."""

    BINDINGS = [
        ("ctrl+l", "clear_log", "Clear log"),
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.controller = PromptController(responder=backend.respond)

    def compose(self) -> ComposeResult:
        yield Header(id="header")
        with Container(id="body"):
            with Vertical(id="left_col"):
                yield SystemStatusPanel(id="panel_status")
                yield Panel("CORE MODULES", core_modules_content, id="panel_modules")
                yield DataStreamPanel(id="panel_datastream")
            with Vertical(id="center_col"):
                yield HUD(id="hud")
            with Vertical(id="right_col"):
                yield Panel("DIAGNOSTICS", diagnostics_content, id="panel_diagnostics")
                yield Panel("SIGNAL STRENGTH", signal_strength_content, id="panel_signal")
                yield Panel("THREAT STATUS", threat_level_content, id="panel_threat")
        with Horizontal(id="bottom_row"):
            yield TerminalConsole(id="console_panel")
            yield ShortcutsPanel(id="shortcuts_panel")
        with Horizontal(id="prompt_bar"):
            yield Static("> ", id="prompt_caret")
            yield PromptInput(id="prompt_input")

    def on_mount(self) -> None:
        console = self.query_one("#console_panel", TerminalConsole)
        console.write_system("F.R.I.D.A.Y. Terminal initialized successfully.")
        console.write_system("All core systems online.")
        console.write_system(f"AI Core: {config.AI_CORE_STATUS}")
        console.write_system("Terminal ready for input.")
        self.query_one("#prompt_input", PromptInput).focus()
        self._apply_responsive_layout()

    def on_resize(self, event: events.Resize) -> None:
        self._apply_responsive_layout()

    def _apply_responsive_layout(self) -> None:
        width = self.size.width
        left = self.query_one("#left_col")
        right = self.query_one("#right_col")
        bottom_row = self.query_one("#bottom_row")
        compact = width < config.COMPACT_WIDTH_THRESHOLD
        left.set_class(compact, "hidden")
        right.set_class(compact, "hidden")
        bottom_row.set_class(width < config.WIDE_LAYOUT_WIDTH, "stacked")

    def action_clear_log(self) -> None:
        self.query_one("#console_panel", TerminalConsole).clear()

    def on_input_submitted(self, event: PromptInput.Submitted) -> None:
        text = event.value.strip()
        prompt_input = self.query_one("#prompt_input", PromptInput)
        prompt_input.remember(text)
        prompt_input.value = ""
        if not text:
            return

        console = self.query_one("#console_panel", TerminalConsole)
        console.write_user(text)
        self.run_prompt(text)

    @work(exclusive=True)
    async def run_prompt(self, text: str) -> None:
        console = self.query_one("#console_panel", TerminalConsole)
        try:
            result = await self.controller.handle_prompt(text, log=console.write_system)
            console.write_friday(result.reply_lines)
        except Exception as e:
            # Last-resort safety net: if anything above this raises unexpectedly,
            # make sure the UI still resolves instead of sitting on the last
            # "Building..." status line forever.
            console.write_system(f"✗ Unexpected error: {e}")
            console.write_friday(["Something went wrong — check the console log above."])


class FridayApp(App):
    """F.R.I.D.A.Y. Deep Ocean AI Terminal shell (frontend only)."""

    TITLE = config.APP_NAME
    CSS = theme.APP_CSS
    BINDINGS = [
        ("ctrl+c", "quit", "Quit"),
        ("ctrl+q", "quit", "Quit"),
    ]

    def on_mount(self) -> None:
        self.push_screen(BootScreen())
