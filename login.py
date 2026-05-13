import tkinter as tk
from tkinter import messagebox
import database
from purok import run_purok_window

def run_login():
    database.create_tables()
    database.create_purok_table()

    root = tk.Tk()
    root.title("Login - Resident Information System")
    root.geometry("300x220")

    tk.Label(root, text="Username").pack(pady=5)
    username_entry = tk.Entry(root)
    username_entry.pack()

    tk.Label(root, text="Password").pack(pady=5)
    password_entry = tk.Entry(root, show="*")
    password_entry.pack()

    def login():
        username = username_entry.get().strip()
        password = password_entry.get().strip()
        if not username or not password:
            messagebox.showwarning("Error", "Please fill in both fields.")
            return

        if database.validate_login(username, password):
            messagebox.showinfo("Login Successful", f"Welcome, {username}!")
            root.destroy()
            run_purok_window()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    def register():
        username = username_entry.get().strip()
        password = password_entry.get().strip()
        if not username or not password:
            messagebox.showwarning("Error", "Please fill in both fields.")
            return
        try:
            database.add_user(username, password)
            messagebox.showinfo("Success", "Account created successfully!")
        except Exception:
            messagebox.showerror("Error", "Username already exists.")

    tk.Button(root, text="Login", command=login).pack(pady=10)
    tk.Button(root, text="Register", command=register).pack()

    root.mainloop()
