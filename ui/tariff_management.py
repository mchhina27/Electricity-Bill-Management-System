import tkinter as tk
from tkinter import ttk, messagebox

from services.tariff_service import (
    get_all_tariffs,
    add_tariff,
    update_tariff,
    delete_tariff
)


class TariffManagement:

    def __init__(self):

        self.window = tk.Toplevel()

        self.window.title("Tariff Management")
        self.window.geometry("900x650")

        self.selected_tariff_id = None

        # =========================================
        # Title
        # =========================================

        title = tk.Label(
            self.window,
            text="TARIFF MANAGEMENT",
            font=("Arial", 20, "bold")
        )

        title.pack(pady=20)

        # =========================================
        # Form
        # =========================================

        form_frame = tk.Frame(self.window)
        form_frame.pack(pady=10)

        # Connection Type

        tk.Label(
            form_frame,
            text="Connection Type"
        ).grid(
            row=0,
            column=0,
            padx=10,
            pady=10
        )

        self.connection_type_combo = ttk.Combobox(
            form_frame,
            values=[
                "DOMESTIC",
                "COMMERCIAL",
                "INDUSTRIAL"
            ],
            state="readonly",
            width=20
        )

        self.connection_type_combo.grid(
            row=0,
            column=1,
            padx=10,
            pady=10
        )

        self.connection_type_combo.set("DOMESTIC")

        # Minimum Units

        tk.Label(
            form_frame,
            text="Minimum Units"
        ).grid(
            row=1,
            column=0,
            padx=10,
            pady=10
        )

        self.min_units_entry = tk.Entry(
            form_frame,
            width=23
        )

        self.min_units_entry.grid(
            row=1,
            column=1,
            padx=10,
            pady=10
        )

        # Maximum Units

        tk.Label(
            form_frame,
            text="Maximum Units"
        ).grid(
            row=2,
            column=0,
            padx=10,
            pady=10
        )

        self.max_units_entry = tk.Entry(
            form_frame,
            width=23
        )

        self.max_units_entry.grid(
            row=2,
            column=1,
            padx=10,
            pady=10
        )

        # Rate Per Unit

        tk.Label(
            form_frame,
            text="Rate Per Unit"
        ).grid(
            row=3,
            column=0,
            padx=10,
            pady=10
        )

        self.rate_per_unit_entry = tk.Entry(
            form_frame,
            width=23
        )

        self.rate_per_unit_entry.grid(
            row=3,
            column=1,
            padx=10,
            pady=10
        )

        # =========================================
        # Buttons
        # =========================================

        button_frame = tk.Frame(self.window)
        button_frame.pack(pady=15)

        tk.Button(
            button_frame,
            text="Add Tariff",
            width=15,
            command=self.add_tariff
        ).grid(
            row=0,
            column=0,
            padx=5
        )

        tk.Button(
            button_frame,
            text="Update Tariff",
            width=15,
            command=self.update_tariff
        ).grid(
            row=0,
            column=1,
            padx=5
        )

        tk.Button(
            button_frame,
            text="Delete Tariff",
            width=15,
            command=self.delete_tariff
        ).grid(
            row=0,
            column=2,
            padx=5
        )

        tk.Button(
            button_frame,
            text="Clear",
            width=15,
            command=self.clear_form
        ).grid(
            row=0,
            column=3,
            padx=5
        )

        tk.Button(
            button_frame,
            text="Refresh",
            width=15,
            command=self.load_tariffs
        ).grid(
            row=0,
            column=4,
            padx=5
        )

        # =========================================
        # Table
        # =========================================

        table_frame = tk.Frame(self.window)

        table_frame.pack(
            fill=tk.BOTH,
            expand=True,
            padx=20,
            pady=15
        )

        columns = (
            "tariff_id",
            "connection_type",
            "min_units",
            "max_units",
            "rate_per_unit"
        )

        self.tariff_table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings"
        )

        headings = {
            "tariff_id": "Tariff ID",
            "connection_type": "Connection Type",
            "min_units": "Minimum Units",
            "max_units": "Maximum Units",
            "rate_per_unit": "Rate Per Unit"
        }

        for column in columns:

            self.tariff_table.heading(
                column,
                text=headings[column]
            )

            self.tariff_table.column(
                column,
                width=150,
                anchor="center"
            )

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient=tk.VERTICAL,
            command=self.tariff_table.yview
        )

        self.tariff_table.configure(
            yscrollcommand=scrollbar.set
        )

        self.tariff_table.pack(
            side=tk.LEFT,
            fill=tk.BOTH,
            expand=True
        )

        scrollbar.pack(
            side=tk.RIGHT,
            fill=tk.Y
        )

        self.tariff_table.bind(
            "<ButtonRelease-1>",
            self.select_tariff
        )

        self.load_tariffs()


    # =========================================
    # Load Tariffs
    # =========================================

    def load_tariffs(self):

        for item in self.tariff_table.get_children():
            self.tariff_table.delete(item)

        tariffs = get_all_tariffs()

        for tariff in tariffs:

            self.tariff_table.insert(
                "",
                tk.END,
                values=(
                    tariff["tariff_id"],
                    tariff["connection_type"],
                    tariff["min_units"],
                    tariff["max_units"],
                    tariff["rate_per_unit"]
                )
            )


    # =========================================
    # Select Tariff
    # =========================================

    def select_tariff(self, event):

        selected = self.tariff_table.focus()

        if not selected:
            return

        values = self.tariff_table.item(
            selected,
            "values"
        )

        if not values:
            return

        self.selected_tariff_id = values[0]

        self.connection_type_combo.set(values[1])

        self.min_units_entry.delete(
            0,
            tk.END
        )

        self.min_units_entry.insert(
            0,
            values[2]
        )

        self.max_units_entry.delete(
            0,
            tk.END
        )

        self.max_units_entry.insert(
            0,
            values[3]
        )

        self.rate_per_unit_entry.delete(
            0,
            tk.END
        )

        self.rate_per_unit_entry.insert(
            0,
            values[4]
        )


    # =========================================
    # Add Tariff
    # =========================================

    def add_tariff(self):

        if not self.validate_form():
            return

        success = add_tariff(
            self.connection_type_combo.get(),
            self.min_units_entry.get().strip(),
            self.max_units_entry.get().strip(),
            self.rate_per_unit_entry.get().strip()
        )

        if success:

            messagebox.showinfo(
                "Success",
                "Tariff added successfully."
            )

            self.clear_form()
            self.load_tariffs()

        else:

            messagebox.showerror(
                "Error",
                "Could not add tariff."
            )


    # =========================================
    # Update Tariff
    # =========================================

    def update_tariff(self):

        if self.selected_tariff_id is None:

            messagebox.showwarning(
                "No Selection",
                "Please select a tariff first."
            )

            return

        if not self.validate_form():
            return

        success = update_tariff(
            self.selected_tariff_id,
            self.connection_type_combo.get(),
            self.min_units_entry.get().strip(),
            self.max_units_entry.get().strip(),
            self.rate_per_unit_entry.get().strip()
        )

        if success:

            messagebox.showinfo(
                "Success",
                "Tariff updated successfully."
            )

            self.clear_form()
            self.load_tariffs()

        else:

            messagebox.showerror(
                "Error",
                "Could not update tariff."
            )


    # =========================================
    # Delete Tariff
    # =========================================

    def delete_tariff(self):

        if self.selected_tariff_id is None:

            messagebox.showwarning(
                "No Selection",
                "Please select a tariff first."
            )

            return

        confirm = messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete this tariff?"
        )

        if not confirm:
            return

        success = delete_tariff(
            self.selected_tariff_id
        )

        if success:

            messagebox.showinfo(
                "Success",
                "Tariff deleted successfully."
            )

            self.clear_form()
            self.load_tariffs()

        else:

            messagebox.showerror(
                "Error",
                "Could not delete tariff."
            )


    # =========================================
    # Clear Form
    # =========================================

    def clear_form(self):

        self.selected_tariff_id = None

        self.connection_type_combo.set("DOMESTIC")

        self.min_units_entry.delete(
            0,
            tk.END
        )

        self.max_units_entry.delete(
            0,
            tk.END
        )

        self.rate_per_unit_entry.delete(
            0,
            tk.END
        )


    # =========================================
    # Validate Form
    # =========================================

    def validate_form(self):

        min_units = self.min_units_entry.get().strip()
        max_units = self.max_units_entry.get().strip()
        rate = self.rate_per_unit_entry.get().strip()

        if not min_units or not max_units or not rate:

            messagebox.showwarning(
                "Missing Information",
                "Please fill in all fields."
            )

            return False

        try:

            min_units = int(min_units)
            max_units = int(max_units)
            rate = float(rate)

        except ValueError:

            messagebox.showwarning(
                "Invalid Input",
                "Units must be whole numbers and rate must be numeric."
            )

            return False

        if min_units < 0 or max_units < 0:

            messagebox.showwarning(
                "Invalid Units",
                "Units cannot be negative."
            )

            return False

        if max_units < min_units:

            messagebox.showwarning(
                "Invalid Range",
                "Maximum Units cannot be less than Minimum Units."
            )

            return False

        if rate <= 0:

            messagebox.showwarning(
                "Invalid Rate",
                "Rate Per Unit must be greater than 0."
            )

            return False

        return True