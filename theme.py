"""
RIMS — Dynamic Theme System
━━━━━━━━━━━━━━━━━━━━━━━━━━
Supports dark, light, and forest themes with dynamic module-level resolution,
font scaling, and border contrast enhancement.

Usage:
    import theme
    theme.BG            # resolves to current theme's BG
    theme.set_theme("light")   # switch to light theme
    theme.font("Courier", 9, "bold")  # returns scaled font tuple
    theme.set_font_scale("large")    # switch to large font size
"""


# ═══════════════════════════════════════════════════════════════════
# Font scale system
# ═══════════════════════════════════════════════════════════════════

FONT_SCALE_SMALL  = 0.85
FONT_SCALE_MEDIUM = 1.0
FONT_SCALE_LARGE  = 1.25

_FONT_SCALE_LEVELS = {
    "small":  FONT_SCALE_SMALL,
    "medium": FONT_SCALE_MEDIUM,
    "large":  FONT_SCALE_LARGE,
}

_current_font_scale = "medium"
_current_fs = FONT_SCALE_MEDIUM


def set_font_scale(level: str) -> None:
    """Switch to a font scale level: 'small', 'medium', or 'large'."""
    global _current_font_scale, _current_fs
    level = level.lower()
    if level in _FONT_SCALE_LEVELS:
        _current_font_scale = level
        _current_fs = _FONT_SCALE_LEVELS[level]


def get_font_scale() -> str:
    """Return the current font scale level name."""
    return _current_font_scale


def get_font_scale_factor() -> float:
    """Return the current font scale multiplier."""
    return _current_fs


def font(family, size, *variants):
    """
    Return a font tuple scaled by the current font scale factor.
    
    Example:
        theme.font("Courier", 9, "bold") -> ("Courier", 11, "bold")  # at large scale
    """
    scaled = max(6, int(size * _current_fs))
    if variants:
        return (family, scaled, *variants)
    return (family, scaled)


# ═══════════════════════════════════════════════════════════════════
# Theme definitions
# ═══════════════════════════════════════════════════════════════════

class Theme:
    """Immutable theme definition — holds all colour values."""

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def copy(self):
        return Theme(**{k: getattr(self, k) for k in dir(self)
                        if not k.startswith("_")})


# ── Dark theme (original RIMS palette — enhanced borders) ─────────
DARK = Theme(
    # Core palette
    BG      = "#0b0d14",   # Main window background (deep navy-black)
    CARD    = "#11141f",   # Card / container background
    PANEL   = "#181c2a",   # Entry / inner panel background
    BORDER  = "#3a4560",   # Borders and dividers (was #252c42 — lighter for contrast)
    ACCENT  = "#4f8ef7",   # Primary accent (blue)
    ACCENT2 = "#7c5cfc",   # Secondary accent (violet)
    SUCCESS = "#4fc97e",   # Success / positive state (green)
    DANGER  = "#f74f6a",   # Danger / destructive actions (red)
    WARN    = "#f7a94f",   # Warning / pending state (amber)
    TEXT    = "#e8ecf4",   # Primary text (near-white)
    MUTED   = "#8892b0",   # Secondary / muted text (was #6b7490 — lighter for readability)

    # Semantic aliases
    PENDING = "#f7a94f",
    INACTIVE = "#f74f6a",

    # Login-specific extras (same as base in dark)
    LABEL   = "#c8d0e8",
)

# ── Light theme (enhanced borders) ────────────────────────────────
LIGHT = Theme(
    BG      = "#edeff3",   # Soft neutral gray background
    CARD    = "#ffffff",   # Pure white cards
    PANEL   = "#f4f5f8",   # Subtle gray-blue for entry fields and inner panels
    BORDER  = "#a0a8b8",   # Borders and dividers (was #cdd3de — darker for contrast on white)
    ACCENT  = "#3b82f6",   # Primary blue — Tailwind blue-500
    ACCENT2 = "#8b5cf6",   # Violet — Tailwind violet-500
    SUCCESS = "#22c55e",   # Green — Tailwind green-500
    DANGER  = "#ef4444",   # Red — Tailwind red-500
    WARN    = "#f59e0b",   # Amber — Tailwind amber-500
    TEXT    = "#1f2937",   # Near-black text — Tailwind gray-800
    MUTED   = "#6b7280",   # Gray text — Tailwind gray-500
    PENDING = "#f59e0b",
    INACTIVE = "#ef4444",
    LABEL   = "#4b5563",   # Form label color — Tailwind gray-600
)

# ── Forest theme (enhanced borders) ─────────────────────────────
FOREST = Theme(
    BG      = "#0e1a0f",   # Deep forest floor
    CARD    = "#182618",   # Pine canopy
    PANEL   = "#213521",   # Forest mid-layer
    BORDER  = "#3d6b3d",   # Moss on trees (was #2d4f2d — lighter for contrast)
    ACCENT  = "#4caf50",   # Fresh leaf green
    ACCENT2 = "#d4a843",   # Warm honey-amber
    SUCCESS = "#4caf50",   # Leaf green
    DANGER  = "#d45a4a",   # Rust / autumn berry
    WARN    = "#d4a843",   # Warm amber
    TEXT    = "#dce8dc",   # Pale leaf-white
    MUTED   = "#7a9a7a",   # Faded moss (was #5a7a5a — lighter for readability)
    PENDING = "#d4a843",
    INACTIVE = "#d45a4a",
    LABEL   = "#8ab88a",   # Light muted green for form labels
)

# ── Theme registry ────────────────────────────────────────────────
_THEMES = {
    "dark":  DARK,
    "light": LIGHT,
    "forest": FOREST,
}

_current_theme_name = "dark"
_current_theme = DARK


def set_theme(name: str) -> None:
    """
    Switch the active theme to 'dark', 'light', or 'forest'.
    All subsequent module-level accesses (e.g. theme.BG) will use the new theme.
    """
    global _current_theme_name, _current_theme
    name = name.lower()
    if name not in _THEMES:
        name = "dark"
    _current_theme_name = name
    _current_theme = _THEMES[name]


def get_current_theme() -> str:
    """Return the current theme name ('dark', 'light', or 'forest')."""
    return _current_theme_name


def get_available_themes() -> list:
    """Return list of available theme names."""
    return list(_THEMES.keys())


# ═══════════════════════════════════════════════════════════════════
# Dynamic module-level attribute resolution
# ═══════════════════════════════════════════════════════════════════

def __getattr__(name: str):
    """Resolve any unknown attribute against the current theme."""
    if name.startswith("_"):
        raise AttributeError(f"module 'theme' has no attribute {name!r}")
    val = getattr(_current_theme, name, None)
    if val is not None:
        return val
    raise AttributeError(f"module 'theme' has no attribute {name!r}")


def __dir__():
    """List available theme colours."""
    return sorted(k for k in dir(_current_theme) if not k.startswith("_"))
