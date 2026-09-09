"""
Admin application shell: persistent sidebar + top bar + a content area that
swaps between pages. This replaces the old design where every section
(Customers, Meters, Tariffs, ...) opened as its own separate Toplevel window.

None of the underlying service calls changed -- each page class below still
calls the exact same functions from services/*.py that the original
Toplevel-based screens did.
"""

import tkinter as tk
from tkinter import messagebox

from ui import theme
from ui.theme import COLORS
from ui.components import Sidebar, TopBar

from ui.dashboard_page import DashboardPage
from ui.customer_management import CustomerManagementPage
from ui.meter_management import MeterManagementPage
from ui.tariff_management import TariffManagementPage
from ui.bill_management import BillManagementPage
from ui.payment_management import PaymentManagementPage
from ui.reports import ReportsPage


NAV_SECTIONS = [
    ("OVERVIEW", [
        ("dashboard", "Dashboard"),
    ]),
    ("MANAGEMENT", [
        ("customers", "Customers"),
        ("meters", "Meters"),
        ("tariffs", "Tariffs"),
    ]),
    ("BILLING", [
        ("bills", "Bills"),
        ("payments", "Payments"),
    ]),
    ("INSIGHTS", [
        ("reports", "Reports"),
    ]),
]

# key -> (PageClass, title, subtitle)
PAGE_REGISTRY = {
    "dashboard": (DashboardPage, "Dashboard", "Overview of billing activity and system status"),
    "customers": (CustomerManagementPage, "Customer Management", "Manage customer accounts and connection details"),
    "meters": (MeterManagementPage, "Meter Management", "Track meters, readings and device status"),
    "tariffs": (TariffManagementPage, "Tariff Management", "Configure slab-based unit rates by connection type"),
    "bills": (BillManagementPage, "Bill Management", "Generate and review customer electricity bills"),
    "payments": (PaymentManagementPage, "Payment Management", "Record and track incoming bill payments"),
    "reports": (ReportsPage, "Reports", "Billing and collection statistics"),
}


class AdminDashboard:

    def __init__(self, on_logout=None):
        self.on_logout = on_logout

        self.window = tk.Toplevel()
        self.window.title("Electricity Billing Management System — Admin")
        self.window.geometry("1360x830")
        self.window.minsize(1080, 640)

        theme.apply_theme(self.window)

        self.window.grid_columnconfigure(1, weight=1)
        self.window.grid_rowconfigure(0, weight=1)

        self.current_page_key = None
        self.current_page_widget = None

        # ---- Sidebar -------------------------------------------------
        self.sidebar = Sidebar(
            self.window,
            sections=NAV_SECTIONS,
            on_select=self.show_page,
            brand_title="VOLTGRID",
            brand_subtitle="ELECTRIC UTILITY",
        )
        self.sidebar.grid(row=0, column=0, sticky="ns")

        # ---- Right side (top bar + content) --------------------------
        right = tk.Frame(self.window, bg=COLORS["bg"])
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(1, weight=1)

        self.topbar = TopBar(
            right, user_label="Administrator", role_label="ADMIN ACCESS", on_logout=self.logout
        )
        self.topbar.grid(row=0, column=0, sticky="ew")

        self.content = tk.Frame(right, bg=COLORS["bg"])
        self.content.grid(row=1, column=0, sticky="nsew")
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

        self.window.protocol("WM_DELETE_WINDOW", self.logout)

        self.show_page("dashboard")

    # -----------------------------------------------------------------
    # Navigation
    # -----------------------------------------------------------------

    def show_page(self, key):
        if key not in PAGE_REGISTRY:
            return

        page_class, title, subtitle = PAGE_REGISTRY[key]

        if self.current_page_widget is not None:
            self.current_page_widget.destroy()

        self.current_page_key = key
        self.sidebar.set_active(key)
        self.topbar.set_title(title, subtitle)

        # Each page fetches fresh data from the database on creation,
        # so navigating to a section always shows up-to-date records.
        self.current_page_widget = page_class(self.content)
        self.current_page_widget.grid(row=0, column=0, sticky="nsew")

    def logout(self):
        confirm = messagebox.askyesno("Log Out", "Are you sure you want to log out?")
        if not confirm:
            return

        self.window.destroy()

        if self.on_logout:
            self.on_logout()
