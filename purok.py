import tkinter as tk
from tkinter import ttk, messagebox
import database
import ui

def run_purok_window():
    database.create_purok_table()

    root = tk.Tk()
    root.title("Select Purok")
    root.geometry("500x400")

    # Configure grid expansion
    for i in range(5):
        root.grid_rowconfigure(i, weight=1)
    root.grid_columnconfigure(0, weight=1)

    # --- Table of Puroks with Scrollbar ---
    frame = tk.Frame(root)
    frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

    tree_scroll = tk.Scrollbar(frame)
    tree_scroll.pack(side="right", fill="y")

    tree = ttk.Treeview(frame, columns=("ID", "Name"), show="headings", yscrollcommand=tree_scroll.set)
    tree.heading("ID", text="ID")
    tree.heading("Name", text="Purok Name")
    tree.column("ID", width=50)
    tree.column("Name", width=300)
    tree.pack(fill="both", expand=True)

    tree_scroll.config(command=tree.yview)

    def refresh_puroks():
        for row in tree.get_children():
            tree.delete(row)
        for purok in database.get_puroks():
            tree.insert("", "end", values=purok)

    def add_purok(event=None):
        name = purok_entry.get().strip()
        if not name:
            messagebox.showwarning("Error", "Please enter a Purok name.")
            return
        database.add_purok(name)
        purok_entry.delete(0, tk.END)
        refresh_puroks()

    def open_residents(event=None):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Error", "Select a Purok first.")
            return
        purok_id = tree.item(selected[0])["values"][0]
        purok_name = tree.item(selected[0])["values"][1]
        root.destroy()
        ui.run_app(purok_id, purok_name)

    # --- Add Purok Section ---
    add_frame = tk.Frame(root)
    add_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)

    tk.Label(add_frame, text="➕ Add New Purok", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0,5))
    purok_entry = tk.Entry(add_frame)
    purok_entry.pack(fill="x", pady=5)
    purok_entry.bind("<Return>", add_purok)  # Enter adds Purok
    tk.Button(add_frame, text="Add Purok", command=add_purok).pack(fill="x", pady=5)

    # --- Open Residents Button ---
    tk.Button(root, text="Open Residents", command=open_residents).grid(row=2, column=0, sticky="ew", padx=10, pady=5)

    # Keyboard shortcut: Enter on selected row opens residents
    tree.bind("<Return>", open_residents)

    refresh_puroks()
    root.mainloop()
