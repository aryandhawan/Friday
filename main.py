"""
main.py

Entry point for the F.R.I.D.A.Y. terminal UI.

    UI (ui/, ascii_art/)
      -> PromptController (core/controller.py)
          -> placeholder response today
          -> real AI backend later (no UI changes required)

Run with:  python main.py
"""

from __future__ import annotations

from ui.app import FridayApp


def main() -> None:
    FridayApp().run()


if __name__ == "__main__":
    main()
