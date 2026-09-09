"""
Central design system for the Electricity Billing Management System UI.

Every screen pulls its colors, fonts and ttk widget styles from this module
instead of hard-coding them, so the whole application stays visually
consistent and can be re-themed from one place.

No third-party UI library is used here — everything is plain Tkinter/ttk.
"""

import tkinter as tk
from tkinter import ttk


# =============================================================================
# COLOR PALETTE
# Warm, neutral utility-company palette: off-white surfaces, charcoal text,
# and a restrained amber accent (evokes electricity without looking like a
# neon "AI dashboard"). Status colors are muted, not saturated/neon.
# =============================================================================

COLORS = {
    # Base surfaces
    "bg": "#F3F1EA",             # app background (warm off-white)
    "surface": "#FFFFFF",        # cards, tables, panels
    "surface_alt": "#F6F4EE",    # subtle alternating / recessed panels
    "border": "#E2DFD3",         # hairline borders
    "border_strong": "#D3CFBF",

    # Text
    "text": "#2A2823",           # dark charcoal (warm-toned, not pure black)
    "text_muted": "#75705F",
    "text_faint": "#A39C88",
    "text_on_dark": "#F4F2EA",

    # Accent — restrained electric amber
    "accent": "#F0A93A",
    "accent_dark": "#C9871F",
    "accent_soft": "#FBE7C4",    # light amber wash (selection / highlight)
    "accent_text": "#5A3D0A",    # readable text on amber backgrounds

    # Status colors — muted, not neon
    "success": "#2E7D46",
    "success_bg": "#E4F2E7",
    "danger": "#B3452F",
    "danger_bg": "#F7E7E1",
    "warning": "#A66A16",
    "warning_bg": "#F7ECD8",
    "neutral": "#6B6656",
    "neutral_bg": "#ECE9DF",

    # Sidebar (dark charcoal-navy, not pure black)
    "sidebar_bg": "#22201B",
    "sidebar_hover": "#2E2B24",
    "sidebar_active_bg": "#38332A",
    "sidebar_text": "#C7C2B3",
    "sidebar_text_muted": "#8A8574",
    "sidebar_text_active": "#FFFFFF",
}


# =============================================================================
# FONTS
# Tkinter falls back gracefully if "Segoe UI" isn't present, but we provide a
# safe secondary choice so the app still looks intentional on Linux/macOS.
# =============================================================================

def _pick_font_family():
    try:
        families = set(tk.font.families())
    except Exception:
        return "Arial"
    for candidate in ("Segoe UI", "Helvetica Neue", "Helvetica", "Arial"):
        if candidate in families:
            return candidate
    return "TkDefaultFont"


_FAMILY = None


def family():
    global _FAMILY
    if _FAMILY is None:
        _FAMILY = _pick_font_family()
    return _FAMILY


def build_fonts():
    """Call once a Tk root exists (font.families() needs a root)."""
    f = family()
    return {
        "brand": (f, 15, "bold"),
        "h1": (f, 21, "bold"),
        "h2": (f, 15, "bold"),
        "h3": (f, 12, "bold"),
        "body": (f, 10),
        "body_bold": (f, 10, "bold"),
        "small": (f, 9),
        "small_bold": (f, 9, "bold"),
        "nav_section": (f, 8, "bold"),
        "nav_item": (f, 10),
        "nav_item_active": (f, 10, "bold"),
        "kpi_value": (f, 22, "bold"),
        "kpi_label": (f, 9, "bold"),
        "mono_value": (f, 13, "bold"),
        "badge": (f, 8, "bold"),
    }


FONTS = {}  # populated by apply_theme() once a Tk root is available


# =============================================================================
# THEME APPLICATION
# =============================================================================

def apply_theme(root):
    """Configure ttk styles and root background. Safe to call once per Toplevel."""
    global FONTS
    if not FONTS:
        FONTS.update(build_fonts())

    root.configure(bg=COLORS["bg"])

    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure(".", background=COLORS["bg"], foreground=COLORS["text"], font=FONTS["body"])
    style.configure("TFrame", background=COLORS["bg"])
    style.configure("Surface.TFrame", background=COLORS["surface"])
    style.configure("TLabel", background=COLORS["bg"], foreground=COLORS["text"], font=FONTS["body"])
    style.configure("Surface.TLabel", background=COLORS["surface"], foreground=COLORS["text"], font=FONTS["body"])

    # ---- Buttons -----------------------------------------------------
    style.configure(
        "Primary.TButton",
        background=COLORS["accent"],
        foreground=COLORS["accent_text"],
        font=FONTS["body_bold"],
        padding=(16, 9),
        borderwidth=0,
        relief="flat",
    )
    style.map(
        "Primary.TButton",
        background=[("active", COLORS["accent_dark"]), ("disabled", COLORS["border"])],
        foreground=[("disabled", COLORS["text_faint"])],
    )

    style.configure(
        "Secondary.TButton",
        background=COLORS["surface"],
        foreground=COLORS["text"],
        font=FONTS["body_bold"],
        padding=(14, 8),
        borderwidth=1,
        relief="solid",
    )
    style.map(
        "Secondary.TButton",
        background=[("active", COLORS["surface_alt"])],
        bordercolor=[("!disabled", COLORS["border_strong"])],
    )

    style.configure(
        "Destructive.TButton",
        background=COLORS["danger"],
        foreground="#FFFFFF",
        font=FONTS["body_bold"],
        padding=(14, 8),
        borderwidth=0,
        relief="flat",
    )
    style.map("Destructive.TButton", background=[("active", "#8F3623")])

    style.configure(
        "Ghost.TButton",
        background=COLORS["bg"],
        foreground=COLORS["text_muted"],
        font=FONTS["body"],
        padding=(12, 8),
        borderwidth=0,
        relief="flat",
    )
    style.map(
        "Ghost.TButton",
        background=[("active", COLORS["surface_alt"])],
        foreground=[("active", COLORS["text"])],
    )

    style.configure(
        "GhostOnSurface.TButton",
        background=COLORS["surface"],
        foreground=COLORS["text_muted"],
        font=FONTS["body"],
        padding=(12, 8),
        borderwidth=0,
        relief="flat",
    )
    style.map(
        "GhostOnSurface.TButton",
        background=[("active", COLORS["surface_alt"])],
        foreground=[("active", COLORS["text"])],
    )

    # ---- Treeview (tables) --------------------------------------------
    style.configure(
        "Treeview",
        background=COLORS["surface"],
        fieldbackground=COLORS["surface"],
        foreground=COLORS["text"],
        rowheight=32,
        font=FONTS["body"],
        borderwidth=0,
        relief="flat",
    )
    style.configure(
        "Treeview.Heading",
        background=COLORS["surface_alt"],
        foreground=COLORS["text_muted"],
        font=FONTS["small_bold"],
        relief="flat",
        padding=(10, 9),
        borderwidth=0,
    )
    style.map(
        "Treeview.Heading",
        background=[("active", COLORS["surface_alt"])],
    )
    style.map(
        "Treeview",
        background=[("selected", COLORS["accent_soft"])],
        foreground=[("selected", COLORS["text"])],
    )
    style.layout("Treeview", [("Treeview.treearea", {"sticky": "nswe"})])

    # ---- Combobox -------------------------------------------------------
    style.configure(
        "TCombobox",
        fieldbackground=COLORS["surface"],
        background=COLORS["surface"],
        foreground=COLORS["text"],
        arrowcolor=COLORS["text_muted"],
        padding=6,
        relief="flat",
    )
    style.map(
        "TCombobox",
        fieldbackground=[("readonly", COLORS["surface"])],
        selectbackground=[("readonly", COLORS["surface"])],
        selectforeground=[("readonly", COLORS["text"])],
        bordercolor=[("focus", COLORS["accent"])],
    )

    # ---- Scrollbar --------------------------------------------------
    style.configure(
        "Vertical.TScrollbar",
        background=COLORS["surface_alt"],
        troughcolor=COLORS["bg"],
        bordercolor=COLORS["bg"],
        arrowcolor=COLORS["text_muted"],
        relief="flat",
    )

    # ---- Notebook (unused currently, styled for consistency) --------
    style.configure("TNotebook", background=COLORS["bg"], borderwidth=0)
    style.configure(
        "TNotebook.Tab",
        background=COLORS["surface_alt"],
        foreground=COLORS["text_muted"],
        font=FONTS["body_bold"],
        padding=(14, 8),
    )
    style.map(
        "TNotebook.Tab",
        background=[("selected", COLORS["surface"])],
        foreground=[("selected", COLORS["text"])],
    )

    return style


# =============================================================================
# SMALL STYLING HELPERS (used across every page for consistent form controls)
# =============================================================================

def entry_kwargs(width=24):
    return dict(
        width=width,
        font=FONTS["body"],
        bg=COLORS["surface"],
        fg=COLORS["text"],
        insertbackground=COLORS["text"],
        relief="flat",
        highlightthickness=1,
        highlightbackground=COLORS["border_strong"],
        highlightcolor=COLORS["accent"],
        bd=0,
    )


def styled_entry(parent, width=24, **overrides):
    kwargs = entry_kwargs(width)
    kwargs.update(overrides)
    return tk.Entry(parent, **kwargs)


def styled_combobox(parent, values, width=20, state="readonly", **overrides):
    box = ttk.Combobox(parent, values=values, width=width, state=state, font=FONTS["body"], **overrides)
    return box


def field_label(parent, text, on_surface=True, **overrides):
    bg = COLORS["surface"] if on_surface else COLORS["bg"]
    kwargs = dict(
        text=text,
        font=FONTS["small_bold"],
        bg=bg,
        fg=COLORS["text_muted"],
        anchor="w",
    )
    kwargs.update(overrides)
    return tk.Label(parent, **kwargs)
