import tkinter as tk
from tkinter import ttk, messagebox

from services.meter_service import (
    get_all_meters,
    add_meter,
    update_meter,
    delete_meter
)


class MeterManagement:

    def __init__(self):

        self.window = tk.Toplevel()

        self.window.title("Meter Management")
        self.window.geometry("1200x700")

        self.selected_meter_id = None

        # =========================================
        # Title
        # =========================================

        title = tk.Label(
            self.window,
            text="Meter Management",
            font=("Arial", 20, "bold")
        )

        title.pack(pady=15)

        # =========================================
        # Form
        # =========================================

        form_frame = tk.Frame(self.window)
        form_frame.pack(pady=10)

        # Customer ID
        tk.Label(
            form_frame,
            text="Customer ID"
        ).grid(row=0, column=0, padx=5, pady=5)

        self.customer_id_entry = tk.Entry(
            form_frame,
            width=20
        )

        self.customer_id_entry.grid(
            row=0,
            column=1,
            padx=5,
            pady=5
        )

        # Meter Number
        tk.Label(
            form_frame,
            text="Meter Number"
        ).grid(row=0, column=2, padx=5, pady=5)

        self.meter_number_entry = tk.Entry(
            form_frame,
            width=20
        )

        self.meter_number_entry.grid(
            row=0,
            column=3,
            padx=5,
            pady=5
        )

        # Meter Type
        tk.Label(
            form_frame,
            text="Meter Type"
        ).grid(row=1, column=0, padx=5, pady=5)

        self.meter_type_combo = ttk.Combobox(
            form_frame,
            values=[
                "SINGLE_PHASE",
                "THREE_PHASE"
            ],
            width=18,
            state="readonly"
        )

        self.meter_type_combo.grid(
            row=1,
            column=1,
            padx=5,
            pady=5
        )

        self.meter_type_combo.set("SINGLE_PHASE")

        # Installation Date
        tk.Label(
            form_frame,
            text="Installation Date"
        ).grid(row=1, column=2, padx=5, pady=5)

        self.installation_date_entry = tk.Entry(
            form_frame,
            width=20
        )

        self.installation_date_entry.grid(
            row=1,
            column=3,
            padx=5,
            pady=5
        )

        # Initial Reading
        tk.Label(
            form_frame,
            text="Initial Reading"
        ).grid(row=2, column=0, padx=5, pady=5)

        self.initial_reading_entry = tk.Entry(
            form_frame,
            width=20
        )

        self.initial_reading_entry.grid(
            row=2,
            column=1,
            padx=5,
            pady=5
        )

        # Current Reading
        tk.Label(
            form_frame,
            text="Current Reading"
        ).grid(row=2, column=2, padx=5, pady=5)

        self.current_reading_entry = tk.Entry(
            form_frame,
            width=20
        )

        self.current_reading_entry.grid(
            row=2,
            column=3,
            padx=5,
            pady=5
        )

        # Meter Status
        tk.Label(
            form_frame,
            text="Meter Status"
        ).grid(row=3, column=0, padx=5, pady=5)

        self.meter_status_combo = ttk.Combobox(
            form_frame,
            values=[
                "ACTIVE",
                "INACTIVE",
                "FAULTY"
            ],
            width=18,
            state="readonly"
        )

        self.meter_status_combo.grid(
            row=3,
            column=1,
            padx=5,
            pady=5
        )

        self.meter_status_combo.set("ACTIVE")

        # =========================================
        # Buttons
        # =========================================

        button_frame = tk.Frame(self.window)
        button_frame.pack(pady=10)

        tk.Button(
            button_frame,
            text="Add Meter",
            width=15,
            command=self.add_meter
        ).grid(row=0, column=0, padx=5)

        tk.Button(
            button_frame,
            text="Update Meter",
            width=15,
            command=self.update_meter
        ).grid(row=0, column=1, padx=5)

        tk.Button(
            button_frame,
            text="Delete Meter",
            width=15,
            command=self.delete_meter
        ).grid(row=0, column=2, padx=5)

        tk.Button(
            button_frame,
            text="Clear",
            width=15,
            command=self.clear_form
        ).grid(row=0, column=3, padx=5)

        tk.Button(
            button_frame,
            text="Refresh",
            width=15,
            command=self.load_meters
        ).grid(row=0, column=4, padx=5)

        # =========================================
        # Table
        # =========================================

        table_frame = tk.Frame(self.window)

        table_frame.pack(
            fill=tk.BOTH,
            expand=True,
            padx=15,
            pady=10
        )

        columns = (
            "meter_id",
            "customer_id",
            "meter_number",
            "meter_type",
            "installation_date",
            "initial_reading",
            "current_reading",
            "meter_status"
        )

        self.meter_table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings"
        )

        headings = {
            "meter_id": "Meter ID",
            "customer_id": "Customer ID",
            "meter_number": "Meter Number",
            "meter_type": "Meter Type",
            "installation_date": "Installation Date",
            "initial_reading": "Initial Reading",
            "current_reading": "Current Reading",
            "meter_status": "Status"
        }

        for column in columns:

            self.meter_table.heading(
                column,
                text=headings[column]
            )

            self.meter_table.column(
                column,
                width=140
            )

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient=tk.VERTICAL,
            command=self.meter_table.yview
        )

        self.meter_table.configure(
            yscrollcommand=scrollbar.set
        )

        self.meter_table.pack(
            side=tk.LEFT,
            fill=tk.BOTH,
            expand=True
        )

        scrollbar.pack(
            side=tk.RIGHT,
            fill=tk.Y
        )

        self.meter_table.bind(
            "<ButtonRelease-1>",
            self.select_meter
        )

        # Load meters
        self.load_meters()

    # =========================================
    # Load Meters
    # =========================================

    def load_meters(self):

        for item in self.meter_table.get_children():
            self.meter_table.delete(item)

        meters = get_all_meters()

        for meter in meters:

            self.meter_table.insert(
                "",
                tk.END,
                values=(
                    meter["meter_id"],
                    meter["customer_id"],
                    meter["meter_number"],
                    meter["meter_type"],
                    meter["installation_date"],
                    meter["initial_reading"],
                    meter["current_reading"],
                    meter["meter_status"]
                )
            )

    # =========================================
    # Select Meter
    # =========================================

    def select_meter(self, event):

        selected = self.meter_table.focus()

        if not selected:
            return

        values = self.meter_table.item(
            selected,
            "values"
        )

        if not values:
            return

        self.selected_meter_id = values[0]

        self.customer_id_entry.delete(0, tk.END)
        self.customer_id_entry.insert(0, values[1])

        self.meter_number_entry.delete(0, tk.END)
        self.meter_number_entry.insert(0, values[2])

        self.meter_type_combo.set(values[3])

        self.installation_date_entry.delete(0, tk.END)
        self.installation_date_entry.insert(0, values[4])

        self.initial_reading_entry.delete(0, tk.END)
        self.initial_reading_entry.insert(0, values[5])

        self.current_reading_entry.delete(0, tk.END)
        self.current_reading_entry.insert(0, values[6])

        self.meter_status_combo.set(values[7])

    # =========================================
    # Add Meter
    # =========================================

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
            self.meter_status_combo.get()
        )

        if success:

            messagebox.showinfo(
                "Success",
                "Meter added successfully."
            )

            self.clear_form()
            self.load_meters()

        else:

            messagebox.showerror(
                "Error",
                "Could not add meter.\n\n"
                "Make sure:\n"
                "- Customer ID exists\n"
                "- Customer does not already have a meter\n"
                "- Meter number is unique"
            )

    # =========================================
    # Update Meter
    # =========================================

    def update_meter(self):

        if self.selected_meter_id is None:

            messagebox.showwarning(
                "No Selection",
                "Please select a meter first."
            )

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
            self.meter_status_combo.get()
        )

        if success:

            messagebox.showinfo(
                "Success",
                "Meter updated successfully."
            )

            self.clear_form()
            self.load_meters()

        else:

            messagebox.showerror(
                "Error",
                "Could not update meter."
            )

    # =========================================
    # Delete Meter
    # =========================================

    def delete_meter(self):

        if self.selected_meter_id is None:

            messagebox.showwarning(
                "No Selection",
                "Please select a meter first."
            )

            return

        confirm = messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete this meter?"
        )

        if not confirm:
            return

        success = delete_meter(
            self.selected_meter_id
        )

        if success:

            messagebox.showinfo(
                "Success",
                "Meter deleted successfully."
            )

            self.clear_form()
            self.load_meters()

        else:

            messagebox.showerror(
                "Error",
                "Could not delete meter.\n"
                "The meter may be referenced by another table."
            )

    # =========================================
    # Clear Form
    # =========================================

    def clear_form(self):

        self.selected_meter_id = None

        self.customer_id_entry.delete(0, tk.END)
        self.meter_number_entry.delete(0, tk.END)
        self.installation_date_entry.delete(0, tk.END)
        self.initial_reading_entry.delete(0, tk.END)
        self.current_reading_entry.delete(0, tk.END)

        self.meter_type_combo.set("SINGLE_PHASE")
        self.meter_status_combo.set("ACTIVE")

    # =========================================
    # Validate Form
    # =========================================

    def validate_form(self):

        required_fields = [
            self.customer_id_entry.get().strip(),
            self.meter_number_entry.get().strip(),
            self.installation_date_entry.get().strip()
        ]

        if not all(required_fields):

            messagebox.showwarning(
                "Missing Information",
                "Please fill in Customer ID, Meter Number "
                "and Installation Date."
            )

            return False

        # Validate Customer ID
        try:
            int(self.customer_id_entry.get().strip())

        except ValueError:

            messagebox.showwarning(
                "Invalid Customer ID",
                "Customer ID must be a number."
            )

            return False

        # Validate readings
        try:

            initial = float(
                self.initial_reading_entry.get().strip()
                or 0
            )

            current = float(
                self.current_reading_entry.get().strip()
                or 0
            )

            if initial < 0 or current < 0:

                messagebox.showwarning(
                    "Invalid Reading",
                    "Meter readings cannot be negative."
                )

                return False

            if current < initial:

                messagebox.showwarning(
                    "Invalid Reading",
                    "Current reading cannot be less than "
                    "initial reading."
                )

                return False

        except ValueError:

            messagebox.showwarning(
                "Invalid Reading",
                "Readings must be numeric values."
            )

            return False

        return True