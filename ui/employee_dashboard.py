"""
Employee application shell -- same visual shell as the Admin dashboard,
but with a restricted set of sections (no Tariffs, no Employee accounts).
"""

import tkinter as tk
from tkinter import messagebox

from ui import theme
from ui.theme import COLORS
from ui.components import Sidebar, TopBar, ScrollableFrame

from ui.dashboard_page import DashboardPage
from ui.customer_management import CustomerManagementPage
from ui.meter_management import MeterManagementPage
from ui.bill_management import BillManagementPage
from ui.payment_management import PaymentManagementPage
from ui.reports import ReportsPage
from ui.grievance_management import GrievanceManagementPage


NAV_SECTIONS = [
    ("OVERVIEW", [
        ("dashboard", "Dashboard"),
    ]),
    ("MANAGEMENT", [
        ("customers", "Customers"),
        ("meters", "Meters"),
    ]),
    ("BILLING", [
        ("bills", "Bills"),
        ("payments", "Payments"),
    ]),
    ("INSIGHTS", [
        ("grievances", "Grievances"),
        ("reports", "Reports"),
    ]),
]

PAGE_REGISTRY = {
    "dashboard": (DashboardPage, "Dashboard", "Overview of billing activity and system status"),
    "customers": (CustomerManagementPage, "Customer Management", "Manage customer accounts and connection details"),
    "meters": (MeterManagementPage, "Meter Management", "Track meters, readings and device status"),
    "bills": (BillManagementPage, "Bill Management", "Generate and review customer electricity bills"),
    "payments": (PaymentManagementPage, "Payment Management", "Record and track incoming bill payments"),
    "grievances": (GrievanceManagementPage, "Grievances", "Review and resolve customer-submitted grievances"),
    "reports": (ReportsPage, "Reports", "Billing and collection statistics"),
}


class EmployeeDashboard:

    def __init__(self, employee_name=None, on_logout=None):
        self.on_logout = on_logout
        self.employee_name = employee_name or "Employee"

        self.window = tk.Toplevel()
        self.window.title("Electricity Billing Management System — Employee")
        self.window.geometry("1360x830")
        self.window.minsize(1080, 640)

        theme.apply_theme(self.window)

        self.window.grid_columnconfigure(1, weight=1)
        self.window.grid_rowconfigure(0, weight=1)

        self.current_page_key = None
        self.current_page_widget = None

        self.sidebar = Sidebar(
            self.window,
            sections=NAV_SECTIONS,
            on_select=self.show_page,
            brand_title="VOLTGRID",
            brand_subtitle="ELECTRIC UTILITY",
        )
        self.sidebar.grid(row=0, column=0, sticky="ns")

        right = tk.Frame(self.window, bg=COLORS["bg"])
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(1, weight=1)

        self.topbar = TopBar(
            right, user_label=self.employee_name, role_label="EMPLOYEE ACCESS", on_logout=self.logout
        )
        self.topbar.grid(row=0, column=0, sticky="ew")

        self.content_scroll = ScrollableFrame(right, bg=COLORS["bg"])
        self.content_scroll.grid(row=1, column=0, sticky="nsew")
        self.content = self.content_scroll.inner

        self.window.protocol("WM_DELETE_WINDOW", self.logout)

        self.show_page("dashboard")

    def show_page(self, key):
        if key not in PAGE_REGISTRY:
            return

        page_class, title, subtitle = PAGE_REGISTRY[key]

        if self.current_page_widget is not None:
            self.current_page_widget.destroy()

        self.current_page_key = key
        self.sidebar.set_active(key)
        self.topbar.set_title(title, subtitle)

        self.current_page_widget = page_class(self.content)
        self.current_page_widget.grid(row=0, column=0, sticky="nsew")

        self.content_scroll.canvas.yview_moveto(0)

    def logout(self):
        confirm = messagebox.askyesno("Log Out", "Are you sure you want to log out?")
        if not confirm:
            return

        self.window.destroy()

        if self.on_logout:
            self.on_logout()
