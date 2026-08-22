import tkinter as tk
from tkinter import ttk, messagebox

from services.bill_service import (
    get_all_bills,
    get_customer_meter_details,
    get_last_bill_reading,
    generate_bill
)


class BillManagement:

    def __init__(self):

        self.window = tk.Toplevel()
        self.window.title("Bill Management")
        self.window.geometry("1250x700")

        tk.Label(
            self.window,
            text="BILL MANAGEMENT",
            font=("Arial", 20, "bold")
        ).pack(pady=15)

        form = tk.Frame(self.window)
        form.pack(pady=10)

        tk.Label(form, text="Customer ID").grid(row=0, column=0, padx=10, pady=5)

        self.customer_id_entry = tk.Entry(form, width=20)
        self.customer_id_entry.grid(row=0, column=1)

        tk.Button(
            form,
            text="Load Customer",
            command=self.load_customer
        ).grid(row=0, column=2, padx=10)

        tk.Label(form, text="Billing Month (YYYY-MM-DD)").grid(
            row=1, column=0, padx=10, pady=5
        )

        self.billing_month_entry = tk.Entry(form, width=20)
        self.billing_month_entry.grid(row=1, column=1)

        tk.Label(form, text="Previous Reading").grid(
            row=2, column=0, padx=10, pady=5
        )

        self.previous_entry = tk.Entry(form, width=20)
        self.previous_entry.grid(row=2, column=1)

        tk.Label(form, text="Current Reading").grid(
            row=3, column=0, padx=10, pady=5
        )

        self.current_entry = tk.Entry(form, width=20)
        self.current_entry.grid(row=3, column=1)

        tk.Button(
            form,
            text="Generate Bill",
            width=20,
            command=self.create_bill
        ).grid(row=4, column=0, columnspan=2, pady=15)

        self.customer_data = None

        columns = (
            "bill_id",
            "customer_id",
            "customer_name",
            "billing_month",
            "units_consumed",
            "total_amount",
            "due_date",
            "status"
        )

        self.table = ttk.Treeview(
            self.window,
            columns=columns,
            show="headings"
        )

        for column in columns:
            self.table.heading(
                column,
                text=column.replace("_", " ").title()
            )
            self.table.column(column, width=130, anchor="center")

        self.table.pack(
            fill=tk.BOTH,
            expand=True,
            padx=20,
            pady=20
        )

        self.load_bills()


    def load_customer(self):

        customer_id = self.customer_id_entry.get().strip()

        if not customer_id:
            messagebox.showwarning(
                "Error",
                "Enter Customer ID."
            )
            return

        self.customer_data = get_customer_meter_details(customer_id)

        if not self.customer_data:
            messagebox.showerror(
                "Error",
                "Customer or meter not found."
            )
            return

        previous_reading = get_last_bill_reading(customer_id)

        self.previous_entry.delete(0, tk.END)
        self.previous_entry.insert(0, previous_reading)

        messagebox.showinfo(
            "Customer Loaded",
            "Customer and meter details loaded successfully."
        )


    def create_bill(self):

        if not self.customer_data:
            messagebox.showwarning(
                "Error",
                "Load customer first."
            )
            return

        billing_month = self.billing_month_entry.get().strip()
        previous = self.previous_entry.get().strip()
        current = self.current_entry.get().strip()

        if not billing_month or not previous or not current:
            messagebox.showwarning(
                "Error",
                "Fill all bill fields."
            )
            return

        data = self.customer_data

        try:
            success, result = generate_bill(
                data["customer_id"],
                data.get("customer_name", ""),
                data.get("email", ""),
                data.get("phone", ""),
                data.get("address", ""),
                data.get("connection_type", "DOMESTIC"),
                data.get("meter_number", ""),
                billing_month,
                previous,
                current
            )

            if success:
                messagebox.showinfo(
                    "Success",
                    f"Bill generated successfully.\nTotal Amount: ₹{result}"
                )

                self.current_entry.delete(0, tk.END)
                self.billing_month_entry.delete(0, tk.END)
                self.load_bills()

            else:
                messagebox.showerror(
                    "Error",
                    str(result)
                )

        except Exception as e:
            messagebox.showerror(
                "Error",
                str(e)
            )


    def load_bills(self):

        for item in self.table.get_children():
            self.table.delete(item)

        bills = get_all_bills()

        for bill in bills:
            self.table.insert(
                "",
                tk.END,
                values=(
                    bill["bill_id"],
                    bill["customer_id"],
                    bill["customer_name"],
                    bill["billing_month"],
                    bill["units_consumed"],
                    bill["total_amount"],
                    bill["due_date"],
                    bill["status"]
                )
            )