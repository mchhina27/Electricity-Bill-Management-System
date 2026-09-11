"""
Reusable UI building blocks shared by every screen: the app shell (Sidebar,
TopBar), Card panels, status Badges, form helpers, an inline message banner,
a lightweight bar chart, and Treeview row-striping helpers.

Everything here is built from plain tkinter/ttk widgets — no external UI
toolkit is used. Rounded panels and badges are drawn with tk.Canvas rounded
polygons, which is a standard, dependency-free way to get soft corners in
Tkinter.
"""

import tkinter as tk
from tkinter import ttk

from ui import theme
from ui.theme import COLORS


# =============================================================================
# Rounded rectangle helper
# =============================================================================

def _round_rect_points(x1, y1, x2, y2, radius):
    radius = max(0, min(radius, (x2 - x1) / 2, (y2 - y1) / 2))
    return [
        x1 + radius, y1,
        x2 - radius, y1,
        x2, y1,
        x2, y1 + radius,
        x2, y2 - radius,
        x2, y2,
        x2 - radius, y2,
        x1 + radius, y2,
        x1, y2,
        x1, y2 - radius,
        x1, y1 + radius,
        x1, y1,
    ]


# =============================================================================
# Card — flat panel with a moderate rounded corner and a hairline border
# =============================================================================

class Card(tk.Frame):
    """
    A flat, softly-rounded panel used for forms, tables and KPI tiles.
    Put content inside `card.body` (a plain tk.Frame that fills the card).
    """

    def __init__(self, parent, bg=None, radius=10, padding=16, **kwargs):
        outer_bg = kwargs.pop("outer_bg", parent["bg"] if "bg" in parent.keys() else COLORS["bg"])
        super().__init__(parent, bg=outer_bg, highlightthickness=0, bd=0, **kwargs)

        self._bg = bg or COLORS["surface"]
        self._radius = radius
        self._outer_bg = outer_bg
        self._min_w = 0
        self._min_h = 0

        self.canvas = tk.Canvas(self, bg=outer_bg, highlightthickness=0, bd=0)
        self.canvas.pack(fill="both", expand=True)

        self.body = tk.Frame(self.canvas, bg=self._bg, padx=padding, pady=padding)
        self._window = self.canvas.create_window(0, 0, window=self.body, anchor="nw")

        self.canvas.bind("<Configure>", self._redraw)
        # Give the canvas a real minimum size based on the form/content it
        # holds. Without this, a Card placed in an unweighted grid cell (or
        # via plain pack()) collapses to Tk's default 200x200 canvas size
        # instead of sizing to fit its labels/entries/buttons.
        self.body.bind("<Configure>", self._sync_min_size)

    def _sync_min_size(self, _event):
        req_w = self.body.winfo_reqwidth() + 4
        req_h = self.body.winfo_reqheight() + 4
        if req_w != self._min_w or req_h != self._min_h:
            self._min_w, self._min_h = req_w, req_h
            self.canvas.configure(width=req_w, height=req_h)

    def _redraw(self, event):
        w, h = event.width, event.height
        if w < 4 or h < 4:
            return
        self.canvas.delete("bg_shape")
        pts = _round_rect_points(1, 1, w - 1, h - 1, self._radius)
        self.canvas.create_polygon(
            pts, smooth=True, fill=self._bg, outline=COLORS["border"], width=1, tags="bg_shape"
        )
        self.canvas.tag_lower("bg_shape")
        self.canvas.coords(self._window, 1, 1)
        self.canvas.itemconfig(self._window, width=w - 2, height=h - 2)


# =============================================================================
# Badge — small rounded status pill (used outside of tables)
# =============================================================================

_BADGE_KINDS = {
    "success": (COLORS["success_bg"], COLORS["success"]),
    "danger": (COLORS["danger_bg"], COLORS["danger"]),
    "warning": (COLORS["warning_bg"], COLORS["warning"]),
    "accent": (COLORS["accent_soft"], COLORS["accent_text"]),
    "neutral": (COLORS["neutral_bg"], COLORS["neutral"]),
}


class Badge(tk.Canvas):
    def __init__(self, parent, text, kind="neutral", **kwargs):
        bg_color, fg_color = _BADGE_KINDS.get(kind, _BADGE_KINDS["neutral"])
        parent_bg = kwargs.pop("parent_bg", parent["bg"] if "bg" in parent.keys() else COLORS["surface"])
        font = theme.FONTS.get("badge", ("Arial", 8, "bold"))

        probe = tk.Label(parent, text=text, font=font)
        probe.update_idletasks()
        text_w = probe.winfo_reqwidth()
        text_h = probe.winfo_reqheight()
        probe.destroy()

        pad_x, pad_y = 12, 5
        w = text_w + pad_x * 2
        h = text_h + pad_y * 2

        super().__init__(parent, width=w, height=h, bg=parent_bg, highlightthickness=0, bd=0)
        pts = _round_rect_points(0, 0, w, h, h / 2)
        self.create_polygon(pts, smooth=True, fill=bg_color, outline=bg_color)
        self.create_text(w / 2, h / 2, text=text.upper(), font=font, fill=fg_color)


def status_kind(status):
    """Map a domain status string to a Badge/row 'kind' color."""
    s = (status or "").strip().upper()
    if s in ("PAID", "SUCCESS", "ACTIVE"):
        return "success"
    if s in ("OVERDUE", "FAILED", "FAULTY"):
        return "danger"
    if s in ("UNPAID", "PENDING", "INACTIVE"):
        return "warning"
    return "neutral"


# =============================================================================
# Treeview helpers — alternating rows + status-colored text
# =============================================================================

def configure_row_tags(tree):
    """Base alternating-row background tags. Call once per Treeview."""
    tree.tag_configure("evenrow", background=COLORS["surface"])
    tree.tag_configure("oddrow", background=COLORS["surface_alt"])

    for kind, (_, fg) in _BADGE_KINDS.items():
        tree.tag_configure(f"{kind}_even", background=COLORS["surface"], foreground=fg)
        tree.tag_configure(f"{kind}_odd", background=COLORS["surface_alt"], foreground=fg)


def row_tags(index, status=None):
    """Return the tag tuple for a Treeview row given its index and optional status text."""
    parity = "even" if index % 2 == 0 else "odd"
    if status:
        return (f"{status_kind(status)}_{parity}",)
    return (parity + "row",)


# =============================================================================
# Sidebar
# =============================================================================

class Sidebar(tk.Frame):
    WIDTH = 232

    def __init__(self, parent, sections, on_select, brand_title="VOLTGRID", brand_subtitle="ELECTRIC UTILITY"):
        super().__init__(parent, bg=COLORS["sidebar_bg"], width=self.WIDTH)
        self.grid_propagate(False)

        self.on_select = on_select
        self._nav_items = {}
        self._active_key = None

        brand = tk.Frame(self, bg=COLORS["sidebar_bg"])
        brand.pack(fill="x", pady=(24, 16), padx=22)
        tk.Label(
            brand, text=brand_title, font=theme.FONTS["brand"],
            bg=COLORS["sidebar_bg"], fg=COLORS["text_on_dark"]
        ).pack(anchor="w")
        tk.Label(
            brand, text=brand_subtitle, font=theme.FONTS["small"],
            bg=COLORS["sidebar_bg"], fg=COLORS["accent"]
        ).pack(anchor="w", pady=(2, 0))

        tk.Frame(self, bg=COLORS["accent"], height=2).pack(fill="x", padx=22, pady=(0, 8))

        nav_container = tk.Frame(self, bg=COLORS["sidebar_bg"])
        nav_container.pack(fill="both", expand=True)

        for section_title, items in sections:
            tk.Label(
                nav_container, text=section_title, font=theme.FONTS["nav_section"],
                bg=COLORS["sidebar_bg"], fg=COLORS["sidebar_text_muted"], anchor="w"
            ).pack(fill="x", padx=22, pady=(14, 6))

            for key, label in items:
                self._add_nav_item(nav_container, key, label)

        tk.Frame(self, bg=COLORS["sidebar_bg"]).pack(fill="both", expand=True)  # spacer

    def _add_nav_item(self, parent, key, label):
        row = tk.Frame(parent, bg=COLORS["sidebar_bg"], cursor="hand2")
        row.pack(fill="x", padx=10, pady=1)

        indicator = tk.Frame(row, bg=COLORS["sidebar_bg"], width=3)
        indicator.pack(side="left", fill="y")

        lbl = tk.Label(
            row, text=label, font=theme.FONTS["nav_item"], bg=COLORS["sidebar_bg"],
            fg=COLORS["sidebar_text"], anchor="w", padx=14, pady=9
        )
        lbl.pack(side="left", fill="both", expand=True)

        self._nav_items[key] = (row, indicator, lbl)

        def on_click(_event, k=key):
            self.on_select(k)

        def on_enter(_event, k=key):
            if self._active_key != k:
                row.configure(bg=COLORS["sidebar_hover"])
                lbl.configure(bg=COLORS["sidebar_hover"])

        def on_leave(_event, k=key):
            if self._active_key != k:
                row.configure(bg=COLORS["sidebar_bg"])
                lbl.configure(bg=COLORS["sidebar_bg"])

        for widget in (row, lbl):
            widget.bind("<Button-1>", on_click)
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)

    def set_active(self, key):
        for k, (row, indicator, lbl) in self._nav_items.items():
            if k == key:
                row.configure(bg=COLORS["sidebar_active_bg"])
                lbl.configure(bg=COLORS["sidebar_active_bg"], fg=COLORS["sidebar_text_active"],
                               font=theme.FONTS["nav_item_active"])
                indicator.configure(bg=COLORS["accent"])
            else:
                row.configure(bg=COLORS["sidebar_bg"])
                lbl.configure(bg=COLORS["sidebar_bg"], fg=COLORS["sidebar_text"],
                               font=theme.FONTS["nav_item"])
                indicator.configure(bg=COLORS["sidebar_bg"])
        self._active_key = key


# =============================================================================
# TopBar
# =============================================================================

class TopBar(tk.Frame):
    HEIGHT = 72

    def __init__(self, parent, user_label, role_label, on_logout):
        super().__init__(parent, bg=COLORS["surface"], height=self.HEIGHT)
        self.grid_propagate(False)
        self.grid_columnconfigure(0, weight=1)

        tk.Frame(self, bg=COLORS["border"], height=1).place(relx=0, rely=1.0, anchor="sw", relwidth=1)

        text_frame = tk.Frame(self, bg=COLORS["surface"])
        text_frame.grid(row=0, column=0, sticky="w", padx=28, pady=12)

        self.title_label = tk.Label(
            text_frame, text="", font=theme.FONTS["h2"], bg=COLORS["surface"], fg=COLORS["text"]
        )
        self.title_label.pack(anchor="w")

        self.subtitle_label = tk.Label(
            text_frame, text="", font=theme.FONTS["small"], bg=COLORS["surface"], fg=COLORS["text_muted"]
        )
        self.subtitle_label.pack(anchor="w", pady=(2, 0))

        right_frame = tk.Frame(self, bg=COLORS["surface"])
        right_frame.grid(row=0, column=1, sticky="e", padx=28)

        user_box = tk.Frame(right_frame, bg=COLORS["surface"])
        user_box.pack(side="left", padx=(0, 18))
        tk.Label(
            user_box, text=user_label, font=theme.FONTS["body_bold"], bg=COLORS["surface"], fg=COLORS["text"]
        ).pack(anchor="e")
        tk.Label(
            user_box, text=role_label, font=theme.FONTS["small"], bg=COLORS["surface"], fg=COLORS["accent_dark"]
        ).pack(anchor="e")

        ttk.Button(right_frame, text="Log Out", style="Secondary.TButton", command=on_logout).pack(side="left")

    def set_title(self, title, subtitle):
        self.title_label.configure(text=title.upper())
        self.subtitle_label.configure(text=subtitle or "")


# =============================================================================
# Page header (title + description + optional action button, used inside pages)
# =============================================================================

class PageHeader(tk.Frame):
    def __init__(self, parent, title, description, action_text=None, action_command=None):
        super().__init__(parent, bg=COLORS["bg"])
        self.grid_columnconfigure(0, weight=1)

        text_frame = tk.Frame(self, bg=COLORS["bg"])
        text_frame.grid(row=0, column=0, sticky="w")
        tk.Label(
            text_frame, text=title, font=theme.FONTS["h1"], bg=COLORS["bg"], fg=COLORS["text"]
        ).pack(anchor="w")
        if description:
            tk.Label(
                text_frame, text=description, font=theme.FONTS["body"], bg=COLORS["bg"], fg=COLORS["text_muted"]
            ).pack(anchor="w", pady=(3, 0))

        if action_text:
            ttk.Button(
                self, text=action_text, style="Primary.TButton", command=action_command
            ).grid(row=0, column=1, sticky="e")


# =============================================================================
# Inline banner — replaces most messagebox popups for non-destructive feedback
# =============================================================================

class InlineBanner(tk.Frame):
    """
    A colored inline message strip used instead of messagebox popups for
    non-destructive feedback (validation issues, save confirmations, etc).

    Usage: reserve its spot once with `place_in_grid(...)` or `pack_reserve()`,
    then call `.show(message, kind)` / `.hide()` — the layout slot stays put
    either way, so surrounding widgets never jump around.
    """

    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["surface"])
        self._label = tk.Label(
            self, text="", font=theme.FONTS["small_bold"], anchor="w",
            padx=14, pady=9, justify="left", wraplength=520
        )
        self._label.pack(fill="x")
        self._mode = None  # "grid" or "pack"

    def place_in_grid(self, row, column=0, columnspan=1, sticky="ew", pady=(0, 12), **kwargs):
        self._mode = "grid"
        self.grid(row=row, column=column, columnspan=columnspan, sticky=sticky, pady=pady, **kwargs)
        self.grid_remove()

    def pack_reserve(self, **kwargs):
        self._mode = "pack"
        pack_kwargs = dict(fill="x", pady=(0, 12))
        pack_kwargs.update(kwargs)
        self.pack(**pack_kwargs)
        self.pack_forget()

    def show(self, message, kind="success"):
        bg, fg = _BADGE_KINDS.get(kind, _BADGE_KINDS["neutral"])
        self._label.configure(text=message, bg=bg, fg=fg)
        self.configure(bg=bg)
        if self._mode == "grid":
            self.grid()
        elif self._mode == "pack":
            self.pack(fill="x", pady=(0, 12))
        else:
            self.pack(fill="x", pady=(0, 12))
            self._mode = "pack"

    def hide(self):
        if self._mode == "grid":
            self.grid_remove()
        elif self._mode == "pack":
            self.pack_forget()


# =============================================================================
# Search bar with placeholder text
# =============================================================================

class SearchBar(tk.Frame):
    def __init__(self, parent, placeholder="Search...", on_change=None, width=30):
        super().__init__(parent, bg=COLORS["surface"], highlightthickness=1,
                          highlightbackground=COLORS["border_strong"])
        self._placeholder = placeholder
        self._on_change = on_change
        self._showing_placeholder = True

        tk.Label(self, text="Search", font=theme.FONTS["small"], bg=COLORS["surface"],
                 fg=COLORS["text_faint"]).pack(side="left", padx=(10, 4))

        self.entry = tk.Entry(
            self, width=width, font=theme.FONTS["body"], bg=COLORS["surface"], fg=COLORS["text_faint"],
            relief="flat", bd=0, highlightthickness=0, insertbackground=COLORS["text"]
        )
        self.entry.pack(side="left", fill="x", expand=True, ipady=6, padx=(0, 10))
        self.entry.insert(0, placeholder)

        self.entry.bind("<FocusIn>", self._clear_placeholder)
        self.entry.bind("<FocusOut>", self._restore_placeholder)
        self.entry.bind("<KeyRelease>", self._changed)

    def _clear_placeholder(self, _event):
        if self._showing_placeholder:
            self.entry.delete(0, tk.END)
            self.entry.configure(fg=COLORS["text"])
            self._showing_placeholder = False

    def _restore_placeholder(self, _event):
        if not self.entry.get().strip():
            self.entry.insert(0, self._placeholder)
            self.entry.configure(fg=COLORS["text_faint"])
            self._showing_placeholder = True

    def _changed(self, _event):
        if self._on_change:
            self._on_change(self.get())

    def get(self):
        if self._showing_placeholder:
            return ""
        return self.entry.get().strip()


# =============================================================================
# Empty state — shown instead of fabricated data when a table/report has none
# =============================================================================

class EmptyState(tk.Frame):
    def __init__(self, parent, message, subtext=None):
        super().__init__(parent, bg=COLORS["surface"])
        tk.Label(
            self, text=message, font=theme.FONTS["body_bold"], bg=COLORS["surface"], fg=COLORS["text_muted"]
        ).pack(pady=(28, 2))
        if subtext:
            tk.Label(
                self, text=subtext, font=theme.FONTS["small"], bg=COLORS["surface"], fg=COLORS["text_faint"]
            ).pack(pady=(0, 28))
        else:
            tk.Frame(self, bg=COLORS["surface"], height=20).pack()


# =============================================================================
# KPI tile — used on the Dashboard
# =============================================================================

class KpiTile(Card):
    def __init__(self, parent, label, value, accent="neutral", footnote=None):
        super().__init__(parent, bg=COLORS["surface"], radius=10, padding=16, outer_bg=COLORS["bg"])
        _, fg = _BADGE_KINDS.get(accent, _BADGE_KINDS["neutral"])

        tk.Frame(self.body, bg=fg, height=3, width=28).pack(anchor="w", pady=(0, 10))

        self.value_label = tk.Label(
            self.body, text=str(value), font=theme.FONTS["kpi_value"], bg=COLORS["surface"], fg=COLORS["text"]
        )
        self.value_label.pack(anchor="w")

        tk.Label(
            self.body, text=label.upper(), font=theme.FONTS["kpi_label"], bg=COLORS["surface"],
            fg=COLORS["text_muted"]
        ).pack(anchor="w", pady=(4, 0))

        if footnote:
            tk.Label(
                self.body, text=footnote, font=theme.FONTS["small"], bg=COLORS["surface"],
                fg=COLORS["text_faint"]
            ).pack(anchor="w", pady=(6, 0))

    def set_value(self, value):
        self.value_label.configure(text=str(value))


# =============================================================================
# Simple bar chart — dependency-free Canvas chart (no matplotlib)
# =============================================================================

class SimpleBarChart(tk.Canvas):
    """
    A minimal bar chart drawn on a Canvas: no external charting library.
    `data` is a list of (label, numeric_value) tuples.
    """

    def __init__(self, parent, data, height=180, bar_color=None, value_format="{:.0f}"):
        super().__init__(parent, bg=COLORS["surface"], highlightthickness=0, bd=0, height=height)
        self._data = data or []
        self._bar_color = bar_color or COLORS["accent"]
        self._value_format = value_format
        self.bind("<Configure>", self._draw)

    def set_data(self, data):
        self._data = data or []
        self._draw(None)

    def _draw(self, _event):
        self.delete("all")
        w = self.winfo_width()
        h = self.winfo_height()
        if w < 20 or h < 20:
            return

        if not self._data:
            self.create_text(
                w / 2, h / 2, text="No billing data yet", font=theme.FONTS["small"], fill=COLORS["text_faint"]
            )
            return

        pad_left, pad_right, pad_top, pad_bottom = 8, 8, 18, 24
        chart_w = w - pad_left - pad_right
        chart_h = h - pad_top - pad_bottom

        values = [v for _, v in self._data]
        max_val = max(values) if values else 0
        if max_val <= 0:
            max_val = 1

        n = len(self._data)
        slot_w = chart_w / n
        bar_w = max(10, slot_w * 0.5)

        # baseline
        self.create_line(
            pad_left, pad_top + chart_h, w - pad_right, pad_top + chart_h, fill=COLORS["border_strong"]
        )

        for i, (label, value) in enumerate(self._data):
            slot_x = pad_left + i * slot_w
            bar_h = (value / max_val) * chart_h if max_val else 0
            x1 = slot_x + (slot_w - bar_w) / 2
            x2 = x1 + bar_w
            y2 = pad_top + chart_h
            y1 = y2 - bar_h

            pts = _round_rect_points(x1, y1, x2, y2, radius=min(5, bar_w / 2))
            self.create_polygon(pts, smooth=True, fill=self._bar_color, outline=self._bar_color)

            if value:
                self.create_text(
                    (x1 + x2) / 2, max(y1 - 10, 10),
                    text=self._value_format.format(value), font=theme.FONTS["small"], fill=COLORS["text_muted"]
                )

            self.create_text(
                (x1 + x2) / 2, pad_top + chart_h + 12,
                text=label, font=theme.FONTS["small"], fill=COLORS["text_faint"]
            )


# =============================================================================
# Convenience field builder used in forms across pages
# =============================================================================

def form_field(parent, row, column, label_text, factory, colspan=1, padx=(0, 18), pady=(0, 14)):
    """
    Places a stacked label+widget in a grid cell (label above the input),
    which reads more like a real application form than the original
    label-left / entry-right layout.

    `factory` is a callable that receives the cell frame as its parent and
    returns the created widget, e.g.:
        entry = form_field(grid, 0, 0, "First Name", lambda p: theme.styled_entry(p))
    """
    bg = parent["bg"] if "bg" in parent.keys() else COLORS["surface"]
    cell = tk.Frame(parent, bg=bg)
    cell.grid(row=row, column=column, columnspan=colspan, sticky="ew", padx=padx, pady=pady)
    theme.field_label(cell, label_text, on_surface=(bg != COLORS["bg"])).pack(anchor="w", pady=(0, 5))
    widget = factory(cell)
    widget.pack(anchor="w", fill="x")
    return widget


# =============================================================================
# ScrollableFrame -- lets an entire page/content area scroll vertically
# when the window is too small to show everything at once.
# =============================================================================

class ScrollableFrame(tk.Frame):
    """
    Wrap a content area in this, then build your page(s) inside
    `scrollable.inner` instead of directly inside the original parent.
    The vertical scrollbar (and mouse wheel) only appear/act when content
    is actually taller than the visible area.
    """

    def __init__(self, parent, bg=None):
        bg = bg or COLORS["bg"]
        super().__init__(parent, bg=bg)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0, bd=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        self.vbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.vbar.grid(row=0, column=1, sticky="ns")
        self.canvas.configure(yscrollcommand=self.vbar.set)

        self.inner = tk.Frame(self.canvas, bg=bg)
        self.inner.grid_columnconfigure(0, weight=1)
        self._window = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")

        self.inner.bind("<Configure>", self._on_inner_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.bind("<Enter>", self._bind_mousewheel)
        self.canvas.bind("<Leave>", self._unbind_mousewheel)

    def _on_inner_configure(self, _event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self._window, width=event.width)

    def _bind_mousewheel(self, _event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel_linux)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel_linux)

    def _unbind_mousewheel(self, _event):
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_mousewheel_linux(self, event):
        direction = -1 if event.num == 4 else 1
        self.canvas.yview_scroll(direction, "units")
