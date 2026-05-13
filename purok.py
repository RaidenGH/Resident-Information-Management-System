import tkinter as tk
from tkinter import ttk, messagebox
import database
import ui

def run_purok_window():
    database.create_purok_table()

    root = tk.Tk()
    root.title("Select Purok")
    root.geometry("400x300")

    tree = ttk.Treeview(root, columns=("ID", "Name"), show="headings")
    tree.heading("ID", text="ID")
    tree.heading("Name", text="Purok Name")
    tree.pack(pady=10)

    def refresh_puroks():
        for row in tree.get_children():
            tree.delete(row)
        for purok in database.get_puroks():
            tree.insert("", "end", values=purok)

    def add_purok():
        name = purok_entry.get().strip()
        if not name:
            messagebox.showwarning("Error", "Please enter a Purok name.")
            return
        database.add_purok(name)
        refresh_puroks()

    def open_residents():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Error", "Select a Purok first.")
            return
        purok_id = tree.item(selected[0])["values"][0]
        purok_name = tree.item(selected[0])["values"][1]
        root.destroy()
        ui.run_app(purok_id, purok_name)

    purok_entry = tk.Entry(root)
    purok_entry.pack(pady=5)
    tk.Button(root, text="Add Purok", command=add_purok).pack(pady=5)
    tk.Button(root, text="Open Residents", command=open_residents).pack(pady=5)

    refresh_puroks()
    root.mainloop()
