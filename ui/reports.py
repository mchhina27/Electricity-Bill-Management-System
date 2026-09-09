"""
Reports page (embedded in the admin shell content area).

Still calls the exact same service functions:
    get_dashboard_statistics from services/report_service.py
    get_all_bills from services/bill_service.py (for the status/trend breakdown,
    the same real data the Dashboard page also uses)

No fabricated statistics -- if there is no data, an empty state is shown
instead of invented numbers.
"""

import tkinter as tk
from tkinter import ttk
from collections import OrderedDict

from ui import theme
from ui.theme import COLORS
from ui import components
from ui.components import Card, PageHeader, EmptyState, SimpleBarChart

from services.report_service import get_dashboard_statistics
from services.bill_service import get_all_bills


def _currency(value):
    try:
        return f"\u20b9{float(value):,.2f}"
    except (TypeError, ValueError):
        return "\u20b90.00"


class ReportsPage(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["bg"])

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        container = tk.Frame(self, bg=COLORS["bg"])
        container.grid(row=0, column=0, sticky="nsew", padx=28, pady=22)
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(3, weight=1)

        header = PageHeader(
            container,
            "Reports & Statistics",
            "Billing and collection summary across the system."
        )
        header.grid(row=0, column=0, sticky="ew", pady=(0, 4))

        refresh_row = tk.Frame(container, bg=COLORS["bg"])
        refresh_row.grid(row=1, column=0, sticky="e", pady=(0, 14))
        ttk.Button(
            refresh_row, text="Refresh Statistics", style="Secondary.TButton", command=self.reload
        ).pack()

        self.body_container = tk.Frame(container, bg=COLORS["bg"])
        self.body_container.grid(row=3, column=0, sticky="nsew")
        self.body_container.grid_columnconfigure(0, weight=1)
        self.body_container.grid_rowconfigure(1, weight=1)

        self.reload()

    def reload(self):
        for w in self.body_container.winfo_children():
            w.destroy()

        stats = get_dashboard_statistics() or {}
        bills = get_all_bills() or []

        self._build_kpis(stats)
        self._build_breakdown(bills)

    # -----------------------------------------------------------------
    def _build_kpis(self, stats):
        total_billed = float(stats.get("total_billed", 0) or 0)
        total_collected = float(stats.get("total_collected", 0) or 0)
        outstanding = max(total_billed - total_collected, 0)

        tiles = [
            ("Total Customers", stats.get("total_customers", 0), "neutral"),
            ("Total Meters", stats.get("total_meters", 0), "neutral"),
            ("Total Bills", stats.get("total_bills", 0), "neutral"),
            ("Total Billed", _currency(total_billed), "accent"),
            ("Total Collected", _currency(total_collected), "success"),
            ("Unpaid Bills", stats.get("unpaid_bills", 0), "warning" if stats.get("unpaid_bills", 0) else "success"),
        ]

        grid = tk.Frame(self.body_container, bg=COLORS["bg"])
        grid.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        for i in range(3):
            grid.grid_columnconfigure(i, weight=1, uniform="report_kpi")

        for i, (label, value, accent) in enumerate(tiles):
            tile = components.KpiTile(grid, label, value, accent=accent)
            r, c = divmod(i, 3)
            tile.grid(row=r, column=c, sticky="nsew", padx=(0 if c == 0 else 8, 0), pady=(0 if r == 0 else 8, 0))
            grid.grid_rowconfigure(r, minsize=110)

        if total_billed and outstanding:
            note = f"Outstanding amount (billed \u2212 collected): {_currency(outstanding)}"
            tk.Label(
                self.body_container, text=note, font=theme.FONTS["small"],
                bg=COLORS["bg"], fg=COLORS["text_muted"]
            ).grid(row=0, column=0, sticky="sw")

    # -----------------------------------------------------------------
    def _build_breakdown(self, bills):
        row_frame = tk.Frame(self.body_container, bg=COLORS["bg"])
        row_frame.grid(row=1, column=0, sticky="nsew")
        row_frame.grid_columnconfigure(0, weight=2)
        row_frame.grid_columnconfigure(1, weight=1)
        row_frame.grid_rowconfigure(0, weight=1)

        # ---- Monthly billing trend ----
        trend_card = Card(row_frame, radius=10, padding=18)
        trend_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        tk.Label(
            trend_card.body, text="MONTHLY BILLING TOTAL", font=theme.FONTS["h3"],
            bg=COLORS["surface"], fg=COLORS["text"]
        ).pack(anchor="w")
        tk.Label(
            trend_card.body, text="Total amount billed, grouped by billing month",
            font=theme.FONTS["small"], bg=COLORS["surface"], fg=COLORS["text_muted"]
        ).pack(anchor="w", pady=(2, 12))

        monthly_totals = self._monthly_totals(bills)
        if monthly_totals:
            SimpleBarChart(trend_card.body, monthly_totals, height=180, value_format="\u20b9{:,.0f}").pack(
                fill="both", expand=True
            )
        else:
            EmptyState(trend_card.body, "No billing data yet", "Generate bills to see a monthly trend here.").pack(
                fill="both", expand=True
            )

        # ---- Status breakdown ----
        status_card = Card(row_frame, radius=10, padding=18)
        status_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        tk.Label(
            status_card.body, text="BILL STATUS BREAKDOWN", font=theme.FONTS["h3"],
            bg=COLORS["surface"], fg=COLORS["text"]
        ).pack(anchor="w")
        tk.Label(
            status_card.body, text="Across all generated bills",
            font=theme.FONTS["small"], bg=COLORS["surface"], fg=COLORS["text_muted"]
        ).pack(anchor="w", pady=(2, 14))

        if bills:
            counts = OrderedDict()
            for bill in bills:
                status = (bill.get("status") or "UNKNOWN").upper()
                counts[status] = counts.get(status, 0) + 1
            total = len(bills)

            for status, count in counts.items():
                row = tk.Frame(status_card.body, bg=COLORS["surface"])
                row.pack(fill="x", pady=6)
                components.Badge(row, status, kind=components.status_kind(status)).pack(side="left")
                pct = (count / total) * 100 if total else 0
                tk.Label(
                    row, text=f"{count} bills  \u00b7  {pct:.0f}%", font=theme.FONTS["body"],
                    bg=COLORS["surface"], fg=COLORS["text_muted"]
                ).pack(side="right")
        else:
            EmptyState(status_card.body, "Nothing to summarize", "Bill statuses will appear here.").pack(
                fill="both", expand=True
            )

    @staticmethod
    def _monthly_totals(bills):
        totals = OrderedDict()
        for bill in bills:
            month_raw = str(bill.get("billing_month") or "")
            key = month_raw[:7] if len(month_raw) >= 7 else (month_raw or "\u2014")
            amount = float(bill.get("total_amount") or 0)
            totals[key] = totals.get(key, 0) + amount

        ordered_keys = sorted(totals.keys())[-6:]
        return [(k, totals[k]) for k in ordered_keys]
