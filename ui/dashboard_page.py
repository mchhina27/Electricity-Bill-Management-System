"""
Admin Dashboard overview page — the landing screen inside the admin shell.

All figures come from existing service functions:
  - services.report_service.get_dashboard_statistics()   -> KPI totals
  - services.bill_service.get_all_bills()                 -> recent activity
                                                               + monthly trend
No new SQL/business logic is introduced; the monthly trend is a plain-Python
grouping of bills already returned by get_all_bills(), and "Outstanding
Amount" is total_billed - total_collected, both already provided by the
report service.
"""

import tkinter as tk
from tkinter import ttk
from collections import OrderedDict

from ui import theme
from ui.theme import COLORS
from ui import components
from ui.components import Card, KpiTile, PageHeader, EmptyState, SimpleBarChart

from services.report_service import get_dashboard_statistics
from services.bill_service import get_all_bills


def _format_currency(amount):
    try:
        return f"₹{float(amount):,.2f}"
    except (TypeError, ValueError):
        return "₹0.00"


class DashboardPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["bg"])

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        container = tk.Frame(self, bg=COLORS["bg"])
        container.grid(row=0, column=0, sticky="nsew", padx=28, pady=22)
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(3, weight=1)

        PageHeader(
            container,
            "Dashboard",
            "A live snapshot of customers, billing and collections."
        ).grid(row=0, column=0, sticky="ew", pady=(0, 18))

        self.stats = get_dashboard_statistics() or {}
        self.bills = get_all_bills() or []

        self._build_kpis(container, row=1)
        self._build_middle_row(container, row=2)
        self._build_recent_activity(container, row=3)

    # -----------------------------------------------------------------
    # KPI row
    # -----------------------------------------------------------------

    def _build_kpis(self, parent, row):
        kpi_row = tk.Frame(parent, bg=COLORS["bg"])
        kpi_row.grid(row=row, column=0, sticky="ew", pady=(0, 18))

        for i in range(4):
            kpi_row.grid_columnconfigure(i, weight=1, uniform="kpi")

        total_billed = float(self.stats.get("total_billed", 0) or 0)
        total_collected = float(self.stats.get("total_collected", 0) or 0)
        outstanding = max(total_billed - total_collected, 0)

        tiles = [
            ("Total Customers", self.stats.get("total_customers", 0), "neutral", None),
            ("Total Bills", self.stats.get("total_bills", 0), "neutral",
             f"{self.stats.get('unpaid_bills', 0)} unpaid"),
            ("Amount Collected", _format_currency(total_collected), "success", None),
            ("Outstanding Amount", _format_currency(outstanding), "warning" if outstanding else "success", None),
        ]

        for i, (label, value, accent, footnote) in enumerate(tiles):
            tile = KpiTile(kpi_row, label, value, accent=accent, footnote=footnote)
            tile.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 8, 0))
            kpi_row.grid_rowconfigure(0, minsize=118)

    # -----------------------------------------------------------------
    # Middle row: monthly trend chart + status summary
    # -----------------------------------------------------------------

    def _build_middle_row(self, parent, row):
        row_frame = tk.Frame(parent, bg=COLORS["bg"])
        row_frame.grid(row=row, column=0, sticky="nsew", pady=(0, 18))
        row_frame.grid_columnconfigure(0, weight=2)
        row_frame.grid_columnconfigure(1, weight=1)
        row_frame.grid_rowconfigure(0, weight=1)

        # ---- Monthly billing trend --------------------------------
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

        monthly_totals = self._monthly_totals()
        if monthly_totals:
            chart = SimpleBarChart(
                trend_card.body, monthly_totals, height=170, value_format="₹{:,.0f}"
            )
            chart.pack(fill="both", expand=True)
        else:
            EmptyState(
                trend_card.body, "No bills generated yet",
                "Generated bills will appear here as a monthly trend."
            ).pack(fill="both", expand=True)

        # ---- Status summary ------------------------------------------
        status_card = Card(row_frame, radius=10, padding=18)
        status_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        tk.Label(
            status_card.body, text="BILL STATUS SUMMARY", font=theme.FONTS["h3"],
            bg=COLORS["surface"], fg=COLORS["text"]
        ).pack(anchor="w")
        tk.Label(
            status_card.body, text="Across all generated bills",
            font=theme.FONTS["small"], bg=COLORS["surface"], fg=COLORS["text_muted"]
        ).pack(anchor="w", pady=(2, 14))

        if self.bills:
            self._build_status_summary(status_card.body)
        else:
            EmptyState(status_card.body, "Nothing to summarize", "Bill statuses will appear here.").pack(
                fill="both", expand=True
            )

    def _build_status_summary(self, parent):
        counts = OrderedDict()
        for bill in self.bills:
            status = (bill.get("status") or "UNKNOWN").upper()
            counts[status] = counts.get(status, 0) + 1

        total = len(self.bills)

        for status, count in counts.items():
            row = tk.Frame(parent, bg=COLORS["surface"])
            row.pack(fill="x", pady=6)

            components.Badge(row, status, kind=components.status_kind(status)).pack(side="left")

            pct = (count / total) * 100 if total else 0
            tk.Label(
                row, text=f"{count} bills  ·  {pct:.0f}%", font=theme.FONTS["body"],
                bg=COLORS["surface"], fg=COLORS["text_muted"]
            ).pack(side="right")

    # -----------------------------------------------------------------
    # Recent activity
    # -----------------------------------------------------------------

    def _build_recent_activity(self, parent, row):
        card = Card(parent, radius=10, padding=18)
        card.grid(row=row, column=0, sticky="nsew")
        card.body.grid_columnconfigure(0, weight=1)
        card.body.grid_rowconfigure(1, weight=1)

        tk.Label(
            card.body, text="RECENT BILLS", font=theme.FONTS["h3"],
            bg=COLORS["surface"], fg=COLORS["text"]
        ).grid(row=0, column=0, sticky="w", pady=(0, 12))

        recent = self.bills[:8]  # get_all_bills() is already ordered newest-first

        if not recent:
            EmptyState(card.body, "No bills yet", "Generated bills will show up here.").grid(
                row=1, column=0, sticky="nsew"
            )
            return

        columns = ("bill_id", "customer_name", "billing_month", "units_consumed", "total_amount", "due_date", "status")
        headings = {
            "bill_id": "Bill ID",
            "customer_name": "Customer",
            "billing_month": "Billing Month",
            "units_consumed": "Units",
            "total_amount": "Amount",
            "due_date": "Due Date",
            "status": "Status",
        }

        tree = ttk.Treeview(card.body, columns=columns, show="headings", height=len(recent))
        for col in columns:
            tree.heading(col, text=headings[col])
            tree.column(col, width=130, anchor="center")
        tree.column("customer_name", width=170, anchor="w")

        components.configure_row_tags(tree)

        for i, bill in enumerate(recent):
            tree.insert(
                "", tk.END,
                values=(
                    bill.get("bill_id", ""),
                    bill.get("customer_name", ""),
                    bill.get("billing_month", ""),
                    bill.get("units_consumed", ""),
                    _format_currency(bill.get("total_amount", 0)),
                    bill.get("due_date", ""),
                    bill.get("status", ""),
                ),
                tags=components.row_tags(i, bill.get("status")),
            )

        tree.grid(row=1, column=0, sticky="nsew")

    def _monthly_totals(self):
        """Group bill total_amount by the YYYY-MM prefix of billing_month."""
        totals = OrderedDict()
        for bill in self.bills:
            month_raw = str(bill.get("billing_month") or "")
            key = month_raw[:7] if len(month_raw) >= 7 else (month_raw or "—")
            amount = float(bill.get("total_amount") or 0)
            totals[key] = totals.get(key, 0) + amount

        # Keep the most recent 6 months in chronological order.
        ordered_keys = sorted(totals.keys())[-6:]
        return [(k, totals[k]) for k in ordered_keys]
