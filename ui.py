import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import database
import csv

def run_app(purok_id, purok_name):
    root = tk.Tk()
    root.title(f"Residents of {purok_name}")
    root.geometry("900x600")

    # Configure grid expansion
    for i in range(8):
        root.grid_rowconfigure(i, weight=1)
    for j in range(4):
        root.grid_columnconfigure(j, weight=1)

    # Input fields
    tk.Label(root, text="Name").grid(row=0, column=0, sticky="e", padx=5, pady=5)
    name_entry = tk.Entry(root)
    name_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

    tk.Label(root, text="Age").grid(row=1, column=0, sticky="e", padx=5, pady=5)
    age_entry = tk.Entry(root)
    age_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

    tk.Label(root, text="Contact").grid(row=2, column=0, sticky="e", padx=5, pady=5)
    contact_entry = tk.Entry(root)
    contact_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

    # Resident table with scrollbar
    frame = tk.Frame(root)
    frame.grid(row=5, column=0, columnspan=4, sticky="nsew", padx=10, pady=10)

    tree_scroll = tk.Scrollbar(frame)
    tree_scroll.pack(side="right", fill="y")

    tree = ttk.Treeview(frame, columns=("ID", "Name", "Age", "Contact"), show="headings", yscrollcommand=tree_scroll.set)
    for col in ("ID", "Name", "Age", "Contact"):
        tree.heading(col, text=col)
        tree.column(col, width=200)
    tree.pack(fill="both", expand=True)

    tree_scroll.config(command=tree.yview)

    # Functions
    def refresh_table():
        for row in tree.get_children():
            tree.delete(row)
        residents = database.get_residents_by_purok(purok_id)
        # Sort by last name
        residents.sort(key=lambda r: r[1].split()[-1].lower())
        for resident in residents:
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

    def export_residents():
        filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files","*.csv")])
        if not filename:
            return
        residents = database.get_residents_by_purok(purok_id)
        with open(filename, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["ID", "Name", "Age", "Contact"])
            writer.writerows(residents)
        messagebox.showinfo("Export", f"Residents exported to {filename}")

    def import_residents():
        filename = filedialog.askopenfilename(filetypes=[("CSV files","*.csv")])
        if not filename:
            return
        with open(filename, "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                database.add_resident(row["Name"], row["Age"], row["Contact"], purok_id)
        messagebox.showinfo("Import", f"Residents imported from {filename}")
        refresh_table()

    # Buttons
    tk.Button(root, text="Add", command=add_resident).grid(row=3, column=0, sticky="ew", padx=5, pady=5)
    tk.Button(root, text="Update", command=update_resident).grid(row=3, column=1, sticky="ew", padx=5, pady=5)
    tk.Button(root, text="Delete", command=delete_resident).grid(row=3, column=2, sticky="ew", padx=5, pady=5)
    tk.Button(root, text="Export CSV", command=export_residents).grid(row=4, column=0, sticky="ew", padx=5, pady=5)
    tk.Button(root, text="Import CSV", command=import_residents).grid(row=4, column=1, sticky="ew", padx=5, pady=5)

    refresh_table()
    root.mainloop()
