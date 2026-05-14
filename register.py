import tkinter as tk
from tkinter import messagebox
import users_database

def run_register(return_to_login):
    users_database.create_users_table()

    root = tk.Tk()
    root.title("Create Account")
    root.geometry("400x400")

    # Configure grid expansion
    for i in range(8):
        root.grid_rowconfigure(i, weight=1)
    for j in range(2):
        root.grid_columnconfigure(j, weight=1)

    labels = ["First Name", "Last Name", "Email", "Phone", "Username", "Password"]
    entries = {}

    for idx, label in enumerate(labels):
        tk.Label(root, text=label).grid(row=idx, column=0, sticky="e", padx=5, pady=5)
        entry = tk.Entry(root, show="*" if label == "Password" else "")
        entry.grid(row=idx, column=1, sticky="ew", padx=5, pady=5)
        entries[label] = entry

    def create_account():
        first_name = entries["First Name"].get().strip()
        last_name = entries["Last Name"].get().strip()
        email = entries["Email"].get().strip()
        phone = entries["Phone"].get().strip()
        username = entries["Username"].get().strip()
        password = entries["Password"].get().strip()

        if not all([first_name, last_name, email, phone, username, password]):
            messagebox.showwarning("Error", "All fields are required.")
            return

        try:
            users_database.add_user(username, password, first_name, last_name, email, phone)
            messagebox.showinfo("Success", "Account created successfully!")
            root.destroy()
            return_to_login()
        except Exception:
            messagebox.showerror("Error", "Username already exists.")

    def go_back():
        root.destroy()
        return_to_login()

    tk.Button(root, text="Create Account", command=create_account).grid(row=6, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
    tk.Button(root, text="Back", command=go_back).grid(row=7, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

    root.mainloop()
