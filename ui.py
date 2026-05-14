import tkinter as tk
from tkinter import ttk, messagebox
import database

def run_app(purok_id, purok_name):
    root = tk.Tk()
    root.title(f"Residents of {purok_name}")
    root.geometry("800x500")

    # Configure grid expansion
    for i in range(6):
        root.grid_rowconfigure(i, weight=1)
    for j in range(4):
        root.grid_columnconfigure(j, weight=1)

    tk.Label(root, text="Name").grid(row=0, column=0, sticky="e", padx=5, pady=5)
    name_entry = tk.Entry(root)
    name_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

    tk.Label(root, text="Age").grid(row=1, column=0, sticky="e", padx=5, pady=5)
    age_entry = tk.Entry(root)
    age_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

    tk.Label(root, text="Contact").grid(row=2, column=0, sticky="e", padx=5, pady=5)
    contact_entry = tk.Entry(root)
    contact_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

    tree = ttk.Treeview(root, columns=("ID", "Name", "Age", "Contact"), show="headings")
    for col in ("ID", "Name", "Age", "Contact"):
        tree.heading(col, text=col)
        tree.column(col, width=150)
    tree.grid(row=5, column=0, columnspan=4, sticky="nsew", padx=10, pady=10)

    def refresh_table():
        for row in tree.get_children():
            tree.delete(row)
        for resident in database.get_residents_by_purok(purok_id):
            tree.insert("", "end", values=resident)

    def add_resident():
        name = name_entry.get().strip()
        age = age_entry.get().strip()
        contact = contact_entry.get().strip()
        if not name or not age or not contact:
            messagebox.showwarning("Error", "All fields are required.")
            return
        database.add_resident(name, age, contact, purok_id)
        messagebox.showinfo("Success", "Resident added successfully!")
        refresh_table()

    def update_resident():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Error", "Select a resident to update.")
            return
        resident_id = tree.item(selected[0])["values"][0]