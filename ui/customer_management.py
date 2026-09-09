"""
Customer Management page (embedded in the admin shell content area).

All data access is unchanged from the original project -- this file only
changes how the screen looks and is composed. It still calls:
    get_all_customers, add_customer, update_customer, delete_customer
from services/customer_service.py with the exact same arguments/order.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

from ui import theme
from ui.theme import COLORS
from ui import components
from ui.components import Card, PageHeader, InlineBanner, SearchBar, EmptyState

from services.customer_service import (
    get_all_customers,
    add_customer,
    update_customer,
    delete_customer,
)


CONNECTION_TYPES = ["DOMESTIC", "COMMERCIAL", "INDUSTRIAL"]

TABLE_COLUMNS = (
    "customer_id",
    "first_name",
    "last_name",
    "email",
    "phone",
    "city",
    "state",
    "connection_type",
)

TABLE_HEADINGS = {
    "customer_id": "ID",
    "first_name": "First Name",
    "last_name": "Last Name",
    "email": "Email",
    "phone": "Phone",
    "city": "City",
    "state": "State",
    "connection_type": "Connection Type",
}


class CustomerManagementPage(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["bg"])

        self.selected_customer_id = None
        self.all_customers = []

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        container = tk.Frame(self, bg=COLORS["bg"])
        container.grid(row=0, column=0, sticky="nsew", padx=28, pady=22)
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(2, weight=1)

        PageHeader(
            container,
            "Customer Management",
            "Add, update and search registered customer accounts."
        ).grid(row=0, column=0, sticky="ew", pady=(0, 14))

        self.banner = InlineBanner(container)
        self.banner.place_in_grid(row=1, column=0)

        body = tk.Frame(container, bg=COLORS["bg"])
        body.grid(row=2, column=0, sticky="nsew")
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(0, weight=1)

        self._build_form(body)
        self._build_table(body)

        self.load_customers()

    # =================================================================
    # FORM PANEL
    # =================================================================

    def _build_form(self, parent):
        card = Card(parent, radius=10, padding=18)
        card.grid(row=0, column=0, sticky="ns", padx=(0, 16))

        tk.Label(
            card.body, text="CUSTOMER DETAILS", font=theme.FONTS["h3"],
            bg=COLORS["surface"], fg=COLORS["text"]
        ).pack(anchor="w")
        tk.Label(
            card.body, text="Select a row to edit, or fill this in to add a new customer.",
            font=theme.FONTS["small"], bg=COLORS["surface"], fg=COLORS["text_muted"], wraplength=300, justify="left"
        ).pack(anchor="w", pady=(2, 14))

        grid = tk.Frame(card.body, bg=COLORS["surface"])
        grid.pack(fill="x")
        grid.grid_columnconfigure(0, weight=1)
        grid.grid_columnconfigure(1, weight=1)

        self.first_name_entry = components.form_field(
            grid, 0, 0, "First Name", lambda p: theme.styled_entry(p, width=18)
        )
        self.last_name_entry = components.form_field(
            grid, 0, 1, "Last Name", lambda p: theme.styled_entry(p, width=18), padx=(0, 0)
        )
        self.email_entry = components.form_field(
            grid, 1, 0, "Email", lambda p: theme.styled_entry(p, width=18)
        )
        self.phone_entry = components.form_field(
            grid, 1, 1, "Phone", lambda p: theme.styled_entry(p, width=18), padx=(0, 0)
        )
        self.address_entry = components.form_field(
            grid, 2, 0, "Address", lambda p: theme.styled_entry(p, width=18)
        )
        self.city_entry = components.form_field(
            grid, 2, 1, "City", lambda p: theme.styled_entry(p, width=18), padx=(0, 0)
        )
        self.state_entry = components.form_field(
            grid, 3, 0, "State", lambda p: theme.styled_entry(p, width=18)
        )
        self.pincode_entry = components.form_field(
            grid, 3, 1, "Pincode", lambda p: theme.styled_entry(p, width=18), padx=(0, 0)
        )
        self.connection_date_entry = components.form_field(
            grid, 4, 0, "Connection Date (YYYY-MM-DD)", lambda p: theme.styled_entry(p, width=18)
        )
        self.connection_date_entry.insert(0, date.today().strftime("%Y-%m-%d"))

        self.connection_type_combo = components.form_field(
            grid, 4, 1, "Connection Type",
            lambda p: theme.styled_combobox(p, CONNECTION_TYPES, width=15), padx=(0, 0)
        )
        self.connection_type_combo.set("DOMESTIC")

        button_row1 = tk.Frame(card.body, bg=COLORS["surface"])
        button_row1.pack(fill="x", pady=(10, 6))
        ttk.Button(
            button_row1, text="Add Customer", style="Primary.TButton", command=self.add_customer
        ).pack(side="left", fill="x", expand=True, padx=(0, 6))
        ttk.Button(
            button_row1, text="Update", style="Secondary.TButton", command=self.update_customer
        ).pack(side="left", fill="x", expand=True)

        button_row2 = tk.Frame(card.body, bg=COLORS["surface"])
        button_row2.pack(fill="x")
        ttk.Button(
            button_row2, text="Delete", style="Destructive.TButton", command=self.delete_customer
        ).pack(side="left", fill="x", expand=True, padx=(0, 6))
        ttk.Button(
            button_row2, text="Clear Form", style="GhostOnSurface.TButton", command=self.clear_form
        ).pack(side="left", fill="x", expand=True)

    # =================================================================
    # TABLE PANEL
    # =================================================================

    def _build_table(self, parent):
        card = Card(parent, radius=10, padding=18)
        card.grid(row=0, column=1, sticky="nsew")
        card.body.grid_columnconfigure(0, weight=1)
        card.body.grid_rowconfigure(2, weight=1)

        header_row = tk.Frame(card.body, bg=COLORS["surface"])
        header_row.grid(row=0, column=0, sticky="ew")
        header_row.grid_columnconfigure(0, weight=1)

        self.count_label = tk.Label(
            header_row, text="", font=theme.FONTS["h3"], bg=COLORS["surface"], fg=COLORS["text"]
        )
        self.count_label.grid(row=0, column=0, sticky="w")

        self.search_bar = SearchBar(header_row, placeholder="Search by name, email, phone or city", on_change=self._on_search)
        self.search_bar.grid(row=0, column=1, sticky="e")

        tk.Frame(card.body, bg=COLORS["surface"], height=12).grid(row=1, column=0)

        table_wrap = tk.Frame(card.body, bg=COLORS["surface"])
        table_wrap.grid(row=2, column=0, sticky="nsew")
        table_wrap.grid_columnconfigure(0, weight=1)
        table_wrap.grid_rowconfigure(0, weight=1)

        self.customer_table = ttk.Treeview(table_wrap, columns=TABLE_COLUMNS, show="headings")
        for col in TABLE_COLUMNS:
            self.customer_table.heading(col, text=TABLE_HEADINGS[col])
            self.customer_table.column(col, width=120, anchor="center")
        self.customer_table.column("email", width=170, anchor="w")
        self.customer_table.column("first_name", anchor="w")
        self.customer_table.column("last_name", anchor="w")

        components.configure_row_tags(self.customer_table)

        scrollbar = ttk.Scrollbar(table_wrap, orient=tk.VERTICAL, command=self.customer_table.yview)
        self.customer_table.configure(yscrollcommand=scrollbar.set)

        self.customer_table.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.customer_table.bind("<ButtonRelease-1>", self.select_customer)

        self.empty_state_holder = tk.Frame(table_wrap, bg=COLORS["surface"])
        self.empty_state_holder.grid(row=0, column=0, sticky="nsew")
        self.empty_state_holder.grid_remove()

    # =================================================================
    # DATA LOADING / FILTERING
    # =================================================================

    def load_customers(self):
        self.all_customers = get_all_customers() or []
        self._render_rows(self.all_customers)

    def _on_search(self, query):
        if not query:
            self._render_rows(self.all_customers)
            return

        query = query.lower()
        filtered = [
            c for c in self.all_customers
            if query in str(c.get("first_name", "")).lower()
            or query in str(c.get("last_name", "")).lower()
            or query in str(c.get("email", "")).lower()
            or query in str(c.get("phone", "")).lower()
            or query in str(c.get("city", "")).lower()
        ]
        self._render_rows(filtered)

    def _render_rows(self, customers):
        for item in self.customer_table.get_children():
            self.customer_table.delete(item)

        self.count_label.configure(text=f"{len(customers)} Customer{'s' if len(customers) != 1 else ''}")

        if not customers:
            self.customer_table.grid_remove()
            self.empty_state_holder.grid()
            for w in self.empty_state_holder.winfo_children():
                w.destroy()
            EmptyState(
                self.empty_state_holder, "No customers found",
                "Try a different search, or add a new customer using the form."
            ).pack(fill="both", expand=True)
            return

        self.empty_state_holder.grid_remove()
        self.customer_table.grid()

        for i, customer in enumerate(customers):
            self.customer_table.insert(
                "", tk.END,
                values=(
                    customer.get("customer_id", ""),
                    customer.get("first_name", ""),
                    customer.get("last_name", ""),
                    customer.get("email", ""),
                    customer.get("phone", ""),
                    customer.get("city", ""),
                    customer.get("state", ""),
                    customer.get("connection_type", ""),
                ),
                tags=components.row_tags(i),
            )

    # =================================================================
    # SELECT / VALIDATE
    # =================================================================

    def select_customer(self, _event):
        selected = self.customer_table.focus()
        if not selected:
            return

        values = self.customer_table.item(selected, "values")
        if not values:
            return

        customer_id = values[0]
        customer = next(
            (c for c in self.all_customers if str(c["customer_id"]) == str(customer_id)), None
        )
        if customer is None:
            return

        self.selected_customer_id = customer["customer_id"]
        self.banner.hide()

        self._set_entry(self.first_name_entry, customer.get("first_name", ""))
        self._set_entry(self.last_name_entry, customer.get("last_name", ""))
        self._set_entry(self.email_entry, customer.get("email", ""))
        self._set_entry(self.phone_entry, customer.get("phone", ""))
        self._set_entry(self.address_entry, customer.get("address", ""))
        self._set_entry(self.city_entry, customer.get("city", ""))
        self._set_entry(self.state_entry, customer.get("state", ""))
        self._set_entry(self.pincode_entry, customer.get("pincode", ""))
        self._set_entry(self.connection_date_entry, str(customer.get("connection_date", "")))
        self.connection_type_combo.set(customer.get("connection_type", "DOMESTIC"))

    @staticmethod
    def _set_entry(entry, value):
        entry.delete(0, tk.END)
        entry.insert(0, value)

    def validate_form(self):
        fields = [
            self.first_name_entry.get().strip(),
            self.last_name_entry.get().strip(),
            self.email_entry.get().strip(),
            self.phone_entry.get().strip(),
            self.address_entry.get().strip(),
            self.city_entry.get().strip(),
            self.state_entry.get().strip(),
            self.connection_date_entry.get().strip(),
        ]

        if not all(fields):
            self.banner.show("Please fill in all required fields.", kind="warning")
            return False

        email = self.email_entry.get().strip()
        if "@" not in email or "." not in email:
            self.banner.show("Please enter a valid email address.", kind="warning")
            return False

        connection_date = self.connection_date_entry.get().strip()
        try:
            date.fromisoformat(connection_date)
        except ValueError:
            self.banner.show("Connection date must be in YYYY-MM-DD format.", kind="warning")
            return False

        return True

    # =================================================================
    # ADD / UPDATE / DELETE
    # =================================================================

    def add_customer(self):
        if not self.validate_form():
            return

        success, message = add_customer(
            self.first_name_entry.get().strip(),
            self.last_name_entry.get().strip(),
            self.email_entry.get().strip(),
            self.phone_entry.get().strip(),
            self.address_entry.get().strip(),
            self.city_entry.get().strip(),
            self.state_entry.get().strip(),
            self.pincode_entry.get().strip() or None,
            self.connection_date_entry.get().strip(),
            self.connection_type_combo.get().strip(),
        )

        if success:
            self.banner.show(message, kind="success")
            self.clear_form()
            self.load_customers()
        else:
            self.banner.show(message, kind="danger")

    def update_customer(self):
        if self.selected_customer_id is None:
            self.banner.show("Select a customer from the table first.", kind="warning")
            return

        if not self.validate_form():
            return

        success, message = update_customer(
            self.selected_customer_id,
            self.first_name_entry.get().strip(),
            self.last_name_entry.get().strip(),
            self.email_entry.get().strip(),
            self.phone_entry.get().strip(),
            self.address_entry.get().strip(),
            self.city_entry.get().strip(),
            self.state_entry.get().strip(),
            self.pincode_entry.get().strip() or None,
            self.connection_date_entry.get().strip(),
            self.connection_type_combo.get().strip(),
        )

        if success:
            self.banner.show(message, kind="success")
            self.clear_form()
            self.load_customers()
        else:
            self.banner.show(message, kind="danger")

    def delete_customer(self):
        if self.selected_customer_id is None:
            self.banner.show("Select a customer from the table first.", kind="warning")
            return

        confirm = messagebox.askyesno(
            "Confirm Delete", "Are you sure you want to delete this customer? This cannot be undone."
        )
        if not confirm:
            return

        success, message = delete_customer(self.selected_customer_id)

        if success:
            self.banner.show(message, kind="success")
            self.clear_form()
            self.load_customers()
        else:
            self.banner.show(message, kind="danger")

    def clear_form(self):
        self.selected_customer_id = None
        self.banner.hide()

        for entry in (
            self.first_name_entry, self.last_name_entry, self.email_entry, self.phone_entry,
            self.address_entry, self.city_entry, self.state_entry, self.pincode_entry,
            self.connection_date_entry,
        ):
            entry.delete(0, tk.END)

        self.connection_date_entry.insert(0, date.today().strftime("%Y-%m-%d"))
        self.connection_type_combo.set("DOMESTIC")
