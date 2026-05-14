import tkinter as tk
from tkinter import messagebox
import users_database as database
from purok import run_purok_window
import register

def run_login():
    database.create_users_table()

    root = tk.Tk()
    root.title("Login - Resident Information System")
    root.geometry("400x250")

    # Configure grid expansion
    for i in range(4):
        root.grid_rowconfigure(i, weight=1)
    for j in range(2):
        root.grid_columnconfigure(j, weight=1)

    tk.Label(root, text="Username").grid(row=0, column=0, sticky="e", padx=5, pady=5)
    username_entry = tk.Entry(root)
    username_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

    tk.Label(root, text="Password").grid(row=1, column=0, sticky="e", padx=5, pady=5)
    password_entry = tk.Entry(root, show="*")
    password_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

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

    def open_register():
        root.destroy()
        register.run_register(run_login)

    tk.Button(root, text="Login", command=login).grid(row=2, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
    tk.Button(root, text="Create Account", command=open_register).grid(row=3, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

    root.mainloop()
