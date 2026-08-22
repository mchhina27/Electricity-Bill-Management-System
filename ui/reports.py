import tkinter as tk
from services.report_service import get_dashboard_statistics


class Reports:

    def __init__(self):

        self.window = tk.Toplevel()

        self.window.title("Reports and Statistics")
        self.window.geometry("600x500")

        tk.Label(
            self.window,
            text="REPORTS AND STATISTICS",
            font=("Arial", 20, "bold")
        ).pack(pady=25)

        self.stats_frame = tk.Frame(self.window)
        self.stats_frame.pack(pady=20)

        tk.Button(
            self.window,
            text="Refresh Statistics",
            width=25,
            command=self.load_statistics
        ).pack(pady=20)

        self.load_statistics()


    def load_statistics(self):

        for widget in self.stats_frame.winfo_children():
            widget.destroy()

        stats = get_dashboard_statistics()

        data = [
            ("Total Customers", stats.get("total_customers", 0)),
            ("Total Meters", stats.get("total_meters", 0)),
            ("Total Bills", stats.get("total_bills", 0)),
            ("Total Billed Amount", f"₹{stats.get('total_billed', 0)}"),
            ("Total Collected", f"₹{stats.get('total_collected', 0)}"),
            ("Unpaid Bills", stats.get("unpaid_bills", 0))
        ]

        for label, value in data:

            row = tk.Frame(self.stats_frame)
            row.pack(fill=tk.X, pady=5)

            tk.Label(
                row,
                text=label,
                font=("Arial", 12),
                width=25,
                anchor="w"
            ).pack(side=tk.LEFT)

            tk.Label(
                row,
                text=value,
                font=("Arial", 12, "bold"),
                width=20,
                anchor="w"
            ).pack(side=tk.LEFT)