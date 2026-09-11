"""
Application entry point: login screen + role-based routing into the
Admin shell or the Customer portal.

Still uses the same authentication call with the same arguments:
    services.auth.login(username, password)
"""

import tkinter as tk
from tkinter import ttk

from services.auth import login
from ui import theme
from ui.theme import COLORS
from ui.components import Card
from ui.admin_dashboard import AdminDashboard
from ui.employee_dashboard import EmployeeDashboard
from ui.customer_dashboard import CustomerDashboard


# -----------------------------------------------------------------------
# Main window (login screen)
# -----------------------------------------------------------------------

root = tk.Tk()
root.title("Electricity Billing Management System")
root.geometry("480x560")
root.resizable(False, False)

theme.apply_theme(root)
root.configure(bg=COLORS["bg"])


def show_login_error(message):
    error_label.configure(text=message)


def clear_login_error():
    error_label.configure(text="")


def return_to_login():
    """Called when a dashboard logs the user out."""
    username_entry.delete(0, tk.END)
    password_entry.delete(0, tk.END)
    clear_login_error()
    root.deiconify()


def attempt_login():
    username = username_entry.get().strip()
    password = password_entry.get()

    if not username or not password:
        show_login_error("Please enter both username and password.")
        return

    user = login(username, password)

    if not user:
        show_login_error("Invalid username or password.")
        return

    clear_login_error()
    username_entry.delete(0, tk.END)
    password_entry.delete(0, tk.END)

    role = user["role"]

    # Hide the login window while a dashboard is open; it reappears via
    # return_to_login() when the user logs out.
    root.withdraw()

    if role == "ADMIN":
        AdminDashboard(on_logout=return_to_login)
    elif role == "EMPLOYEE":
        EmployeeDashboard(employee_name=user.get("employee_name"), on_logout=return_to_login)
    elif role == "CUSTOMER":
        if not user.get("customer_id"):
            root.deiconify()
            show_login_error("This customer account isn't linked to a customer record. Contact an administrator.")
            return
        CustomerDashboard(user["customer_id"], on_logout=return_to_login)
    else:
        root.deiconify()
        show_login_error("Unknown user role.")


# -----------------------------------------------------------------------
# Layout
# -----------------------------------------------------------------------

wrapper = tk.Frame(root, bg=COLORS["bg"])
wrapper.pack(fill="both", expand=True)

card_holder = tk.Frame(wrapper, bg=COLORS["bg"])
card_holder.place(relx=0.5, rely=0.5, anchor="center")

# ---- Brand header --------------------------------------------------
tk.Label(
    card_holder, text="VOLTGRID", font=theme.FONTS["h1"], bg=COLORS["bg"], fg=COLORS["text"]
).pack(pady=(0, 2))
tk.Label(
    card_holder, text="ELECTRIC UTILITY  \u00b7  BILLING PORTAL", font=theme.FONTS["small_bold"],
    bg=COLORS["bg"], fg=COLORS["accent_dark"]
).pack()
tk.Frame(card_holder, bg=COLORS["accent"], height=2, width=64).pack(pady=(10, 24))

# ---- Login card ------------------------------------------------------
login_card = Card(card_holder, radius=12, padding=28, outer_bg=COLORS["bg"])
login_card.pack()

tk.Label(
    login_card.body, text="Sign In", font=theme.FONTS["h2"], bg=COLORS["surface"], fg=COLORS["text"]
).pack(anchor="w")
tk.Label(
    login_card.body, text="Enter your credentials to continue", font=theme.FONTS["small"],
    bg=COLORS["surface"], fg=COLORS["text_muted"]
).pack(anchor="w", pady=(2, 18))

theme.field_label(login_card.body, "Username").pack(anchor="w", pady=(0, 5))
username_entry = theme.styled_entry(login_card.body, width=32)
username_entry.pack(fill="x", pady=(0, 14), ipady=4)

theme.field_label(login_card.body, "Password").pack(anchor="w", pady=(0, 5))
password_entry = theme.styled_entry(login_card.body, width=32, show="*")
password_entry.pack(fill="x", pady=(0, 6), ipady=4)

error_label = tk.Label(
    login_card.body, text="", font=theme.FONTS["small_bold"], bg=COLORS["surface"],
    fg=COLORS["danger"], anchor="w", wraplength=300, justify="left"
)
error_label.pack(anchor="w", pady=(2, 12))

ttk.Button(
    login_card.body, text="Log In", style="Primary.TButton", command=attempt_login
).pack(fill="x", ipady=2)

password_entry.bind("<Return>", lambda _event: attempt_login())
username_entry.bind("<Return>", lambda _event: password_entry.focus_set())

tk.Label(
    card_holder, text="Admin and customer accounts both sign in here.", font=theme.FONTS["small"],
    bg=COLORS["bg"], fg=COLORS["text_faint"]
).pack(pady=(18, 0))


# -----------------------------------------------------------------------
# Start application
# -----------------------------------------------------------------------

if __name__ == "__main__":
    root.mainloop()
