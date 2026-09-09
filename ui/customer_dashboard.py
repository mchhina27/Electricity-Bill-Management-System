"""
Customer-facing dashboard -- simpler than the admin shell (no sidebar),
but built from the same design system so it feels like the same product.

Still calls the exact same service function with the exact same argument:
    get_customer_bills(customer_id) from services/bill_service.py
"""

import tkinter as tk
from tkinter import ttk

from ui import theme
from ui.theme import COLORS
from ui import components
from ui.components import Card, KpiTile, EmptyState

from services.bill_service import get_customer_bills


TABLE_COLUMNS = (
    "bill_id", "billing_month", "previous_reading", "current_reading",
    "units_consumed", "total_amount", "due_date", "status",
)

TABLE_HEADINGS = {
    "bill_id": "Bill ID",
    "billing_month": "Billing Month",
    "previous_reading": "Previous",
    "current_reading": "Current",
    "units_consumed": "Units",
    "total_amount": "Amount",
    "due_date": "Due Date",
    "status": "Status",
}


def _currency(value):
    try:
        return f"\u20b9{float(value):,.2f}"
    except (TypeError, ValueError):
        return "\u20b90.00"


class CustomerDashboard:

    def __init__(self, customer_id, on_logout=None):
        self.customer_id = customer_id
        self.on_logout = on_logout

        self.window = tk.Toplevel()
        self.window.title("Electricity Billing Management System — Customer Portal")
        self.window.geometry("1100x720")
        self.window.minsize(860, 560)

        theme.apply_theme(self.window)

        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_rowconfigure(1, weight=1)

        top = tk.Frame(self.window, bg=COLORS["surface"], height=72)
        top.grid(row=0, column=0, sticky="ew")
        top.grid_propagate(False)
        top.grid_columnconfigure(0, weight=1)

        tk.Frame(top, bg=COLORS["border"], height=1).place(relx=0, rely=1.0, anchor="sw", relwidth=1)

        text_frame = tk.Frame(top, bg=COLORS["surface"])
        text_frame.grid(row=0, column=0, sticky="w", padx=28, pady=14)
        tk.Label(
            text_frame, text="CUSTOMER PORTAL", font=theme.FONTS["h2"], bg=COLORS["surface"], fg=COLORS["text"]
        ).pack(anchor="w")
        tk.Label(
            text_frame, text=f"Account: {self.customer_id}", font=theme.FONTS["small"],
            bg=COLORS["surface"], fg=COLORS["text_muted"]
        ).pack(anchor="w", pady=(2, 0))

        ttk.Button(
            top, text="Log Out", style="Secondary.TButton", command=self.logout
        ).grid(row=0, column=1, sticky="e", padx=28)

        content = tk.Frame(self.window, bg=COLORS["bg"])
        content.grid(row=1, column=0, sticky="nsew")
        content.grid_columnconfigure(0, weight=1)
        content.grid_rowconfigure(2, weight=1)

        self.container = tk.Frame(content, bg=COLORS["bg"])
        self.container.grid(row=0, column=0, sticky="nsew", padx=28, pady=22)
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_rowconfigure(2, weight=1)

        self.window.protocol("WM_DELETE_WINDOW", self.logout)

        self.load_bills()

    # -----------------------------------------------------------------
    def logout(self):
        self.window.destroy()
        if self.on_logout:
            self.on_logout()

    # -----------------------------------------------------------------
    def load_bills(self):
        for w in self.container.winfo_children():
            w.destroy()

        bills = get_customer_bills(self.customer_id) or []

        self._build_summary(bills)
        self._build_table(bills)

    def _build_summary(self, bills):
        outstanding = sum(float(b.get("total_amount", 0) or 0) for b in bills if (b.get("status") or "").upper() != "PAID")
        unpaid_count = sum(1 for b in bills if (b.get("status") or "").upper() != "PAID")

        header_row = tk.Frame(self.container, bg=COLORS["bg"])
        header_row.grid(row=0, column=0, sticky="ew", pady=(0, 4))
        tk.Label(
            header_row, text="Billing Summary", font=theme.FONTS["h1"], bg=COLORS["bg"], fg=COLORS["text"]
        ).pack(side="left")
        ttk.Button(
            header_row, text="Refresh", style="Secondary.TButton", command=self.load_bills
        ).pack(side="right")

        kpi_row = tk.Frame(self.container, bg=COLORS["bg"])
        kpi_row.grid(row=1, column=0, sticky="ew", pady=(14, 18))
        for i in range(3):
            kpi_row.grid_columnconfigure(i, weight=1, uniform="cust_kpi")

        tiles = [
            ("Amount Due", _currency(outstanding), "warning" if outstanding else "success"),
            ("Unpaid Bills", unpaid_count, "warning" if unpaid_count else "success"),
            ("Total Bills on Record", len(bills), "neutral"),
        ]
        for i, (label, value, accent) in enumerate(tiles):
            tile = KpiTile(kpi_row, label, value, accent=accent)
            tile.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 8, 0))
            kpi_row.grid_rowconfigure(0, minsize=110)

    def _build_table(self, bills):
        card = Card(self.container, radius=10, padding=18)
        card.grid(row=2, column=0, sticky="nsew")
        card.body.grid_columnconfigure(0, weight=1)
        card.body.grid_rowconfigure(1, weight=1)

        tk.Label(
            card.body, text="YOUR BILLS", font=theme.FONTS["h3"], bg=COLORS["surface"], fg=COLORS["text"]
        ).grid(row=0, column=0, sticky="w", pady=(0, 12))

        table_wrap = tk.Frame(card.body, bg=COLORS["surface"])
        table_wrap.grid(row=1, column=0, sticky="nsew")
        table_wrap.grid_columnconfigure(0, weight=1)
        table_wrap.grid_rowconfigure(0, weight=1)

        if not bills:
            EmptyState(
                table_wrap, "No bills on record yet", "Your electricity bills will appear here once generated."
            ).grid(row=0, column=0, sticky="nsew")
            return

        table = ttk.Treeview(table_wrap, columns=TABLE_COLUMNS, show="headings")
        for col in TABLE_COLUMNS:
            table.heading(col, text=TABLE_HEADINGS[col])
            table.column(col, width=120, anchor="center")

        components.configure_row_tags(table)

        scrollbar = ttk.Scrollbar(table_wrap, orient=tk.VERTICAL, command=table.yview)
        table.configure(yscrollcommand=scrollbar.set)

        table.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        for i, bill in enumerate(bills):
            table.insert(
                "", tk.END,
                values=(
                    bill["bill_id"],
                    bill["billing_month"],
                    bill["previous_reading"],
                    bill["current_reading"],
                    bill["units_consumed"],
                    _currency(bill["total_amount"]),
                    bill["due_date"],
                    bill["status"],
                ),
                tags=components.row_tags(i, bill.get("status")),
            )
