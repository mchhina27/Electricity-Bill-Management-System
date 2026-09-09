"""
Meter Management page (embedded in the admin shell content area).

Still calls the exact same service functions with the exact same arguments:
    get_all_meters, add_meter, update_meter, delete_meter
from services/meter_service.py.
"""

import tkinter as tk
from tkinter import ttk, messagebox

from ui import theme
from ui.theme import COLORS
from ui import components
from ui.components import Card, PageHeader, InlineBanner, SearchBar, EmptyState

from services.meter_service import (
    get_all_meters,
    add_meter,
    update_meter,
    delete_meter,
)


METER_TYPES = ["SINGLE_PHASE", "THREE_PHASE"]
METER_STATUSES = ["ACTIVE", "INACTIVE", "FAULTY"]

TABLE_COLUMNS = (
    "meter_id",
    "customer_id",
    "meter_number",
    "meter_type",
    "installation_date",
    "initial_reading",
    "current_reading",
    "meter_status",
)

TABLE_HEADINGS = {
    "meter_id": "Meter ID",
    "customer_id": "Customer ID",
    "meter_number": "Meter Number",
    "meter_type": "Meter Type",
    "installation_date": "Installed",
    "initial_reading": "Initial Reading",
    "current_reading": "Current Reading",
    "meter_status": "Status",
}


class MeterManagementPage(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["bg"])

        self.selected_meter_id = None
        self.all_meters = []

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        container = tk.Frame(self, bg=COLORS["bg"])
        container.grid(row=0, column=0, sticky="nsew", padx=28, pady=22)
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(2, weight=1)

        PageHeader(
            container,
            "Meter Management",
            "Register meters, update readings and track device status."
        ).grid(row=0, column=0, sticky="ew", pady=(0, 14))

        self.banner = InlineBanner(container)
        self.banner.place_in_grid(row=1, column=0)

        body = tk.Frame(container, bg=COLORS["bg"])
        body.grid(row=2, column=0, sticky="nsew")
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(0, weight=1)

        self._build_form(body)
        self._build_table(body)

        self.load_meters()

    # =================================================================
    # FORM PANEL
    # =================================================================

    def _build_form(self, parent):
        card = Card(parent, radius=10, padding=18)
        card.grid(row=0, column=0, sticky="ns", padx=(0, 16))

        tk.Label(
            card.body, text="METER DETAILS", font=theme.FONTS["h3"],
            bg=COLORS["surface"], fg=COLORS["text"]
        ).pack(anchor="w")
        tk.Label(
            card.body, text="Select a row to edit, or fill this in to register a new meter.",
            font=theme.FONTS["small"], bg=COLORS["surface"], fg=COLORS["text_muted"], wraplength=300, justify="left"
        ).pack(anchor="w", pady=(2, 14))

        grid = tk.Frame(card.body, bg=COLORS["surface"])
        grid.pack(fill="x")
        grid.grid_columnconfigure(0, weight=1)
        grid.grid_columnconfigure(1, weight=1)

        self.customer_id_entry = components.form_field(
            grid, 0, 0, "Customer ID", lambda p: theme.styled_entry(p, width=18)
        )
        self.meter_number_entry = components.form_field(
            grid, 0, 1, "Meter Number", lambda p: theme.styled_entry(p, width=18), padx=(0, 0)
        )
        self.meter_type_combo = components.form_field(
            grid, 1, 0, "Meter Type", lambda p: theme.styled_combobox(p, METER_TYPES, width=15)
        )
        self.meter_type_combo.set("SINGLE_PHASE")

        self.installation_date_entry = components.form_field(
            grid, 1, 1, "Installation Date (YYYY-MM-DD)", lambda p: theme.styled_entry(p, width=18), padx=(0, 0)
        )
        self.initial_reading_entry = components.form_field(
            grid, 2, 0, "Initial Reading", lambda p: theme.styled_entry(p, width=18)
        )
        self.current_reading_entry = components.form_field(
            grid, 2, 1, "Current Reading", lambda p: theme.styled_entry(p, width=18), padx=(0, 0)
        )
        self.meter_status_combo = components.form_field(
            grid, 3, 0, "Meter Status", lambda p: theme.styled_combobox(p, METER_STATUSES, width=15)
        )
        self.meter_status_combo.set("ACTIVE")

        button_row1 = tk.Frame(card.body, bg=COLORS["surface"])
        button_row1.pack(fill="x", pady=(10, 6))
        ttk.Button(
            button_row1, text="Add Meter", style="Primary.TButton", command=self.add_meter
        ).pack(side="left", fill="x", expand=True, padx=(0, 6))
        ttk.Button(
            button_row1, text="Update", style="Secondary.TButton", command=self.update_meter
        ).pack(side="left", fill="x", expand=True)

        button_row2 = tk.Frame(card.body, bg=COLORS["surface"])
        button_row2.pack(fill="x")
        ttk.Button(
            button_row2, text="Delete", style="Destructive.TButton", command=self.delete_meter
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

        self.search_bar = SearchBar(
            header_row, placeholder="Search by meter number or customer ID", on_change=self._on_search
        )
        self.search_bar.grid(row=0, column=1, sticky="e")

        tk.Frame(card.body, bg=COLORS["surface"], height=12).grid(row=1, column=0)

        table_wrap = tk.Frame(card.body, bg=COLORS["surface"])
        table_wrap.grid(row=2, column=0, sticky="nsew")
        table_wrap.grid_columnconfigure(0, weight=1)
        table_wrap.grid_rowconfigure(0, weight=1)

        self.meter_table = ttk.Treeview(table_wrap, columns=TABLE_COLUMNS, show="headings")
        for col in TABLE_COLUMNS:
            self.meter_table.heading(col, text=TABLE_HEADINGS[col])
            self.meter_table.column(col, width=120, anchor="center")

        components.configure_row_tags(self.meter_table)

        scrollbar = ttk.Scrollbar(table_wrap, orient=tk.VERTICAL, command=self.meter_table.yview)
        self.meter_table.configure(yscrollcommand=scrollbar.set)

        self.meter_table.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.meter_table.bind("<ButtonRelease-1>", self.select_meter)

        self.empty_state_holder = tk.Frame(table_wrap, bg=COLORS["surface"])
        self.empty_state_holder.grid(row=0, column=0, sticky="nsew")
        self.empty_state_holder.grid_remove()

    # =================================================================
    # DATA LOADING / FILTERING
    # =================================================================

    def load_meters(self):
        self.all_meters = get_all_meters() or []
        self._render_rows(self.all_meters)

    def _on_search(self, query):
        if not query:
            self._render_rows(self.all_meters)
            return

        query = query.lower()
        filtered = [
            m for m in self.all_meters
            if query in str(m.get("meter_number", "")).lower()
            or query in str(m.get("customer_id", "")).lower()
        ]
        self._render_rows(filtered)

    def _render_rows(self, meters):
        for item in self.meter_table.get_children():
            self.meter_table.delete(item)

        self.count_label.configure(text=f"{len(meters)} Meter{'s' if len(meters) != 1 else ''}")

        if not meters:
            self.meter_table.grid_remove()
            self.empty_state_holder.grid()
            for w in self.empty_state_holder.winfo_children():
                w.destroy()
            EmptyState(
                self.empty_state_holder, "No meters found",
                "Try a different search, or register a new meter using the form."
            ).pack(fill="both", expand=True)
            return

        self.empty_state_holder.grid_remove()
        self.meter_table.grid()

        for i, meter in enumerate(meters):
            self.meter_table.insert(
                "", tk.END,
                values=(
                    meter["meter_id"],
                    meter["customer_id"],
                    meter["meter_number"],
                    meter["meter_type"],
                    meter["installation_date"],
                    meter["initial_reading"],
                    meter["current_reading"],
                    meter["meter_status"],
                ),
                tags=components.row_tags(i, meter.get("meter_status")),
            )

    # =================================================================
    # SELECT
    # =================================================================

    def select_meter(self, _event):
        selected = self.meter_table.focus()
        if not selected:
            return

        values = self.meter_table.item(selected, "values")
        if not values:
            return

        self.selected_meter_id = values[0]
        self.banner.hide()

        self._set_entry(self.customer_id_entry, values[1])
        self._set_entry(self.meter_number_entry, values[2])
        self.meter_type_combo.set(values[3])
        self._set_entry(self.installation_date_entry, values[4])
        self._set_entry(self.initial_reading_entry, values[5])
        self._set_entry(self.current_reading_entry, values[6])
        self.meter_status_combo.set(values[7])

    @staticmethod
    def _set_entry(entry, value):
        entry.delete(0, tk.END)
        entry.insert(0, value)

    # =================================================================
    # VALIDATE
    # =================================================================

    def validate_form(self):
        required_fields = [
            self.customer_id_entry.get().strip(),
            self.meter_number_entry.get().strip(),
            self.installation_date_entry.get().strip(),
        ]

        if not all(required_fields):
            self.banner.show("Please fill in Customer ID, Meter Number and Installation Date.", kind="warning")
            return False

        try:
            int(self.customer_id_entry.get().strip())
        except ValueError:
            self.banner.show("Customer ID must be a number.", kind="warning")
            return False

        try:
            initial = float(self.initial_reading_entry.get().strip() or 0)
            current = float(self.current_reading_entry.get().strip() or 0)

            if initial < 0 or current < 0:
                self.banner.show("Meter readings cannot be negative.", kind="warning")
                return False

            if current < initial:
                self.banner.show("Current reading cannot be less than initial reading.", kind="warning")
                return False

        except ValueError:
            self.banner.show("Readings must be numeric values.", kind="warning")
            return False

        return True

    # =================================================================
    # ADD / UPDATE / DELETE
    # =================================================================

    def add_meter(self):
        if not self.validate_form():
            return

        success = add_meter(
            self.customer_id_entry.get().strip(),
            self.meter_number_entry.get().strip(),
            self.meter_type_combo.get(),
            self.installation_date_entry.get().strip(),
            self.initial_reading_entry.get().strip(),
            self.current_reading_entry.get().strip(),
            self.meter_status_combo.get(),
        )

        if success:
            self.banner.show("Meter added successfully.", kind="success")
            self.clear_form()
            self.load_meters()
        else:
            self.banner.show(
                "Could not add meter. Make sure the Customer ID exists, the customer doesn't "
                "already have a meter, and the meter number is unique.",
                kind="danger",
            )

    def update_meter(self):
        if self.selected_meter_id is None:
            self.banner.show("Select a meter from the table first.", kind="warning")
            return

        if not self.validate_form():
            return

        success = update_meter(
            self.selected_meter_id,
            self.customer_id_entry.get().strip(),
            self.meter_number_entry.get().strip(),
            self.meter_type_combo.get(),
            self.installation_date_entry.get().strip(),
            self.initial_reading_entry.get().strip(),
            self.current_reading_entry.get().strip(),
            self.meter_status_combo.get(),
        )

        if success:
            self.banner.show("Meter updated successfully.", kind="success")
            self.clear_form()
            self.load_meters()
        else:
            self.banner.show("Could not update meter.", kind="danger")

    def delete_meter(self):
        if self.selected_meter_id is None:
            self.banner.show("Select a meter from the table first.", kind="warning")
            return

        confirm = messagebox.askyesno(
            "Confirm Delete", "Are you sure you want to delete this meter? This cannot be undone."
        )
        if not confirm:
            return

        success = delete_meter(self.selected_meter_id)

        if success:
            self.banner.show("Meter deleted successfully.", kind="success")
            self.clear_form()
            self.load_meters()
        else:
            self.banner.show("Could not delete meter. It may be referenced by another table.", kind="danger")

    def clear_form(self):
        self.selected_meter_id = None
        self.banner.hide()

        for entry in (
            self.customer_id_entry, self.meter_number_entry, self.installation_date_entry,
            self.initial_reading_entry, self.current_reading_entry,
        ):
            entry.delete(0, tk.END)

        self.meter_type_combo.set("SINGLE_PHASE")
        self.meter_status_combo.set("ACTIVE")
