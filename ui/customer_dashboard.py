import tkinter as tk
from tkinter import ttk

from services.bill_service import get_customer_bills


class CustomerDashboard:

    def __init__(self, customer_id):

        self.customer_id = customer_id

        self.window = tk.Toplevel()

        self.window.title("Customer Dashboard")
        self.window.geometry("1000x600")

        tk.Label(
            self.window,
            text="CUSTOMER DASHBOARD",
            font=("Arial", 20, "bold")
        ).pack(pady=20)

        tk.Label(
            self.window,
            text=f"Customer ID: {self.customer_id}",
            font=("Arial", 12)
        ).pack()

        columns = (
            "bill_id",
            "billing_month",
            "previous_reading",
            "current_reading",
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

            self.table.column(
                column,
                width=120,
                anchor="center"
            )

        self.table.pack(
            fill=tk.BOTH,
            expand=True,
            padx=20,
            pady=20
        )

        tk.Button(
            self.window,
            text="Refresh Bills",
            command=self.load_bills
        ).pack(pady=10)

        self.load_bills()


    def load_bills(self):

        for item in self.table.get_children():
            self.table.delete(item)

        bills = get_customer_bills(self.customer_id)

        for bill in bills:

            self.table.insert(
                "",
                tk.END,
                values=(
                    bill["bill_id"],
                    bill["billing_month"],
                    bill["previous_reading"],
                    bill["current_reading"],
                    bill["units_consumed"],
                    bill["total_amount"],
                    bill["due_date"],
                    bill["status"]
                )
            )