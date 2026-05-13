import tkinter as tk
from tkinter import ttk, messagebox
import database

def run_app(purok_id, purok_name):
    root = tk.Tk()
    root.title(f"Residents of {purok_name}")
    root.geometry("700x400")

    # Input fields
    tk.Label(root, text="Name").grid(row=0, column=0, padx=5, pady=5)
    name_entry = tk.Entry(root)
    name_entry.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(root, text="Age").grid(row=1, column=0, padx=5, pady=5)
    age_entry = tk.Entry(root)
    age_entry.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(root, text="Contact").grid(row=2, column=0, padx=5, pady=5)
    contact_entry = tk.Entry(root)
    contact_entry.grid(row=2, column=1, padx=5, pady=5)

    # Resident table
    tree = ttk.Treeview(root, columns=("ID", "Name", "Age", "Contact"), show="headings")
    for col in ("ID", "Name", "Age", "Contact"):
        tree.heading(col, text=col)
        tree.column(col, width=150)
    tree.grid(row=5, column=0, columnspan=4, pady=10)

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
        name = name_entry.get().strip()
        age = age_entry.get().strip()
        contact = contact_entry.get().strip()
        if not name or not age or not contact:
            messagebox.showwarning("Error", "All fields are required.")
            return
        database.update_resident(resident_id, name, age, contact)
        messagebox.showinfo("Success", "Resident updated successfully!")
        refresh_table()

    def delete_resident():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Error", "Select a resident to delete.")
            return
        resident_id = tree.item(selected[0])["values"][0]
        database.delete_resident(resident_id)
        messagebox.showinfo("Success", "Resident deleted successfully!")
        refresh_table()

    # Buttons
    tk.Button(root, text="Add", command=add_resident).grid(row=3, column=0, padx=5, pady=5)
    tk.Button(root, text="Update", command=update_resident).grid(row=3, column=1, padx=5, pady=5)
    tk.Button(root, text="Delete", command=delete_resident).grid(row=3, column=2, padx=5, pady=5)

    refresh_table()
    root.mainloop()
