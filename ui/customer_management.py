import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

from services.customer_service import (
    get_all_customers,
    add_customer,
    update_customer,
    delete_customer
)


class CustomerManagement:

    def __init__(self):

        self.window = tk.Toplevel()

        self.window.title("Customer Management")
        self.window.geometry("1200x850")

        self.selected_customer_id = None

        # =========================================
        # TITLE
        # =========================================

        tk.Label(
            self.window,
            text="CUSTOMER MANAGEMENT",
            font=("Arial", 20, "bold")
        ).pack(pady=15)

        # =========================================
        # FORM
        # =========================================

        form_frame = tk.Frame(self.window)
        form_frame.pack(pady=10)

        # First Name
        tk.Label(form_frame, text="First Name").grid(
            row=0, column=0, padx=10, pady=7, sticky="w"
        )

        self.first_name_entry = tk.Entry(form_frame, width=25)
        self.first_name_entry.grid(
            row=0, column=1, padx=10, pady=7
        )

        # Last Name
        tk.Label(form_frame, text="Last Name").grid(
            row=0, column=2, padx=10, pady=7, sticky="w"
        )

        self.last_name_entry = tk.Entry(form_frame, width=25)
        self.last_name_entry.grid(
            row=0, column=3, padx=10, pady=7
        )

        # Email
        tk.Label(form_frame, text="Email").grid(
            row=1, column=0, padx=10, pady=7, sticky="w"
        )

        self.email_entry = tk.Entry(form_frame, width=25)
        self.email_entry.grid(
            row=1, column=1, padx=10, pady=7
        )

        # Phone
        tk.Label(form_frame, text="Phone").grid(
            row=1, column=2, padx=10, pady=7, sticky="w"
        )

        self.phone_entry = tk.Entry(form_frame, width=25)
        self.phone_entry.grid(
            row=1, column=3, padx=10, pady=7
        )

        # Address
        tk.Label(form_frame, text="Address").grid(
            row=2, column=0, padx=10, pady=7, sticky="w"
        )

        self.address_entry = tk.Entry(form_frame, width=25)
        self.address_entry.grid(
            row=2, column=1, padx=10, pady=7
        )

        # City
        tk.Label(form_frame, text="City").grid(
            row=2, column=2, padx=10, pady=7, sticky="w"
        )

        self.city_entry = tk.Entry(form_frame, width=25)
        self.city_entry.grid(
            row=2, column=3, padx=10, pady=7
        )

        # State
        tk.Label(form_frame, text="State").grid(
            row=3, column=0, padx=10, pady=7, sticky="w"
        )

        self.state_entry = tk.Entry(form_frame, width=25)
        self.state_entry.grid(
            row=3, column=1, padx=10, pady=7
        )

        # Pincode
        tk.Label(form_frame, text="Pincode").grid(
            row=3, column=2, padx=10, pady=7, sticky="w"
        )

        self.pincode_entry = tk.Entry(form_frame, width=25)
        self.pincode_entry.grid(
            row=3, column=3, padx=10, pady=7
        )

        # Connection Date
        tk.Label(
            form_frame,
            text="Connection Date (YYYY-MM-DD)"
        ).grid(
            row=4, column=0, padx=10, pady=7, sticky="w"
        )

        self.connection_date_entry = tk.Entry(
            form_frame,
            width=25
        )

        self.connection_date_entry.grid(
            row=4, column=1, padx=10, pady=7
        )

        self.connection_date_entry.insert(
            0,
            date.today().strftime("%Y-%m-%d")
        )

        # Connection Type
        tk.Label(form_frame, text="Connection Type").grid(
            row=4, column=2, padx=10, pady=7, sticky="w"
        )

        self.connection_type_combo = ttk.Combobox(
            form_frame,
            values=[
                "DOMESTIC",
                "COMMERCIAL",
                "INDUSTRIAL"
            ],
            state="readonly",
            width=22
        )

        self.connection_type_combo.grid(
            row=4, column=3, padx=10, pady=7
        )

        self.connection_type_combo.set("DOMESTIC")

        # =========================================
        # BUTTONS
        # =========================================

        button_frame = tk.Frame(self.window)
        button_frame.pack(pady=15)

        tk.Button(
            button_frame,
            text="Add Customer",
            width=16,
            command=self.add_customer
        ).grid(row=0, column=0, padx=5)

        tk.Button(
            button_frame,
            text="Update Customer",
            width=16,
            command=self.update_customer
        ).grid(row=0, column=1, padx=5)

        tk.Button(
            button_frame,
            text="Delete Customer",
            width=16,
            command=self.delete_customer
        ).grid(row=0, column=2, padx=5)

        tk.Button(
            button_frame,
            text="Clear",
            width=16,
            command=self.clear_form
        ).grid(row=0, column=3, padx=5)

        tk.Button(
            button_frame,
            text="Refresh",
            width=16,
            command=self.load_customers
        ).grid(row=0, column=4, padx=5)

        # =========================================
        # TABLE
        # =========================================

        table_frame = tk.Frame(self.window)

        table_frame.pack(
            fill=tk.BOTH,
            expand=True,
            padx=20,
            pady=10
        )

        columns = (
            "customer_id",
            "first_name",
            "last_name",
            "email",
            "phone",
            "city",
            "state",
            "connection_type"
        )

        self.customer_table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings"
        )

        for column in columns:

            self.customer_table.heading(
                column,
                text=column.replace("_", " ").title()
            )

            self.customer_table.column(
                column,
                width=130,
                anchor="center"
            )

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient=tk.VERTICAL,
            command=self.customer_table.yview
        )

        self.customer_table.configure(
            yscrollcommand=scrollbar.set
        )

        self.customer_table.pack(
            side=tk.LEFT,
            fill=tk.BOTH,
            expand=True
        )

        scrollbar.pack(
            side=tk.RIGHT,
            fill=tk.Y
        )

        self.customer_table.bind(
            "<ButtonRelease-1>",
            self.select_customer
        )

        self.load_customers()


    # =========================================
    # LOAD CUSTOMERS
    # =========================================

    def load_customers(self):

        for item in self.customer_table.get_children():
            self.customer_table.delete(item)

        customers = get_all_customers()

        for customer in customers:

            self.customer_table.insert(
                "",
                tk.END,
                values=(
                    customer.get("customer_id", ""),
                    customer.get("first_name", ""),
                    customer.get("last_name", ""),
                    customer.get("email", ""),
                    customer.get("phone", ""),
                    customer.get("city", ""),
                    customer.get("state", ""),
                    customer.get("connection_type", "")
                )
            )


    # =========================================
    # SELECT CUSTOMER
    # =========================================

    def select_customer(self, event):

        selected = self.customer_table.focus()

        if not selected:
            return

        values = self.customer_table.item(
            selected,
            "values"
        )

        if not values:
            return

        customer_id = values[0]

        customers = get_all_customers()

        customer = None

        for item in customers:

            if str(item["customer_id"]) == str(customer_id):
                customer = item
                break

        if customer is None:
            return

        self.selected_customer_id = customer["customer_id"]

        self.first_name_entry.delete(0, tk.END)
        self.first_name_entry.insert(
            0,
            customer.get("first_name", "")
        )

        self.last_name_entry.delete(0, tk.END)
        self.last_name_entry.insert(
            0,
            customer.get("last_name", "")
        )

        self.email_entry.delete(0, tk.END)
        self.email_entry.insert(
            0,
            customer.get("email", "")
        )

        self.phone_entry.delete(0, tk.END)
        self.phone_entry.insert(
            0,
            customer.get("phone", "")
        )

        self.address_entry.delete(0, tk.END)
        self.address_entry.insert(
            0,
            customer.get("address", "")
        )

        self.city_entry.delete(0, tk.END)
        self.city_entry.insert(
            0,
            customer.get("city", "")
        )

        self.state_entry.delete(0, tk.END)
        self.state_entry.insert(
            0,
            customer.get("state", "")
        )

        self.pincode_entry.delete(0, tk.END)
        self.pincode_entry.insert(
            0,
            customer.get("pincode", "")
        )

        self.connection_date_entry.delete(0, tk.END)

        connection_date = customer.get(
            "connection_date",
            ""
        )

        self.connection_date_entry.insert(
            0,
            str(connection_date)
        )

        self.connection_type_combo.set(
            customer.get("connection_type", "DOMESTIC")
        )


    # =========================================
    # VALIDATE FORM
    # =========================================

    def validate_form(self):

        fields = [
            self.first_name_entry.get().strip(),
            self.last_name_entry.get().strip(),
            self.email_entry.get().strip(),
            self.phone_entry.get().strip(),
            self.address_entry.get().strip(),
            self.city_entry.get().strip(),
            self.state_entry.get().strip(),
            self.connection_date_entry.get().strip()
        ]

        if not all(fields):

            messagebox.showwarning(
                "Missing Information",
                "Please fill in all required fields."
            )

            return False

        email = self.email_entry.get().strip()

        if "@" not in email or "." not in email:

            messagebox.showwarning(
                "Invalid Email",
                "Please enter a valid email."
            )

            return False

        connection_date = self.connection_date_entry.get().strip()

        try:

            date.fromisoformat(connection_date)

        except ValueError:

            messagebox.showwarning(
                "Invalid Date",
                "Use YYYY-MM-DD format."
            )

            return False

        return True


    # =========================================
    # ADD CUSTOMER
    # =========================================

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
            self.connection_type_combo.get().strip()
        )

        if success:

            messagebox.showinfo(
                "Success",
                message
            )

            self.clear_form()
            self.load_customers()

        else:

            messagebox.showerror(
                "Error",
                message
            )


    # =========================================
    # UPDATE CUSTOMER
    # =========================================

    def update_customer(self):

        if self.selected_customer_id is None:

            messagebox.showwarning(
                "No Selection",
                "Please select a customer first."
            )

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
            self.connection_type_combo.get().strip()
        )

        if success:

            messagebox.showinfo(
                "Success",
                message
            )

            self.clear_form()
            self.load_customers()

        else:

            messagebox.showerror(
                "Error",
                message
            )


    # =========================================
    # DELETE CUSTOMER
    # =========================================

    def delete_customer(self):

        if self.selected_customer_id is None:

            messagebox.showwarning(
                "No Selection",
                "Please select a customer first."
            )

            return

        confirm = messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete this customer?"
        )

        if not confirm:
            return

        success, message = delete_customer(
            self.selected_customer_id
        )

        if success:

            messagebox.showinfo(
                "Success",
                message
            )

            self.clear_form()
            self.load_customers()

        else:

            messagebox.showerror(
                "Error",
                message
            )


    # =========================================
    # CLEAR FORM
    # =========================================

    def clear_form(self):

        self.selected_customer_id = None

        entries = [
            self.first_name_entry,
            self.last_name_entry,
            self.email_entry,
            self.phone_entry,
            self.address_entry,
            self.city_entry,
            self.state_entry,
            self.pincode_entry,
            self.connection_date_entry
        ]

        for entry in entries:
            entry.delete(0, tk.END)

        self.connection_date_entry.insert(
            0,
            date.today().strftime("%Y-%m-%d")
        )

        self.connection_type_combo.set("DOMESTIC")