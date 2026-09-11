"""
Tariff Management page (embedded in the admin shell content area).

Still calls the exact same service functions with the exact same arguments:
    get_all_tariffs, add_tariff, update_tariff, delete_tariff
from services/tariff_service.py.
"""

import tkinter as tk
from tkinter import ttk, messagebox

from ui import theme
from ui.theme import COLORS
from ui import components
from ui.components import Card, PageHeader, InlineBanner, EmptyState

from services.tariff_service import (
    get_all_tariffs,
    add_tariff,
    update_tariff,
    delete_tariff,
)


CONNECTION_TYPES = ["DOMESTIC", "COMMERCIAL", "INDUSTRIAL"]

TABLE_COLUMNS = ("tariff_id", "connection_type", "unit_range", "rate_per_unit")

TABLE_HEADINGS = {
    "tariff_id": "Tariff ID",
    "connection_type": "Connection Type",
    "unit_range": "Unit Range",
    "rate_per_unit": "Rate / Unit",
}

# Give each connection type its own accent so slabs are easy to scan at a glance.
CONNECTION_TYPE_KIND = {
    "DOMESTIC": "success",
    "COMMERCIAL": "accent",
    "INDUSTRIAL": "warning",
}


class TariffManagementPage(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["bg"])

        self.selected_tariff_id = None
        self.all_tariffs = []

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        container = tk.Frame(self, bg=COLORS["bg"])
        container.grid(row=0, column=0, sticky="nsew", padx=28, pady=22)
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(2, weight=1)

        PageHeader(
            container,
            "Tariff Management",
            "Configure slab-based per-unit rates for each connection type."
        ).grid(row=0, column=0, sticky="ew", pady=(0, 14))

        self.banner = InlineBanner(container)
        self.banner.place_in_grid(row=1, column=0)

        body = tk.Frame(container, bg=COLORS["bg"])
        body.grid(row=2, column=0, sticky="nsew")
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(0, weight=1)

        self._build_form(body)
        self._build_table(body)

        self.load_tariffs()

    # =================================================================
    # FORM PANEL
    # =================================================================

    def _build_form(self, parent):
        card = Card(parent, radius=10, padding=18)
        card.grid(row=0, column=0, sticky="ns", padx=(0, 16))

        tk.Label(
            card.body, text="TARIFF SLAB", font=theme.FONTS["h3"],
            bg=COLORS["surface"], fg=COLORS["text"]
        ).pack(anchor="w")
        tk.Label(
            card.body, text="Select a row to edit, or define a new unit-price slab.",
            font=theme.FONTS["small"], bg=COLORS["surface"], fg=COLORS["text_muted"], wraplength=280, justify="left"
        ).pack(anchor="w", pady=(2, 14))

        grid = tk.Frame(card.body, bg=COLORS["surface"])
        grid.pack(fill="x")
        grid.grid_columnconfigure(0, weight=1)

        self.connection_type_combo = components.form_field(
            grid, 0, 0, "Connection Type", lambda p: theme.styled_combobox(p, CONNECTION_TYPES, width=22)
        )
        self.connection_type_combo.set("DOMESTIC")

        self.min_units_entry = components.form_field(
            grid, 1, 0, "Minimum Units", lambda p: theme.styled_entry(p, width=24)
        )
        self.max_units_entry = components.form_field(
            grid, 2, 0, "Maximum Units", lambda p: theme.styled_entry(p, width=24)
        )
        self.rate_per_unit_entry = components.form_field(
            grid, 3, 0, "Rate Per Unit (₹)", lambda p: theme.styled_entry(p, width=24)
        )

        button_row1 = tk.Frame(card.body, bg=COLORS["surface"])
        button_row1.pack(fill="x", pady=(10, 6))
        ttk.Button(
            button_row1, text="Add Tariff", style="Primary.TButton", command=self.add_tariff
        ).pack(side="left", fill="x", expand=True, padx=(0, 6))
        ttk.Button(
            button_row1, text="Update", style="Secondary.TButton", command=self.update_tariff
        ).pack(side="left", fill="x", expand=True)

        button_row2 = tk.Frame(card.body, bg=COLORS["surface"])
        button_row2.pack(fill="x")
        ttk.Button(
            button_row2, text="Delete", style="Destructive.TButton", command=self.delete_tariff
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
        card.body.grid_rowconfigure(1, weight=1)

        tk.Label(
            card.body, text="ALL TARIFF SLABS", font=theme.FONTS["h3"],
            bg=COLORS["surface"], fg=COLORS["text"]
        ).grid(row=0, column=0, sticky="w", pady=(0, 12))

        table_wrap = tk.Frame(card.body, bg=COLORS["surface"])
        table_wrap.grid(row=1, column=0, sticky="nsew")
        table_wrap.grid_columnconfigure(0, weight=1)
        table_wrap.grid_rowconfigure(0, weight=1)

        self.tariff_table = ttk.Treeview(table_wrap, columns=TABLE_COLUMNS, show="headings")
        for col in TABLE_COLUMNS:
            self.tariff_table.heading(col, text=TABLE_HEADINGS[col])
            self.tariff_table.column(col, width=160, anchor="center")

        components.configure_row_tags(self.tariff_table)

        scrollbar = ttk.Scrollbar(table_wrap, orient=tk.VERTICAL, command=self.tariff_table.yview)
        self.tariff_table.configure(yscrollcommand=scrollbar.set)

        self.tariff_table.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.tariff_table.bind("<ButtonRelease-1>", self.select_tariff)

        self.empty_state_holder = tk.Frame(table_wrap, bg=COLORS["surface"])
        self.empty_state_holder.grid(row=0, column=0, sticky="nsew")
        self.empty_state_holder.grid_remove()

    # =================================================================
    # DATA LOADING
    # =================================================================

    def load_tariffs(self):
        self.all_tariffs = get_all_tariffs() or []
        self._render_rows(self.all_tariffs)

    def _render_rows(self, tariffs):
        for item in self.tariff_table.get_children():
            self.tariff_table.delete(item)

        if not tariffs:
            self.tariff_table.grid_remove()
            self.empty_state_holder.grid()
            for w in self.empty_state_holder.winfo_children():
                w.destroy()
            EmptyState(
                self.empty_state_holder, "No tariff slabs configured",
                "Add a slab using the form to start billing customers."
            ).pack(fill="both", expand=True)
            return

        self.empty_state_holder.grid_remove()
        self.tariff_table.grid()

        for i, tariff in enumerate(tariffs):
            connection_type = tariff["connection_type"]
            kind = CONNECTION_TYPE_KIND.get(connection_type, "neutral")
            parity = "even" if i % 2 == 0 else "odd"

            self.tariff_table.insert(
                "", tk.END,
                values=(
                    tariff["tariff_id"],
                    connection_type,
                    f'{tariff["min_units"]} \u2013 {tariff["max_units"]} units',
                    f'\u20b9{float(tariff["rate_per_unit"]):.2f}',
                ),
                tags=(f"{kind}_{parity}",),
            )

    # =================================================================
    # SELECT
    # =================================================================

    def select_tariff(self, _event):
        selected = self.tariff_table.focus()
        if not selected:
            return

        values = self.tariff_table.item(selected, "values")
        if not values:
            return

        tariff_id = values[0]
        tariff = next((t for t in self.all_tariffs if str(t["tariff_id"]) == str(tariff_id)), None)
        if tariff is None:
            return

        self.selected_tariff_id = tariff["tariff_id"]
        self.banner.hide()

        self.connection_type_combo.set(tariff["connection_type"])
        self._set_entry(self.min_units_entry, tariff["min_units"])
        self._set_entry(self.max_units_entry, tariff["max_units"])
        self._set_entry(self.rate_per_unit_entry, tariff["rate_per_unit"])

    @staticmethod
    def _set_entry(entry, value):
        entry.delete(0, tk.END)
        entry.insert(0, value)

    # =================================================================
    # VALIDATE
    # =================================================================

    def validate_form(self):
        min_units = self.min_units_entry.get().strip()
        max_units = self.max_units_entry.get().strip()
        rate = self.rate_per_unit_entry.get().strip()

        if not min_units or not max_units or not rate:
            self.banner.show("Please fill in all fields.", kind="warning")
            return False

        try:
            min_units = int(min_units)
            max_units = int(max_units)
            rate = float(rate)
        except ValueError:
            self.banner.show("Units must be whole numbers and rate must be numeric.", kind="warning")
            return False

        if min_units < 0 or max_units < 0:
            self.banner.show("Units cannot be negative.", kind="warning")
            return False

        if max_units < min_units:
            self.banner.show("Maximum units cannot be less than minimum units.", kind="warning")
            return False

        if rate <= 0:
            self.banner.show("Rate per unit must be greater than 0.", kind="warning")
            return False

        return True

    # =================================================================
    # ADD / UPDATE / DELETE
    # =================================================================

    def add_tariff(self):
        if not self.validate_form():
            return

        success, message = add_tariff(
            self.connection_type_combo.get(),
            self.min_units_entry.get().strip(),
            self.max_units_entry.get().strip(),
            self.rate_per_unit_entry.get().strip(),
        )

        if success:
            self.banner.show(message, kind="success")
            self.clear_form()
            self.load_tariffs()
        else:
            self.banner.show(message, kind="danger")

    def update_tariff(self):
        if self.selected_tariff_id is None:
            self.banner.show("Select a tariff from the table first.", kind="warning")
            return

        if not self.validate_form():
            return

        success, message = update_tariff(
            self.selected_tariff_id,
            self.connection_type_combo.get(),
            self.min_units_entry.get().strip(),
            self.max_units_entry.get().strip(),
            self.rate_per_unit_entry.get().strip(),
        )

        if success:
            self.banner.show(message, kind="success")
            self.clear_form()
            self.load_tariffs()
        else:
            self.banner.show(message, kind="danger")

    def delete_tariff(self):
        if self.selected_tariff_id is None:
            self.banner.show("Select a tariff from the table first.", kind="warning")
            return

        confirm = messagebox.askyesno(
            "Confirm Delete", "Are you sure you want to delete this tariff slab? This cannot be undone."
        )
        if not confirm:
            return

        success = delete_tariff(self.selected_tariff_id)

        if success:
            self.banner.show("Tariff deleted successfully.", kind="success")
            self.clear_form()
            self.load_tariffs()
        else:
            self.banner.show("Could not delete tariff.", kind="danger")

    def clear_form(self):
        self.selected_tariff_id = None
        self.banner.hide()

        self.connection_type_combo.set("DOMESTIC")
        self.min_units_entry.delete(0, tk.END)
        self.max_units_entry.delete(0, tk.END)
        self.rate_per_unit_entry.delete(0, tk.END)
