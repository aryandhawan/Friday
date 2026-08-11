"""
core/config.py

Static identity/version constants plus the literal panel content
specified by the reference image. Nothing here touches a network,
a database, or an AI API -- it's display data only.
"""

APP_NAME = "F.R.I.D.A.Y."
APP_FULL_NAME = "F.R.I.D.A.Y. TERMINAL"
VERSION = "v0.1.0"

AI_CORE_STATUS = "STANDBY"
SYSTEM_STATUS = "ONLINE"
TERMINAL_MODE = "INTERACTIVE"

# -- [ SYSTEM STATUS ] -------------------------------------------------
SYSTEM_STATUS_FIELDS = [
    ("AI CORE", "STANDBY"),
    ("MEMORY", "24%"),
    ("CPU LOAD", "06%"),
    ("SYSTEM TEMP", "41\u00b0C"),
    ("UPTIME", None),  # filled in live by the panel (elapsed session time)
    ("TERMINAL", "ACTIVE"),
]

# -- [ CORE MODULES ] ---------------------------------------------------
CORE_MODULES = [
    ("NEURAL INTERFACE", "OK"),
    ("LANGUAGE ENGINE", "OK"),
    ("SYNTHETIC MEMORY", "OK"),
    ("LOGIC PROCESSOR", "OK"),
    ("DATA STREAM", "OK"),
]

# -- [ DATA STREAM ] ------------------------------------------------------
DATA_STREAM_FIELDS = [
    ("PACKETS/S", "1.34K"),
    ("INBOUND", "812"),
    ("OUTBOUND", "612"),
    ("ERROR RATE", "0.00%"),
]

# -- [ DIAGNOSTICS ] -------------------------------------------------------
DIAGNOSTICS_FIELDS = [
    ("DIAGNOSTIC RUN", "OK"),
    ("SYSTEM CHECK", "OK"),
    ("MEMORY CHECK", "OK"),
    ("CORE INTEGRITY", "OK"),
    ("NETWORK STATUS", "OK"),
    ("DISK STATUS", "OK"),
    ("AI SUBSYSTEM", "OK"),
    ("THREAT SCAN", "CLEAR"),
]

# -- [ SIGNAL STRENGTH ] -- (label, fraction 0..1) -----------------------
SIGNAL_STRENGTH_FIELDS = [
    ("CORE SIGNAL", 1.00),
    ("NEURAL LINK", 0.92),
    ("DATA LINK", 0.78),
    ("VOICE LINK", 0.65),
    ("VISION LINK", 0.45),
]

# -- [ SHORTCUTS ] --------------------------------------------------------
SHORTCUTS = [
    ("ENTER", "Send Message"),
    ("CTRL+L", "Clear Screen"),
    ("CTRL+Q", "Exit Terminal"),
    ("\u2191", "Previous Input"),
    ("\u2193", "Next Input"),
    ("TAB", "Auto Complete"),
    ("/?", "Help Menu"),
]

# Boot sequence lines played once on startup.
BOOT_SEQUENCE = [
    "SYSTEM BOOT",
    "CLEARING TERMINAL ......... OK",
    "INITIALIZING TERMINAL ..... OK",
    "LOADING BOOT INFORMATION .. OK",
    "RENDERING ASCII HUD ....... OK",
    "RUNNING DIAGNOSTICS ....... OK",
    "AI CORE .................... STANDBY",
    "TERMINAL READY",
]

# Layout thresholds (columns). Below the first, side panels drop.
# Below the second, the bottom console/shortcuts split stacks instead
# of sitting side by side. The reference's primary target is 120+.
WIDE_LAYOUT_WIDTH = 120
COMPACT_WIDTH_THRESHOLD = 100
MIN_HEIGHT_THRESHOLD = 30
