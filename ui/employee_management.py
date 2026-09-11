"""
Employee account management -- Admin only (never wired into the Employee
or Customer shells).
"""

import tkinter as tk
from tkinter import ttk, messagebox

from ui import theme
from ui.theme import COLORS
from ui import components
from ui.components import Card, PageHeader, InlineBanner, EmptyState

from services.employee_service import get_all_employees, add_employee, delete_employee


TABLE_COLUMNS = ("user_id", "username", "employee_name", "created_at")
TABLE_HEADINGS = {
    "user_id": "User ID",
    "username": "Username",
    "employee_name": "Name",
    "created_at": "Created",
}


class EmployeeManagementPage(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["bg"])

        self.selected_user_id = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        container = tk.Frame(self, bg=COLORS["bg"])
        container.grid(row=0, column=0, sticky="nsew", padx=28, pady=22)
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(2, weight=1)

        PageHeader(
            container,
            "Employee Accounts",
            "Create staff login accounts. Employees can manage customers, "
            "meters, bills, payments and grievances, but not tariffs or other staff."
        ).grid(row=0, column=0, sticky="ew", pady=(0, 14))

        self.banner = InlineBanner(container)
        self.banner.place_in_grid(row=1, column=0)

        body = tk.Frame(container, bg=COLORS["bg"])
        body.grid(row=2, column=0, sticky="nsew")
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(0, weight=1)

        self._build_form(body)
        self._build_table(body)

        self.load_employees()

    def _build_form(self, parent):
        card = Card(parent, radius=10, padding=18)
        card.grid(row=0, column=0, sticky="ns", padx=(0, 16))

        tk.Label(
            card.body, text="NEW EMPLOYEE", font=theme.FONTS["h3"], bg=COLORS["surface"], fg=COLORS["text"]
        ).pack(anchor="w")
        tk.Label(
            card.body, text="A temporary password is generated and shown once.",
            font=theme.FONTS["small"], bg=COLORS["surface"], fg=COLORS["text_muted"], wraplength=280, justify="left"
        ).pack(anchor="w", pady=(2, 14))

        grid = tk.Frame(card.body, bg=COLORS["surface"])
        grid.pack(fill="x")
        grid.grid_columnconfigure(0, weight=1)

        self.name_entry = components.form_field(grid, 0, 0, "Full Name", lambda p: theme.styled_entry(p, width=24))
        self.username_entry = components.form_field(
            grid, 1, 0, "Username (for login)", lambda p: theme.styled_entry(p, width=24)
        )

        ttk.Button(
            card.body, text="Create Employee", style="Primary.TButton", command=self.add_employee
        ).pack(fill="x", pady=(8, 6))
        ttk.Button(
            card.body, text="Remove Selected", style="Destructive.TButton", command=self.delete_employee
        ).pack(fill="x")

    def _build_table(self, parent):
        card = Card(parent, radius=10, padding=18)
        card.grid(row=0, column=1, sticky="nsew")
        card.body.grid_columnconfigure(0, weight=1)
        card.body.grid_rowconfigure(1, weight=1)

        tk.Label(
            card.body, text="ALL EMPLOYEES", font=theme.FONTS["h3"], bg=COLORS["surface"], fg=COLORS["text"]
        ).grid(row=0, column=0, sticky="w", pady=(0, 12))

        table_wrap = tk.Frame(card.body, bg=COLORS["surface"])
        table_wrap.grid(row=1, column=0, sticky="nsew")
        table_wrap.grid_columnconfigure(0, weight=1)
        table_wrap.grid_rowconfigure(0, weight=1)

        self.table = ttk.Treeview(table_wrap, columns=TABLE_COLUMNS, show="headings")
        for col in TABLE_COLUMNS:
            self.table.heading(col, text=TABLE_HEADINGS[col])
            self.table.column(col, width=140, anchor="center")

        components.configure_row_tags(self.table)

        scrollbar = ttk.Scrollbar(table_wrap, orient=tk.VERTICAL, command=self.table.yview)
        self.table.configure(yscrollcommand=scrollbar.set)

        self.table.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.table.bind("<ButtonRelease-1>", self.select_employee)

        self.empty_state_holder = tk.Frame(table_wrap, bg=COLORS["surface"])
        self.empty_state_holder.grid(row=0, column=0, sticky="nsew")
        self.empty_state_holder.grid_remove()

    def load_employees(self):
        self.selected_user_id = None

        for item in self.table.get_children():
            self.table.delete(item)

        employees = get_all_employees() or []

        if not employees:
            self.table.grid_remove()
            self.empty_state_holder.grid()
            for w in self.empty_state_holder.winfo_children():
                w.destroy()
            EmptyState(self.empty_state_holder, "No employee accounts yet", "Create one using the form.").pack(
                fill="both", expand=True
            )
            return

        self.empty_state_holder.grid_remove()
        self.table.grid()

        for i, emp in enumerate(employees):
            self.table.insert(
                "", tk.END,
                values=(emp["user_id"], emp["username"], emp["employee_name"], str(emp.get("created_at") or "")),
                tags=components.row_tags(i),
            )

    def select_employee(self, _event):
        selected = self.table.focus()
        if not selected:
            return
        values = self.table.item(selected, "values")
        if not values:
            return
        self.selected_user_id = values[0]

    def add_employee(self):
        name = self.name_entry.get().strip()
        username = self.username_entry.get().strip()

        if not name or not username:
            self.banner.show("Enter both a name and a username.", kind="warning")
            return

        success, message = add_employee(username, name)

        if success:
            self.banner.show(message, kind="success")
            self.name_entry.delete(0, tk.END)
            self.username_entry.delete(0, tk.END)
            self.load_employees()
        else:
            self.banner.show(message, kind="danger")

    def delete_employee(self):
        if self.selected_user_id is None:
            self.banner.show("Select an employee from the table first.", kind="warning")
            return

        confirm = messagebox.askyesno(
            "Confirm Removal", "Remove this employee account? They will no longer be able to log in."
        )
        if not confirm:
            return

        success, message = delete_employee(self.selected_user_id)

        if success:
            self.banner.show(message, kind="success")
            self.load_employees()
        else:
            self.banner.show(message, kind="danger")
