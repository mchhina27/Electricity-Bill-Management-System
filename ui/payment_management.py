"""
Payment Management page (embedded in the admin shell content area).

Still calls the exact same service functions with the exact same arguments:
    get_unpaid_bills, make_payment
from services/payment_service.py.
"""

import tkinter as tk
from tkinter import ttk

from ui import theme
from ui.theme import COLORS
from ui import components
from ui.components import Card, PageHeader, InlineBanner, EmptyState

from services.payment_service import get_unpaid_bills, make_payment


TABLE_COLUMNS = ("bill_id", "customer_name", "billing_month", "total_amount", "due_date")
TABLE_HEADINGS = {
    "bill_id": "Bill ID",
    "customer_name": "Customer",
    "billing_month": "Billing Month",
    "total_amount": "Amount Due",
    "due_date": "Due Date",
}

PAYMENT_METHODS = ["CASH", "CARD", "UPI", "NET_BANKING"]


def _currency(value):
    try:
        return f"\u20b9{float(value):,.2f}"
    except (TypeError, ValueError):
        return "\u20b90.00"


class PaymentManagementPage(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["bg"])

        self.selected_bill = None
        self._bills_by_id = {}

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        container = tk.Frame(self, bg=COLORS["bg"])
        container.grid(row=0, column=0, sticky="nsew", padx=28, pady=22)
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(2, weight=1)

        PageHeader(
            container,
            "Payment Management",
            "Select an unpaid bill and record a payment against it."
        ).grid(row=0, column=0, sticky="ew", pady=(0, 14))

        self.banner = InlineBanner(container)
        self.banner.place_in_grid(row=1, column=0)

        body = tk.Frame(container, bg=COLORS["bg"])
        body.grid(row=2, column=0, sticky="nsew")
        body.grid_columnconfigure(0, weight=2)
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(0, weight=1)

        self._build_table(body)
        self._build_payment_form(body)

        self.load_unpaid_bills()

    # =================================================================
    # TABLE OF UNPAID BILLS
    # =================================================================

    def _build_table(self, parent):
        card = Card(parent, radius=10, padding=18)
        card.grid(row=0, column=0, sticky="nsew", padx=(0, 16))
        card.body.grid_columnconfigure(0, weight=1)
        card.body.grid_rowconfigure(1, weight=1)

        header_row = tk.Frame(card.body, bg=COLORS["surface"])
        header_row.grid(row=0, column=0, sticky="ew")
        header_row.grid_columnconfigure(0, weight=1)

        self.count_label = tk.Label(
            header_row, text="", font=theme.FONTS["h3"], bg=COLORS["surface"], fg=COLORS["text"]
        )
        self.count_label.grid(row=0, column=0, sticky="w")

        ttk.Button(
            header_row, text="Refresh", style="GhostOnSurface.TButton", command=self.load_unpaid_bills
        ).grid(row=0, column=1, sticky="e")

        tk.Frame(card.body, bg=COLORS["surface"], height=12).grid(row=1, column=0)
        table_wrap = tk.Frame(card.body, bg=COLORS["surface"])
        table_wrap.grid(row=2, column=0, sticky="nsew")
        card.body.grid_rowconfigure(2, weight=1)
        table_wrap.grid_columnconfigure(0, weight=1)
        table_wrap.grid_rowconfigure(0, weight=1)

        self.bill_table = ttk.Treeview(table_wrap, columns=TABLE_COLUMNS, show="headings")
        for col in TABLE_COLUMNS:
            self.bill_table.heading(col, text=TABLE_HEADINGS[col])
            self.bill_table.column(col, width=140, anchor="center")
        self.bill_table.column("customer_name", width=170, anchor="w")

        components.configure_row_tags(self.bill_table)

        scrollbar = ttk.Scrollbar(table_wrap, orient=tk.VERTICAL, command=self.bill_table.yview)
        self.bill_table.configure(yscrollcommand=scrollbar.set)

        self.bill_table.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.bill_table.bind("<ButtonRelease-1>", self.select_bill)

        self.empty_state_holder = tk.Frame(table_wrap, bg=COLORS["surface"])
        self.empty_state_holder.grid(row=0, column=0, sticky="nsew")
        self.empty_state_holder.grid_remove()

    # =================================================================
    # PAYMENT FORM
    # =================================================================

    def _build_payment_form(self, parent):
        card = Card(parent, radius=10, padding=18)
        card.grid(row=0, column=1, sticky="nsew")

        tk.Label(
            card.body, text="RECORD PAYMENT", font=theme.FONTS["h3"],
            bg=COLORS["surface"], fg=COLORS["text"]
        ).pack(anchor="w")
        tk.Label(
            card.body, text="Select a bill from the list, then confirm the payment details.",
            font=theme.FONTS["small"], bg=COLORS["surface"], fg=COLORS["text_muted"], wraplength=280, justify="left"
        ).pack(anchor="w", pady=(2, 14))

        self.selection_frame = tk.Frame(card.body, bg=COLORS["surface_alt"])
        self.selection_label = tk.Label(
            self.selection_frame, text="No bill selected.", font=theme.FONTS["small"],
            bg=COLORS["surface_alt"], fg=COLORS["text_muted"], justify="left", anchor="w", padx=12, pady=10
        )
        self.selection_label.pack(fill="x")
        self.selection_frame.pack(fill="x", pady=(0, 14))

        grid = tk.Frame(card.body, bg=COLORS["surface"])
        grid.pack(fill="x")
        grid.grid_columnconfigure(0, weight=1)

        self.method_combo = components.form_field(
            grid, 0, 0, "Payment Method", lambda p: theme.styled_combobox(p, PAYMENT_METHODS, width=22)
        )
        self.method_combo.set("CASH")

        self.transaction_entry = components.form_field(
            grid, 1, 0, "Transaction ID (optional)", lambda p: theme.styled_entry(p, width=24)
        )

        ttk.Button(
            card.body, text="Make Payment", style="Primary.TButton", command=self.pay
        ).pack(fill="x", pady=(10, 0))

    # =================================================================
    # DATA
    # =================================================================

    def load_unpaid_bills(self):
        self.selected_bill = None
        self.selection_label.configure(text="No bill selected.")

        for item in self.bill_table.get_children():
            self.bill_table.delete(item)

        bills = get_unpaid_bills() or []
        self._bills_by_id = {str(b["bill_id"]): b for b in bills}
        self.count_label.configure(text=f"{len(bills)} Unpaid Bill{'s' if len(bills) != 1 else ''}")

        if not bills:
            self.bill_table.grid_remove()
            self.empty_state_holder.grid()
            for w in self.empty_state_holder.winfo_children():
                w.destroy()
            EmptyState(
                self.empty_state_holder, "No outstanding bills",
                "All generated bills are currently paid."
            ).pack(fill="both", expand=True)
            return

        self.empty_state_holder.grid_remove()
        self.bill_table.grid()

        for i, bill in enumerate(bills):
            self.bill_table.insert(
                "", tk.END,
                values=(
                    bill["bill_id"],
                    bill["customer_name"],
                    bill["billing_month"],
                    _currency(bill["total_amount"]),
                    bill["due_date"],
                ),
                tags=components.row_tags(i, "UNPAID"),
            )

    def select_bill(self, _event):
        selected = self.bill_table.focus()
        if not selected:
            return

        values = self.bill_table.item(selected, "values")
        if not values:
            return

        bill_id = str(values[0])
        raw_bill = self._bills_by_id.get(bill_id)
        if raw_bill is None:
            return

        # Keep the raw (unformatted) amount for the actual payment call --
        # `values` holds the display-formatted currency string, which must
        # never be passed into the database layer.
        self.selected_bill = {
            "bill_id": raw_bill["bill_id"],
            "customer_name": raw_bill["customer_name"],
            "total_amount": raw_bill["total_amount"],
        }
        self.banner.hide()
        self.selection_label.configure(
            text=f"Bill #{raw_bill['bill_id']}  \u00b7  {raw_bill['customer_name']}\n"
                 f"Amount Due: {_currency(raw_bill['total_amount'])}",
            fg=COLORS["text"],
        )

    # =================================================================
    # PAY
    # =================================================================

    def pay(self):
        if not self.selected_bill:
            self.banner.show("Select a bill from the list first.", kind="warning")
            return

        bill_id = self.selected_bill["bill_id"]
        customer_name = self.selected_bill["customer_name"]
        amount = self.selected_bill["total_amount"]

        success, message = make_payment(
            bill_id,
            customer_name,
            amount,
            self.method_combo.get(),
            self.transaction_entry.get().strip(),
        )

        if success:
            self.banner.show(message, kind="success")
            self.selected_bill = None
            self.selection_label.configure(text="No bill selected.")
            self.transaction_entry.delete(0, tk.END)
            self.load_unpaid_bills()
        else:
            self.banner.show(message, kind="danger")
