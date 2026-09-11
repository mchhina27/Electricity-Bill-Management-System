"""
Grievance Management page -- used by both Admin and Employee dashboards.

Calls services.grievance_service.get_all_grievances() /
update_grievance_status(), which are only ever wired into the Admin and
Employee shells (never the Customer dashboard), so a customer never gets
a code path to another customer's grievances.
"""

import tkinter as tk
from tkinter import ttk

from ui import theme
from ui.theme import COLORS
from ui import components
from ui.components import Card, PageHeader, InlineBanner, EmptyState

from services.grievance_service import get_all_grievances, update_grievance_status, VALID_STATUSES


TABLE_COLUMNS = ("grievance_id", "customer_name", "category", "related_bill_id", "status", "submitted_at")
TABLE_HEADINGS = {
    "grievance_id": "ID",
    "customer_name": "Customer",
    "category": "Category",
    "related_bill_id": "Bill ID",
    "status": "Status",
    "submitted_at": "Submitted",
}


class GrievanceManagementPage(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["bg"])

        self.selected_grievance = None
        self.all_grievances = []

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        container = tk.Frame(self, bg=COLORS["bg"])
        container.grid(row=0, column=0, sticky="nsew", padx=28, pady=22)
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(2, weight=1)

        PageHeader(
            container,
            "Grievances",
            "Review customer-submitted issues and update their status."
        ).grid(row=0, column=0, sticky="ew", pady=(0, 14))

        self.banner = InlineBanner(container)
        self.banner.place_in_grid(row=1, column=0)

        body = tk.Frame(container, bg=COLORS["bg"])
        body.grid(row=2, column=0, sticky="nsew")
        body.grid_columnconfigure(0, weight=2)
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(0, weight=1)

        self._build_table(body)
        self._build_detail(body)

        self.load_grievances()

    # -----------------------------------------------------------------
    def _build_table(self, parent):
        card = Card(parent, radius=10, padding=18)
        card.grid(row=0, column=0, sticky="nsew", padx=(0, 16))
        card.body.grid_columnconfigure(0, weight=1)
        card.body.grid_rowconfigure(1, weight=1)

        header_row = tk.Frame(card.body, bg=COLORS["surface"])
        header_row.grid(row=0, column=0, sticky="ew")
        header_row.grid_columnconfigure(0, weight=1)

        self.count_label = tk.Label(
            header_row, text="", font=theme.FONTS["h3"], bg=COLORS["surface"], fg=COLORS["text"]
        )
        self.count_label.grid(row=0, column=0, sticky="w")

        ttk.Button(
            header_row, text="Refresh", style="GhostOnSurface.TButton", command=self.load_grievances
        ).grid(row=0, column=1, sticky="e")

        tk.Frame(card.body, bg=COLORS["surface"], height=12).grid(row=1, column=0)
        table_wrap = tk.Frame(card.body, bg=COLORS["surface"])
        table_wrap.grid(row=2, column=0, sticky="nsew")
        card.body.grid_rowconfigure(2, weight=1)
        table_wrap.grid_columnconfigure(0, weight=1)
        table_wrap.grid_rowconfigure(0, weight=1)

        self.table = ttk.Treeview(table_wrap, columns=TABLE_COLUMNS, show="headings")
        for col in TABLE_COLUMNS:
            self.table.heading(col, text=TABLE_HEADINGS[col])
            self.table.column(col, width=120, anchor="center")
        self.table.column("customer_name", width=160, anchor="w")

        components.configure_row_tags(self.table)

        scrollbar = ttk.Scrollbar(table_wrap, orient=tk.VERTICAL, command=self.table.yview)
        self.table.configure(yscrollcommand=scrollbar.set)

        self.table.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.table.bind("<ButtonRelease-1>", self.select_grievance)

        self.empty_state_holder = tk.Frame(table_wrap, bg=COLORS["surface"])
        self.empty_state_holder.grid(row=0, column=0, sticky="nsew")
        self.empty_state_holder.grid_remove()

    # -----------------------------------------------------------------
    def _build_detail(self, parent):
        card = Card(parent, radius=10, padding=18)
        card.grid(row=0, column=1, sticky="nsew")

        tk.Label(
            card.body, text="GRIEVANCE DETAILS", font=theme.FONTS["h3"],
            bg=COLORS["surface"], fg=COLORS["text"]
        ).pack(anchor="w")
        tk.Label(
            card.body, text="Select a grievance from the list to review it.",
            font=theme.FONTS["small"], bg=COLORS["surface"], fg=COLORS["text_muted"], wraplength=280, justify="left"
        ).pack(anchor="w", pady=(2, 14))

        self.detail_frame = tk.Frame(card.body, bg=COLORS["surface_alt"])
        self.detail_label = tk.Label(
            self.detail_frame, text="No grievance selected.", font=theme.FONTS["small"],
            bg=COLORS["surface_alt"], fg=COLORS["text_muted"], justify="left", anchor="w",
            padx=12, pady=10, wraplength=280
        )
        self.detail_label.pack(fill="x")
        self.detail_frame.pack(fill="x", pady=(0, 14))

        theme.field_label(card.body, "Update Status").pack(anchor="w", pady=(0, 5))
        self.status_combo = theme.styled_combobox(card.body, VALID_STATUSES, width=24)
        self.status_combo.pack(anchor="w", fill="x", pady=(0, 12))

        theme.field_label(card.body, "Resolution / Response (optional)").pack(anchor="w", pady=(0, 5))
        self.resolution_text = tk.Text(
            card.body, height=5, font=theme.FONTS["body"], bg=COLORS["surface"], fg=COLORS["text"],
            relief="flat", highlightthickness=1, highlightbackground=COLORS["border_strong"],
            highlightcolor=COLORS["accent"], wrap="word"
        )
        self.resolution_text.pack(fill="x", pady=(0, 12))

        ttk.Button(
            card.body, text="Save Update", style="Primary.TButton", command=self.save_update
        ).pack(fill="x")

    # -----------------------------------------------------------------
    def load_grievances(self):
        self.selected_grievance = None
        self.detail_label.configure(text="No grievance selected.")

        for item in self.table.get_children():
            self.table.delete(item)

        self.all_grievances = get_all_grievances() or []
        self.count_label.configure(text=f"{len(self.all_grievances)} Grievance{'s' if len(self.all_grievances) != 1 else ''}")

        if not self.all_grievances:
            self.table.grid_remove()
            self.empty_state_holder.grid()
            for w in self.empty_state_holder.winfo_children():
                w.destroy()
            EmptyState(self.empty_state_holder, "No grievances", "Customer-submitted grievances will appear here.").pack(
                fill="both", expand=True
            )
            return

        self.empty_state_holder.grid_remove()
        self.table.grid()

        for i, g in enumerate(self.all_grievances):
            customer_name = f'{g.get("first_name", "")} {g.get("last_name", "")}'.strip()
            self.table.insert(
                "", tk.END,
                values=(
                    g["grievance_id"],
                    customer_name,
                    g["category"],
                    g.get("related_bill_id") or "—",
                    g["status"],
                    str(g.get("submitted_at") or ""),
                ),
                tags=components.row_tags(i, g.get("status")),
            )

    def select_grievance(self, _event):
        selected = self.table.focus()
        if not selected:
            return

        values = self.table.item(selected, "values")
        if not values:
            return

        grievance_id = values[0]
        grievance = next((g for g in self.all_grievances if str(g["grievance_id"]) == str(grievance_id)), None)
        if grievance is None:
            return

        self.selected_grievance = grievance
        self.banner.hide()

        customer_name = f'{grievance.get("first_name", "")} {grievance.get("last_name", "")}'.strip()
        self.detail_label.configure(
            text=(
                f'#{grievance["grievance_id"]}  \u00b7  {customer_name}  \u00b7  {grievance.get("email", "")}\n'
                f'Category: {grievance["category"]}\n'
                f'Related Bill: {grievance.get("related_bill_id") or "None"}\n\n'
                f'{grievance["description"]}'
            ),
            fg=COLORS["text"],
        )
        self.status_combo.set(grievance["status"])
        self.resolution_text.delete("1.0", tk.END)
        if grievance.get("resolution"):
            self.resolution_text.insert("1.0", grievance["resolution"])

    def save_update(self):
        if not self.selected_grievance:
            self.banner.show("Select a grievance from the list first.", kind="warning")
            return

        status = self.status_combo.get()
        resolution = self.resolution_text.get("1.0", tk.END).strip()

        success, message = update_grievance_status(
            self.selected_grievance["grievance_id"], status, resolution or None
        )

        if success:
            self.banner.show(message, kind="success")
            self.load_grievances()
        else:
            self.banner.show(message, kind="danger")
