"""
Bill Management page (embedded in the admin shell content area).

Still calls the exact same service functions with the exact same arguments:
    get_all_bills, get_customer_meter_details, get_last_bill_reading, generate_bill
from services/bill_service.py.

The "Calculated Charges" preview panel uses services.bill_service.calculate_energy_charge
(an existing, already-public service function) purely to *display* a live
preview before the bill is committed -- it does not duplicate or change the
authoritative calculation, which still happens inside generate_bill() exactly
as before.
"""

import tkinter as tk
from tkinter import ttk, messagebox

from ui import theme
from ui.theme import COLORS
from ui import components
from ui.components import Card, PageHeader, InlineBanner, SearchBar, EmptyState

from services.bill_service import (
    get_all_bills,
    get_customer_meter_details,
    get_last_bill_reading,
    generate_bill,
    calculate_energy_charge,
)
from services.tariff_service import get_all_tariffs
from datetime import date as _date


TABLE_COLUMNS = (
    "bill_id", "customer_id", "customer_name", "billing_month",
    "units_consumed", "total_amount", "due_date", "status",
)

TABLE_HEADINGS = {
    "bill_id": "Bill ID",
    "customer_id": "Cust. ID",
    "customer_name": "Customer",
    "billing_month": "Billing Month",
    "units_consumed": "Units",
    "total_amount": "Total Amount",
    "due_date": "Due Date",
    "status": "Status",
}

STATUS_FILTERS = ["ALL", "PAID", "UNPAID", "OVERDUE"]


def _currency(value):
    try:
        return f"\u20b9{float(value):,.2f}"
    except (TypeError, ValueError):
        return "\u20b90.00"


class BillManagementPage(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["bg"])

        self.customer_data = None
        self.all_bills = []
        self.status_filter = "ALL"
        self.search_query = ""

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        container = tk.Frame(self, bg=COLORS["bg"])
        container.grid(row=0, column=0, sticky="nsew", padx=28, pady=22)
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(3, weight=1)

        PageHeader(
            container,
            "Bill Management",
            "Load a customer's meter, enter the current reading, and generate a bill."
        ).grid(row=0, column=0, sticky="ew", pady=(0, 14))

        self.banner = InlineBanner(container)
        self.banner.place_in_grid(row=1, column=0)

        top_row = tk.Frame(container, bg=COLORS["bg"])
        top_row.grid(row=2, column=0, sticky="ew", pady=(0, 16))
        top_row.grid_columnconfigure(0, weight=3)
        top_row.grid_columnconfigure(1, weight=2)

        self._build_input_card(top_row)
        self._build_calculated_card(top_row)

        self._build_table(container, row=3)

        self.load_bills()

    # =================================================================
    # INPUT CARD (customer + readings — "input information")
    # =================================================================

    def _build_input_card(self, parent):
        card = Card(parent, radius=10, padding=18)
        card.grid(row=0, column=0, sticky="nsew", padx=(0, 16))

        tk.Label(
            card.body, text="BILL INPUT", font=theme.FONTS["h3"],
            bg=COLORS["surface"], fg=COLORS["text"]
        ).pack(anchor="w")
        tk.Label(
            card.body, text="Load the customer's meter, then enter the current reading.",
            font=theme.FONTS["small"], bg=COLORS["surface"], fg=COLORS["text_muted"]
        ).pack(anchor="w", pady=(2, 14))

        load_row = tk.Frame(card.body, bg=COLORS["surface"])
        load_row.pack(fill="x", pady=(0, 12))

        id_cell = tk.Frame(load_row, bg=COLORS["surface"])
        id_cell.pack(side="left", fill="x", expand=True, padx=(0, 10))
        theme.field_label(id_cell, "Customer ID").pack(anchor="w", pady=(0, 5))
        self.customer_id_entry = theme.styled_entry(id_cell, width=16)
        self.customer_id_entry.pack(anchor="w", fill="x")

        ttk.Button(
            load_row, text="Load Customer", style="Secondary.TButton", command=self.load_customer
        ).pack(side="left", anchor="s")

        self.customer_info_frame = tk.Frame(card.body, bg=COLORS["surface_alt"])
        self.customer_info_label = tk.Label(
            self.customer_info_frame, text="No customer loaded yet.", font=theme.FONTS["small"],
            bg=COLORS["surface_alt"], fg=COLORS["text_muted"], justify="left", anchor="w", padx=12, pady=10
        )
        self.customer_info_label.pack(fill="x")
        self.customer_info_frame.pack(fill="x", pady=(0, 14))

        grid = tk.Frame(card.body, bg=COLORS["surface"])
        grid.pack(fill="x")
        grid.grid_columnconfigure(0, weight=1)
        grid.grid_columnconfigure(1, weight=1)

        self.billing_month_entry = components.form_field(
            grid, 0, 0, "Billing Month (YYYY-MM-DD)", lambda p: theme.styled_entry(p, width=17)
        )
        self.previous_entry = components.form_field(
            grid, 0, 1, "Previous Reading", lambda p: theme.styled_entry(p, width=17), padx=(0, 0)
        )
        self.current_entry = components.form_field(
            grid, 1, 0, "Current Reading", lambda p: theme.styled_entry(p, width=17)
        )

        button_row = tk.Frame(card.body, bg=COLORS["surface"])
        button_row.pack(fill="x", pady=(8, 0))
        ttk.Button(
            button_row, text="Preview Charges", style="Secondary.TButton", command=self.preview_charges
        ).pack(side="left", fill="x", expand=True, padx=(0, 6))
        ttk.Button(
            button_row, text="Generate Bill", style="Primary.TButton", command=self.create_bill
        ).pack(side="left", fill="x", expand=True)

    # =================================================================
    # CALCULATED CARD ("calculated billing information")
    # =================================================================

    def _build_calculated_card(self, parent):
        card = Card(parent, radius=10, padding=18)
        card.grid(row=0, column=1, sticky="nsew")

        tk.Label(
            card.body, text="CALCULATED CHARGES", font=theme.FONTS["h3"],
            bg=COLORS["surface"], fg=COLORS["text"]
        ).pack(anchor="w")
        tk.Label(
            card.body, text="Based on the active tariff slabs for this connection type.",
            font=theme.FONTS["small"], bg=COLORS["surface"], fg=COLORS["text_muted"]
        ).pack(anchor="w", pady=(2, 14))

        self.calc_rows = {}
        for key, label in (
            ("units", "Units Consumed"),
            ("energy", "Energy Charge"),
            ("tax", "Tax (5%)"),
            ("total", "Total Amount"),
        ):
            row = tk.Frame(card.body, bg=COLORS["surface"])
            row.pack(fill="x", pady=6)
            tk.Label(
                row, text=label, font=theme.FONTS["body"], bg=COLORS["surface"], fg=COLORS["text_muted"]
            ).pack(side="left")
            value_font = theme.FONTS["mono_value"] if key == "total" else theme.FONTS["body_bold"]
            value_color = COLORS["accent_dark"] if key == "total" else COLORS["text"]
            value_label = tk.Label(row, text="\u2014", font=value_font, bg=COLORS["surface"], fg=value_color)
            value_label.pack(side="right")
            self.calc_rows[key] = value_label

        tk.Frame(card.body, bg=COLORS["border"], height=1).pack(fill="x", pady=(10, 10))
        tk.Label(
            card.body,
            text="Preview reflects the current form values and is recalculated using the same "
                 "slab rates the system applies when the bill is generated.",
            font=theme.FONTS["small"], bg=COLORS["surface"], fg=COLORS["text_faint"],
            wraplength=260, justify="left"
        ).pack(anchor="w")

    # =================================================================
    # TABLE
    # =================================================================

    def _build_table(self, parent, row):
        card = Card(parent, radius=10, padding=18)
        card.grid(row=row, column=0, sticky="nsew")
        card.body.grid_columnconfigure(0, weight=1)
        card.body.grid_rowconfigure(2, weight=1)

        header_row = tk.Frame(card.body, bg=COLORS["surface"])
        header_row.grid(row=0, column=0, sticky="ew")
        header_row.grid_columnconfigure(0, weight=1)

        self.count_label = tk.Label(
            header_row, text="", font=theme.FONTS["h3"], bg=COLORS["surface"], fg=COLORS["text"]
        )
        self.count_label.grid(row=0, column=0, sticky="w")

        filter_frame = tk.Frame(header_row, bg=COLORS["surface"])
        filter_frame.grid(row=0, column=1, sticky="e")

        self.status_combo = theme.styled_combobox(filter_frame, STATUS_FILTERS, width=10)
        self.status_combo.set("ALL")
        self.status_combo.pack(side="left", padx=(0, 10))
        self.status_combo.bind("<<ComboboxSelected>>", self._on_filter_change)

        self.search_bar = SearchBar(filter_frame, placeholder="Search by customer name", on_change=self._on_search)
        self.search_bar.pack(side="left")

        tk.Frame(card.body, bg=COLORS["surface"], height=12).grid(row=1, column=0)

        table_wrap = tk.Frame(card.body, bg=COLORS["surface"])
        table_wrap.grid(row=2, column=0, sticky="nsew")
        table_wrap.grid_columnconfigure(0, weight=1)
        table_wrap.grid_rowconfigure(0, weight=1)

        self.table = ttk.Treeview(table_wrap, columns=TABLE_COLUMNS, show="headings")
        for col in TABLE_COLUMNS:
            self.table.heading(col, text=TABLE_HEADINGS[col])
            self.table.column(col, width=125, anchor="center")
        self.table.column("customer_name", width=160, anchor="w")

        components.configure_row_tags(self.table)

        scrollbar = ttk.Scrollbar(table_wrap, orient=tk.VERTICAL, command=self.table.yview)
        self.table.configure(yscrollcommand=scrollbar.set)

        self.table.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.empty_state_holder = tk.Frame(table_wrap, bg=COLORS["surface"])
        self.empty_state_holder.grid(row=0, column=0, sticky="nsew")
        self.empty_state_holder.grid_remove()

    # =================================================================
    # DATA LOADING / FILTERING
    # =================================================================

    def load_bills(self):
        self.all_bills = get_all_bills() or []
        self._apply_filters()

    def _on_filter_change(self, _event=None):
        self.status_filter = self.status_combo.get()
        self._apply_filters()

    def _on_search(self, query):
        self.search_query = query
        self._apply_filters()

    def _apply_filters(self):
        bills = self.all_bills

        if self.status_filter and self.status_filter != "ALL":
            bills = [b for b in bills if (b.get("status") or "").upper() == self.status_filter]

        if self.search_query:
            q = self.search_query.lower()
            bills = [b for b in bills if q in str(b.get("customer_name", "")).lower()]

        self._render_rows(bills)

    def _render_rows(self, bills):
        for item in self.table.get_children():
            self.table.delete(item)

        self.count_label.configure(text=f"{len(bills)} Bill{'s' if len(bills) != 1 else ''}")

        if not bills:
            self.table.grid_remove()
            self.empty_state_holder.grid()
            for w in self.empty_state_holder.winfo_children():
                w.destroy()
            EmptyState(
                self.empty_state_holder, "No bills match this view",
                "Adjust the filters, or generate a new bill using the form above."
            ).pack(fill="both", expand=True)
            return

        self.empty_state_holder.grid_remove()
        self.table.grid()

        for i, bill in enumerate(bills):
            self.table.insert(
                "", tk.END,
                values=(
                    bill["bill_id"],
                    bill["customer_id"],
                    bill["customer_name"],
                    bill["billing_month"],
                    bill["units_consumed"],
                    _currency(bill["total_amount"]),
                    bill["due_date"],
                    bill["status"],
                ),
                tags=components.row_tags(i, bill.get("status")),
            )

    # =================================================================
    # LOAD CUSTOMER
    # =================================================================

    def load_customer(self):
        customer_id = self.customer_id_entry.get().strip()

        if not customer_id:
            self.banner.show("Enter a Customer ID to load.", kind="warning")
            return

        self.customer_data = get_customer_meter_details(customer_id)

        if not self.customer_data:
            self.customer_data = None
            self.customer_info_label.configure(text="No customer loaded yet.")
            self.banner.show("Customer or meter not found for that ID.", kind="danger")
            return

        previous_reading = get_last_bill_reading(customer_id)
        self.previous_entry.delete(0, tk.END)
        self.previous_entry.insert(0, previous_reading)

        data = self.customer_data
        name = f'{data.get("first_name", "")} {data.get("last_name", "")}'.strip()
        info_text = (
            f'{name}   \u00b7   {data.get("connection_type", "")}\n'
            f'Meter {data.get("meter_number", "")}   \u00b7   {data.get("email", "")}'
        )
        self.customer_info_label.configure(text=info_text, fg=COLORS["text"])
        self.banner.show("Customer and meter details loaded.", kind="success")

    # =================================================================
    # PREVIEW CHARGES (display-only, uses the existing calculate_energy_charge)
    # =================================================================

    def preview_charges(self):
        if not self.customer_data:
            self.banner.show("Load a customer first.", kind="warning")
            return

        previous = self.previous_entry.get().strip()
        current = self.current_entry.get().strip()

        if not previous or not current:
            self.banner.show("Enter both previous and current readings to preview charges.", kind="warning")
            return

        try:
            previous_val = float(previous)
            current_val = float(current)
        except ValueError:
            self.banner.show("Readings must be numeric.", kind="warning")
            return

        if current_val < previous_val:
            self.banner.show("Current reading cannot be less than previous reading.", kind="warning")
            return

        units_consumed = current_val - previous_val
        energy_charge = calculate_energy_charge(self.customer_data.get("connection_type", "DOMESTIC"), units_consumed)
        tax = round(energy_charge * 0.05, 2)
        total = round(energy_charge + tax, 2)

        self.calc_rows["units"].configure(text=f"{units_consumed:g}")
        self.calc_rows["energy"].configure(text=_currency(energy_charge))
        self.calc_rows["tax"].configure(text=_currency(tax))
        self.calc_rows["total"].configure(text=_currency(total))
        self.banner.hide()

    # =================================================================
    # GENERATE BILL
    # =================================================================

    def create_bill(self):
        if not self.customer_data:
            self.banner.show("Load a customer first.", kind="warning")
            return

        billing_month = self.billing_month_entry.get().strip()
        previous = self.previous_entry.get().strip()
        current = self.current_entry.get().strip()

        if not billing_month or not previous or not current:
            self.banner.show("Fill in billing month, previous reading and current reading.", kind="warning")
            return

        try:
            _date.fromisoformat(billing_month)
        except ValueError:
            self.banner.show("Billing month must be a valid date in YYYY-MM-DD format.", kind="warning")
            return

        data = self.customer_data

        connection_type = data.get("connection_type", "DOMESTIC")
        tariffs_for_type = [t for t in (get_all_tariffs() or []) if t.get("connection_type") == connection_type]
        if not tariffs_for_type:
            self.banner.show(
                f"No tariff slabs are configured for {connection_type} connections. "
                f"Add one under Tariff Management before generating this bill.",
                kind="danger",
            )
            return

        try:
            success, result = generate_bill(
                data["customer_id"],
                f'{data.get("first_name", "")} {data.get("last_name", "")}'.strip(),
                data.get("email", ""),
                data.get("phone", ""),
                data.get("address", ""),
                data.get("connection_type", "DOMESTIC"),
                data.get("meter_number", ""),
                billing_month,
                previous,
                current,
            )

            if success:
                self.banner.show(f"Bill generated successfully. Total amount: {_currency(result)}", kind="success")
                self.current_entry.delete(0, tk.END)
                self.billing_month_entry.delete(0, tk.END)
                self.load_bills()
            else:
                self.banner.show(str(result), kind="danger")

        except Exception as e:
            self.banner.show(str(e), kind="danger")
