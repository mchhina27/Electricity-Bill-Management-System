import tkinter as tk

from ui.customer_management import CustomerManagement
from ui.meter_management import MeterManagement
from ui.tariff_management import TariffManagement
from ui.bill_management import BillManagement
from ui.payment_management import PaymentManagement
from ui.reports import Reports


class AdminDashboard:

    def __init__(self):

        self.window = tk.Toplevel()

        self.window.title("Admin Dashboard")
        self.window.geometry("700x700")

        tk.Label(
            self.window,
            text="ADMIN DASHBOARD",
            font=("Arial", 22, "bold")
        ).pack(pady=25)

        buttons = [
            ("Customer Management", self.open_customer_management),
            ("Meter Management", self.open_meter_management),
            ("Tariff Management", self.open_tariff_management),
            ("Bill Management", self.open_bill_management),
            ("Payment Management", self.open_payment_management),
            ("Reports / Statistics", self.open_reports)
        ]

        for text, command in buttons:

            tk.Button(
                self.window,
                text=text,
                width=35,
                height=2,
                command=command
            ).pack(pady=7)


    def open_customer_management(self):
        CustomerManagement()


    def open_meter_management(self):
        MeterManagement()


    def open_tariff_management(self):
        TariffManagement()


    def open_bill_management(self):
        BillManagement()


    def open_payment_management(self):
        PaymentManagement()


    def open_reports(self):
        Reports()