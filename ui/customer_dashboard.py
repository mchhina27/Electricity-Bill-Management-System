"""
Customer-facing dashboard -- simpler than the admin/employee shells (no
sidebar), built from the same design system.

IMPORTANT FIX: this is opened with the customer's real customer_id (linked
via users.customer_id at login), never a username -- so every query here
is naturally scoped to one customer's own data. get_customer_bills(),
get_grievances_for_customer() and the ownership check inside make_payment()
all take customer_id, so this dashboard can never load or act on another
customer's bills, payments or grievances.
"""

import tkinter as tk
from tkinter import ttk

from ui import theme
from ui.theme import COLORS
from ui import components
from ui.components import Card, KpiTile, EmptyState, InlineBanner, ScrollableFrame

from services.bill_service import get_customer_bills
from services.customer_service import get_customer_by_id
from services.payment_service import make_payment
from services.grievance_service import (
    submit_grievance,
    get_grievances_for_customer,
    VALID_CATEGORIES,
)


BILLS_COLUMNS = (
    "bill_id", "billing_month", "previous_reading", "current_reading",
    "units_consumed", "total_amount", "late_fee", "due_date", "status",
)
BILLS_HEADINGS = {
    "bill_id": "Bill ID",
    "billing_month": "Billing Month",
    "previous_reading": "Previous",
    "current_reading": "Current",
    "units_consumed": "Units",
    "total_amount": "Amount",
    "late_fee": "Late Fee",
    "due_date": "Due Date",
    "status": "Status",
}

GRIEVANCE_COLUMNS = ("grievance_id", "category", "related_bill_id", "status", "submitted_at")
GRIEVANCE_HEADINGS = {
    "grievance_id": "ID",
    "category": "Category",
    "related_bill_id": "Bill ID",
    "status": "Status",
    "submitted_at": "Submitted",
}

PAYMENT_METHODS = ["CASH", "CARD", "UPI", "NET_BANKING"]


def _currency(value):
    try:
        return f"\u20b9{float(value):,.2f}"
    except (TypeError, ValueError):
        return "\u20b90.00"


class CustomerDashboard:

    def __init__(self, customer_id, on_logout=None):
        self.customer_id = customer_id
        self.on_logout = on_logout
        self.selected_bill = None
        self._bills_by_id = {}

        self.window = tk.Toplevel()
        self.window.title("Electricity Billing Management System — Customer Portal")
        self.window.geometry("1100x760")
        self.window.minsize(860, 560)

        theme.apply_theme(self.window)

        customer = get_customer_by_id(self.customer_id) or {}
        display_name = f'{customer.get("first_name", "")} {customer.get("last_name", "")}'.strip() or "Customer"

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
            text_frame, text=f"{display_name}  \u00b7  Customer ID {self.customer_id}", font=theme.FONTS["small"],
            bg=COLORS["surface"], fg=COLORS["text_muted"]
        ).pack(anchor="w", pady=(2, 0))

        ttk.Button(
            top, text="Log Out", style="Secondary.TButton", command=self.logout
        ).grid(row=0, column=1, sticky="e", padx=28)

        self.content_scroll = ScrollableFrame(self.window, bg=COLORS["bg"])
        self.content_scroll.grid(row=1, column=0, sticky="nsew")
        self.container = self.content_scroll.inner

        self.container.grid_columnconfigure(0, weight=1)
        self.wrap = tk.Frame(self.container, bg=COLORS["bg"])
        self.wrap.grid(row=0, column=0, sticky="ew", padx=28, pady=22)
        self.wrap.grid_columnconfigure(0, weight=1)

        self.window.protocol("WM_DELETE_WINDOW", self.logout)

        self.refresh()

    # -----------------------------------------------------------------
    def logout(self):
        self.window.destroy()
        if self.on_logout:
            self.on_logout()

    # -----------------------------------------------------------------
    def refresh(self):
        for w in self.wrap.winfo_children():
            w.destroy()

        bills = get_customer_bills(self.customer_id) or []
        self._bills_by_id = {str(b["bill_id"]): b for b in bills}

        self._build_summary(bills, row=0)
        self._build_bills_and_payment(bills, row=1)
        self._build_grievances(row=2)

    # -----------------------------------------------------------------
    def _build_summary(self, bills, row):
        outstanding = sum(
            float(b.get("total_amount", 0) or 0) for b in bills if (b.get("status") or "").upper() != "PAID"
        )
        unpaid_count = sum(1 for b in bills if (b.get("status") or "").upper() != "PAID")

        header_row = tk.Frame(self.wrap, bg=COLORS["bg"])
        header_row.grid(row=row, column=0, sticky="ew", pady=(0, 4))
        tk.Label(
            header_row, text="Billing Summary", font=theme.FONTS["h1"], bg=COLORS["bg"], fg=COLORS["text"]
        ).pack(side="left")
        ttk.Button(header_row, text="Refresh", style="Secondary.TButton", command=self.refresh).pack(side="right")

        kpi_row = tk.Frame(self.wrap, bg=COLORS["bg"])
        kpi_row.grid(row=row + 1, column=0, sticky="ew", pady=(14, 18))
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

    # -----------------------------------------------------------------
    def _build_bills_and_payment(self, bills, row):
        section = tk.Frame(self.wrap, bg=COLORS["bg"])
        section.grid(row=row, column=0, sticky="ew", pady=(0, 22))
        section.grid_columnconfigure(0, weight=2)
        section.grid_columnconfigure(1, weight=1)

        # ---- Bills table ----
        table_card = Card(section, radius=10, padding=18)
        table_card.grid(row=0, column=0, sticky="nsew", padx=(0, 16))

        tk.Label(
            table_card.body, text="YOUR BILLS", font=theme.FONTS["h3"], bg=COLORS["surface"], fg=COLORS["text"]
        ).pack(anchor="w", pady=(0, 12))

        if not bills:
            EmptyState(
                table_card.body, "No bills on record yet", "Your electricity bills will appear here once generated."
            ).pack(fill="both", expand=True)
        else:
            table_wrap = tk.Frame(table_card.body, bg=COLORS["surface"])
            table_wrap.pack(fill="both", expand=True)

            table = ttk.Treeview(table_wrap, columns=BILLS_COLUMNS, show="headings", height=8)
            for col in BILLS_COLUMNS:
                table.heading(col, text=BILLS_HEADINGS[col])
                table.column(col, width=105, anchor="center")

            components.configure_row_tags(table)

            scrollbar = ttk.Scrollbar(table_wrap, orient=tk.VERTICAL, command=table.yview)
            table.configure(yscrollcommand=scrollbar.set)
            table.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            for i, bill in enumerate(bills):
                table.insert(
                    "", tk.END,
                    values=(
                        bill["bill_id"], bill["billing_month"], bill["previous_reading"], bill["current_reading"],
                        bill["units_consumed"], _currency(bill["total_amount"]), _currency(bill.get("late_fee", 0)),
                        bill["due_date"], bill["status"],
                    ),
                    tags=components.row_tags(i, bill.get("status")),
                )

            table.bind("<ButtonRelease-1>", self._select_bill)

        # ---- Make Payment panel ----
        pay_card = Card(section, radius=10, padding=18)
        pay_card.grid(row=0, column=1, sticky="nsew")

        tk.Label(
            pay_card.body, text="MAKE A PAYMENT", font=theme.FONTS["h3"], bg=COLORS["surface"], fg=COLORS["text"]
        ).pack(anchor="w")
        tk.Label(
            pay_card.body, text="Select an unpaid bill from the table, then confirm payment.",
            font=theme.FONTS["small"], bg=COLORS["surface"], fg=COLORS["text_muted"], wraplength=260, justify="left"
        ).pack(anchor="w", pady=(2, 12))

        self.pay_banner = InlineBanner(pay_card.body)
        self.pay_banner.pack_reserve()

        self.pay_selection_frame = tk.Frame(pay_card.body, bg=COLORS["surface_alt"])
        self.pay_selection_label = tk.Label(
            self.pay_selection_frame, text="No bill selected.", font=theme.FONTS["small"],
            bg=COLORS["surface_alt"], fg=COLORS["text_muted"], justify="left", anchor="w", padx=12, pady=10
        )
        self.pay_selection_label.pack(fill="x")
        self.pay_selection_frame.pack(fill="x", pady=(0, 12))

        theme.field_label(pay_card.body, "Payment Method").pack(anchor="w", pady=(0, 5))
        self.method_combo = theme.styled_combobox(pay_card.body, PAYMENT_METHODS, width=22)
        self.method_combo.set("UPI")
        self.method_combo.pack(anchor="w", fill="x", pady=(0, 12))

        theme.field_label(pay_card.body, "Transaction ID (optional)").pack(anchor="w", pady=(0, 5))
        self.transaction_entry = theme.styled_entry(pay_card.body, width=24)
        self.transaction_entry.pack(anchor="w", fill="x", pady=(0, 12))

        ttk.Button(pay_card.body, text="Make Payment", style="Primary.TButton", command=self._pay).pack(fill="x")

    def _select_bill(self, event):
        table = event.widget
        selected = table.focus()
        if not selected:
            return

        values = table.item(selected, "values")
        if not values:
            return

        bill_id = str(values[0])
        raw_bill = self._bills_by_id.get(bill_id)
        if raw_bill is None:
            return

        self.selected_bill = raw_bill
        self.pay_banner.hide()

        if (raw_bill.get("status") or "").upper() == "PAID":
            self.pay_selection_label.configure(
                text=f"Bill #{raw_bill['bill_id']} is already PAID.", fg=COLORS["text_muted"]
            )
        else:
            self.pay_selection_label.configure(
                text=f"Bill #{raw_bill['bill_id']}  \u00b7  {raw_bill['billing_month']}\n"
                     f"Amount Due: {_currency(raw_bill['total_amount'])}",
                fg=COLORS["text"],
            )

    def _pay(self):
        if not self.selected_bill:
            self.pay_banner.show("Select a bill from the table first.", kind="warning")
            return

        if (self.selected_bill.get("status") or "").upper() == "PAID":
            self.pay_banner.show("This bill has already been paid.", kind="warning")
            return

        success, message = make_payment(
            self.selected_bill["bill_id"],
            self.selected_bill.get("customer_name", ""),
            self.selected_bill["total_amount"],
            self.method_combo.get(),
            self.transaction_entry.get().strip(),
            customer_id=self.customer_id,
        )

        if success:
            self.transaction_entry.delete(0, tk.END)
            self.refresh()
        else:
            self.pay_banner.show(message, kind="danger")

    # -----------------------------------------------------------------
    def _build_grievances(self, row):
        section = tk.Frame(self.wrap, bg=COLORS["bg"])
        section.grid(row=row, column=0, sticky="ew")
        section.grid_columnconfigure(0, weight=1)
        section.grid_columnconfigure(1, weight=1)

        # ---- Submit new grievance ----
        submit_card = Card(section, radius=10, padding=18)
        submit_card.grid(row=0, column=0, sticky="nsew", padx=(0, 16))

        tk.Label(
            submit_card.body, text="SUBMIT A GRIEVANCE", font=theme.FONTS["h3"], bg=COLORS["surface"],
            fg=COLORS["text"]
        ).pack(anchor="w")
        tk.Label(
            submit_card.body, text="Report an incorrect bill, meter issue, payment issue or other concern.",
            font=theme.FONTS["small"], bg=COLORS["surface"], fg=COLORS["text_muted"], wraplength=280, justify="left"
        ).pack(anchor="w", pady=(2, 14))

        self.grievance_banner = InlineBanner(submit_card.body)
        self.grievance_banner.pack_reserve()

        theme.field_label(submit_card.body, "Category").pack(anchor="w", pady=(0, 5))
        self.category_combo = theme.styled_combobox(submit_card.body, VALID_CATEGORIES, width=24)
        self.category_combo.set(VALID_CATEGORIES[0])
        self.category_combo.pack(anchor="w", fill="x", pady=(0, 12))

        theme.field_label(submit_card.body, "Related Bill ID (optional)").pack(anchor="w", pady=(0, 5))
        self.related_bill_entry = theme.styled_entry(submit_card.body, width=24)
        self.related_bill_entry.pack(anchor="w", fill="x", pady=(0, 12))

        theme.field_label(submit_card.body, "Description").pack(anchor="w", pady=(0, 5))
        self.description_text = tk.Text(
            submit_card.body, height=4, font=theme.FONTS["body"], bg=COLORS["surface"], fg=COLORS["text"],
            relief="flat", highlightthickness=1, highlightbackground=COLORS["border_strong"],
            highlightcolor=COLORS["accent"], wrap="word"
        )
        self.description_text.pack(fill="x", pady=(0, 12))

        ttk.Button(
            submit_card.body, text="Submit Grievance", style="Primary.TButton", command=self._submit_grievance
        ).pack(fill="x")

        # ---- Own grievance history ----
        history_card = Card(section, radius=10, padding=18)
        history_card.grid(row=0, column=1, sticky="nsew")

        tk.Label(
            history_card.body, text="YOUR GRIEVANCES", font=theme.FONTS["h3"], bg=COLORS["surface"],
            fg=COLORS["text"]
        ).pack(anchor="w", pady=(0, 12))

        grievances = get_grievances_for_customer(self.customer_id) or []

        if not grievances:
            EmptyState(history_card.body, "No grievances submitted", "Anything you submit will show up here.").pack(
                fill="both", expand=True
            )
            return

        table_wrap = tk.Frame(history_card.body, bg=COLORS["surface"])
        table_wrap.pack(fill="both", expand=True)

        table = ttk.Treeview(table_wrap, columns=GRIEVANCE_COLUMNS, show="headings", height=6)
        for col in GRIEVANCE_COLUMNS:
            table.heading(col, text=GRIEVANCE_HEADINGS[col])
            table.column(col, width=110, anchor="center")

        components.configure_row_tags(table)

        scrollbar = ttk.Scrollbar(table_wrap, orient=tk.VERTICAL, command=table.yview)
        table.configure(yscrollcommand=scrollbar.set)
        table.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for i, g in enumerate(grievances):
            table.insert(
                "", tk.END,
                values=(
                    g["grievance_id"], g["category"], g.get("related_bill_id") or "\u2014",
                    g["status"], str(g.get("submitted_at") or ""),
                ),
                tags=components.row_tags(i, g.get("status")),
            )

    def _submit_grievance(self):
        description = self.description_text.get("1.0", tk.END).strip()
        related_bill = self.related_bill_entry.get().strip() or None

        if related_bill is not None and str(related_bill) not in self._bills_by_id:
            self.grievance_banner.show("That bill ID doesn't belong to your account.", kind="warning")
            return

        success, message = submit_grievance(
            self.customer_id, self.category_combo.get(), description, related_bill
        )

        if success:
            self.related_bill_entry.delete(0, tk.END)
            self.description_text.delete("1.0", tk.END)
            self.refresh()
        else:
            self.grievance_banner.show(message, kind="danger")
