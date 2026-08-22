import tkinter as tk
from tkinter import ttk, messagebox

from services.payment_service import (
    get_unpaid_bills,
    make_payment,
    get_all_payments
)


class PaymentManagement:

    def __init__(self):

        self.window = tk.Toplevel()
        self.window.title("Payment Management")
        self.window.geometry("1150x700")

        self.selected_bill = None

        tk.Label(
            self.window,
            text="PAYMENT MANAGEMENT",
            font=("Arial", 20, "bold")
        ).pack(pady=15)

        columns = (
            "bill_id",
            "customer_name",
            "billing_month",
            "total_amount",
            "due_date"
        )

        self.bill_table = ttk.Treeview(
            self.window,
            columns=columns,
            show="headings",
            height=10
        )

        for col in columns:
            self.bill_table.heading(
                col,
                text=col.replace("_", " ").title()
            )
            self.bill_table.column(col, width=170, anchor="center")

        self.bill_table.pack(
            fill=tk.X,
            padx=20,
            pady=10
        )

        self.bill_table.bind(
            "<ButtonRelease-1>",
            self.select_bill
        )

        form = tk.Frame(self.window)
        form.pack(pady=10)

        tk.Label(form, text="Payment Method").grid(
            row=0, column=0, padx=10
        )

        self.method_combo = ttk.Combobox(
            form,
            values=[
                "CASH",
                "CARD",
                "UPI",
                "NET_BANKING"
            ],
            state="readonly",
            width=20
        )

        self.method_combo.grid(row=0, column=1)
        self.method_combo.set("CASH")

        tk.Label(form, text="Transaction ID").grid(
            row=1, column=0, padx=10, pady=10
        )

        self.transaction_entry = tk.Entry(form, width=25)
        self.transaction_entry.grid(row=1, column=1)

        tk.Button(
            form,
            text="Make Payment",
            width=20,
            command=self.pay
        ).grid(
            row=2,
            column=0,
            columnspan=2,
            pady=10
        )

        tk.Button(
            self.window,
            text="Refresh",
            command=self.load_unpaid_bills
        ).pack(pady=5)

        self.load_unpaid_bills()


    def load_unpaid_bills(self):

        for item in self.bill_table.get_children():
            self.bill_table.delete(item)

        bills = get_unpaid_bills()

        for bill in bills:
            self.bill_table.insert(
                "",
                tk.END,
                values=(
                    bill["bill_id"],
                    bill["customer_name"],
                    bill["billing_month"],
                    bill["total_amount"],
                    bill["due_date"]
                )
            )


    def select_bill(self, event):

        selected = self.bill_table.focus()

        if not selected:
            return

        values = self.bill_table.item(
            selected,
            "values"
        )

        self.selected_bill = values


    def pay(self):

        if not self.selected_bill:
            messagebox.showwarning(
                "Error",
                "Select a bill first."
            )
            return

        bill_id = self.selected_bill[0]
        customer_name = self.selected_bill[1]
        amount = self.selected_bill[3]

        success, message = make_payment(
            bill_id,
            customer_name,
            amount,
            self.method_combo.get(),
            self.transaction_entry.get().strip()
        )

        if success:

            messagebox.showinfo(
                "Success",
                message
            )

            self.selected_bill = None
            self.transaction_entry.delete(0, tk.END)
            self.load_unpaid_bills()

        else:

            messagebox.showerror(
                "Error",
                message
            )