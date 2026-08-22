import tkinter as tk
from tkinter import messagebox

from services.auth import login
from ui.admin_dashboard import AdminDashboard
from ui.customer_dashboard import CustomerDashboard


def attempt_login():
    username = username_entry.get().strip()
    password = password_entry.get()

    if not username or not password:
        messagebox.showwarning(
            "Missing Information",
            "Please enter both username and password."
        )
        return

    user = login(username, password)

    if user:
        # Clear login fields
        username_entry.delete(0, tk.END)
        password_entry.delete(0, tk.END)

        # Open dashboard according to user's role
        if user["role"] == "ADMIN":
            AdminDashboard()

        elif user["role"] == "CUSTOMER":
            CustomerDashboard(user["username"])

        else:
            messagebox.showerror(
                "Error",
                "Unknown user role."
            )

    else:
        messagebox.showerror(
            "Login Failed",
            "Invalid username or password."
        )


# -----------------------------------------
# Main Window
# -----------------------------------------

root = tk.Tk()

root.title("Electricity Bill Management System")
root.geometry("500x350")
root.resizable(False, False)


# -----------------------------------------
# Title
# -----------------------------------------

title_label = tk.Label(
    root,
    text="Electricity Bill Management System",
    font=("Arial", 18, "bold")
)

title_label.pack(pady=30)


# -----------------------------------------
# Username
# -----------------------------------------

username_label = tk.Label(
    root,
    text="Username",
    font=("Arial", 11)
)

username_label.pack()

username_entry = tk.Entry(
    root,
    width=30,
    font=("Arial", 11)
)

username_entry.pack(pady=8)


# -----------------------------------------
# Password
# -----------------------------------------

password_label = tk.Label(
    root,
    text="Password",
    font=("Arial", 11)
)

password_label.pack()

password_entry = tk.Entry(
    root,
    width=30,
    font=("Arial", 11),
    show="*"
)

password_entry.pack(pady=8)


# -----------------------------------------
# Login Button
# -----------------------------------------

login_button = tk.Button(
    root,
    text="Login",
    width=15,
    font=("Arial", 11, "bold"),
    command=attempt_login
)

login_button.pack(pady=20)


# -----------------------------------------
# Start Application
# -----------------------------------------

root.mainloop()