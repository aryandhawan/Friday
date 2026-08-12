"""
ui/theme.py

Deep Ocean Blue terminal palette + Textual CSS. Every widget pulls its
colors from here. Dark navy / near-black backgrounds with cyan/electric
blue accents -- a clean futuristic HUD aesthetic rather than a
decorative cyberpunk one. `COLOR_USER_TEXT` remains the one deliberate
exception color (a crisp near-white) so a user's own typed console
lines are easy to pick out from SYSTEM/F.R.I.D.A.Y. output at a
glance, without introducing an off-palette hue.
"""

# -- Backgrounds (darkest to panel-level) --------------------------------
BG_DEEPEST = "#020B14"
BG_APP = "#041522"
BG_PANEL = "#071A2A"
BG_PANEL_RAISED = "#0A263A"

# -- Accents --------------------------------------------------------------
ACCENT_PRIMARY = "#A200FF"
ACCENT_BRIGHT = "#6F00FF"
ACCENT_DEEP = "#5E00DA"
ACCENT_SECONDARY = "#6E00EC"

# -- Text -------------------------------------------------------------------
TEXT_BRIGHT = "#D7F3FF"
TEXT_MID = "#D88FE8"
TEXT_DIM = "#965FC7"
TEXT_MUTED = "#714295"

# The one deliberate non-blue-ramp accent, used solely for the literal
# text of user-submitted console lines so it's instantly scannable.
COLOR_USER_TEXT = "#F2FBFF"

# -- Semantic aliases -> keeps widget code readable and swappable --------
COLOR_BACKGROUND = BG_DEEPEST
COLOR_PANEL_BG = BG_PANEL
COLOR_BORDER_DIM = ACCENT_SECONDARY
COLOR_BORDER = ACCENT_PRIMARY
COLOR_HUD_MAIN = ACCENT_PRIMARY
COLOR_HUD_ACCENT = ACCENT_BRIGHT
COLOR_TEXT = TEXT_MID
COLOR_TEXT_BRIGHT = TEXT_BRIGHT
COLOR_TEXT_DIM = TEXT_DIM
COLOR_TEXT_DIMMEST = TEXT_MUTED
COLOR_CRITICAL = ACCENT_BRIGHT
COLOR_OK = "#3DDC97"
COLOR_STATUS_ONLINE = ACCENT_BRIGHT

APP_CSS = f"""
Screen {{
    background: {COLOR_BACKGROUND};
    color: {COLOR_TEXT};
}}

#header {{
    height: 2;
    color: {COLOR_TEXT_BRIGHT};
    padding: 0 1;
    background: {BG_APP};
    border-bottom: solid {COLOR_BORDER_DIM};
}}

#body {{
    layout: horizontal;
    height: 1fr;
}}

#left_col, #right_col {{
    width: 30;
    layout: vertical;
}}

#left_col.hidden, #right_col.hidden {{
    display: none;
}}

.panel {{
    border: round {COLOR_BORDER_DIM};
    border-title-color: {COLOR_TEXT_BRIGHT};
    border-title-background: {COLOR_PANEL_BG};
    border-title-align: left;
    background: {COLOR_PANEL_BG};
    color: {COLOR_TEXT};
    padding: 0 1;
    height: auto;
}}

.panel:focus-within {{
    border: round {ACCENT_BRIGHT};
}}

#center_col {{
    width: 1fr;
    layout: vertical;
    background: {COLOR_BACKGROUND};
}}

#hud {{
    height: 1fr;
    content-align: center middle;
    color: {COLOR_HUD_MAIN};
}}

#bottom_row {{
    layout: horizontal;
    height: 13;
}}

#bottom_row.stacked {{
    layout: vertical;
    height: 22;
}}

#console_panel {{
    border: round {COLOR_BORDER_DIM};
    border-title-color: {COLOR_TEXT_BRIGHT};
    border-title-background: {COLOR_PANEL_BG};
    border-title-align: left;
    background: {COLOR_PANEL_BG};
    width: 3fr;
    height: 1fr;
    padding: 0 1;
    scrollbar-color: {ACCENT_SECONDARY};
    scrollbar-color-hover: {ACCENT_PRIMARY};
    scrollbar-color-active: {ACCENT_BRIGHT};
}}

#shortcuts_panel {{
    border: round {COLOR_BORDER_DIM};
    border-title-color: {COLOR_TEXT_BRIGHT};
    border-title-background: {COLOR_PANEL_BG};
    border-title-align: left;
    background: {COLOR_PANEL_BG};
    width: 1fr;
    height: 1fr;
    padding: 0 1;
}}

#bottom_row.stacked #console_panel, #bottom_row.stacked #shortcuts_panel {{
    width: 1fr;
}}

#prompt_bar {{
    height: 3;
    border: round {COLOR_BORDER_DIM};
    background: {COLOR_PANEL_BG};
    padding: 0 1;
    layout: horizontal;
}}

#prompt_bar:focus-within {{
    border: round {ACCENT_BRIGHT};
}}

#prompt_caret {{
    width: 2;
    color: {ACCENT_BRIGHT};
    content-align: left middle;
    text-style: bold;
}}

#prompt_input {{
    background: {COLOR_PANEL_BG};
    color: {COLOR_TEXT_BRIGHT};
    border: none;
}}

#prompt_input:focus {{
    background: {COLOR_PANEL_BG};
}}
"""
