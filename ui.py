import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import database
import csv
import purok

def run_app(purok_id, purok_name):
    root = tk.Tk()
    root.title(f"Residents of {purok_name}")
    root.geometry("900x600")

    # Configure grid expansion
    for i in range(8):
        root.grid_rowconfigure(i, weight=1)
    for j in range(5):
        root.grid_columnconfigure(j, weight=1)

    # Input fields
    tk.Label(root, text="First Name").grid(row=0, column=0, sticky="e", padx=5, pady=5)
    first_name_entry = tk.Entry(root)
    first_name_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

    tk.Label(root, text="Last Name").grid(row=1, column=0, sticky="e", padx=5, pady=5)
    last_name_entry = tk.Entry(root)
    last_name_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

    tk.Label(root, text="Age").grid(row=2, column=0, sticky="e", padx=5, pady=5)
    age_entry = tk.Entry(root)
    age_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

    tk.Label(root, text="Contact").grid(row=3, column=0, sticky="e", padx=5, pady=5)
    contact_entry = tk.Entry(root)
    contact_entry.grid(row=3, column=1, sticky="ew", padx=5, pady=5)

    # Resident table with scrollbar
    frame = tk.Frame(root)
    frame.grid(row=6, column=0, columnspan=5, sticky="nsew", padx=10, pady=10)

    tree_scroll = tk.Scrollbar(frame)
    tree_scroll.pack(side="right", fill="y")

    tree = ttk.Treeview(frame, columns=("ID", "First Name", "Last Name", "Age", "Contact"), show="headings", yscrollcommand=tree_scroll.set)
    for col in ("ID", "First Name", "Last Name", "Age", "Contact"):
        tree.heading(col, text=col)
        tree.column(col, width=150)
    tree.pack(fill="both", expand=True)

    tree_scroll.config(command=tree.yview)

    # Functions
    def refresh_table():
        for row in tree.get_children():
            tree.delete(row)
        residents = database.get_residents_by_purok(purok_id)
        residents.sort(key=lambda r: r[2].lower())  # sort by last_name
        for resident in residents:
            tree.insert("", "end", values=resident)

    def add_resident(event=None):
        first_name = first_name_entry.get().strip()
        last_name = last_name_entry.get().strip()
        age = age_entry.get().strip()
        contact = contact_entry.get().strip()
        if not first_name or not last_name or not age or not contact:
            messagebox.showwarning("Error", "All fields are required.")
            return
        database.add_resident(first_name, last_name, age, contact, purok_id)
        messagebox.showinfo("Success", "Resident added successfully!")
        refresh_table()

    def update_resident(event=None):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Error", "Select a resident to update.")
            return
        resident_id = tree.item(selected[0])["values"][0]
        first_name = first_name_entry.get().strip()
        last_name = last_name_entry.get().strip()
        age = age_entry.get().strip()
        contact = contact_entry.get().strip()
        if not first_name or not last_name or not age or not contact:
            messagebox.showwarning("Error", "All fields are required.")
            return
        database.update_resident(resident_id, first_name, last_name, age, contact)
        messagebox.showinfo("Success", "Resident updated successfully!")
        refresh_table()

    def delete_resident(event=None):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Error", "Select a resident to delete.")
            return
        resident_id = tree.item(selected[0])["values"][0]
        database.delete_resident(resident_id)
        messagebox.showinfo("Success", "Resident deleted successfully!")
        refresh_table()

    def go_back():
        root.destroy()
        purok.run_purok_window()

    # Double-click feature → load resident details into form
    def load_selected(event=None):
        selected = tree.selection()
        if not selected:
            return
        resident = tree.item(selected[0])["values"]
        first_name_entry.delete(0, tk.END)
        first_name_entry.insert(0, resident[1])
        last_name_entry.delete(0, tk.END)
        last_name_entry.insert(0, resident[2])
        age_entry.delete(0, tk.END)
        age_entry.insert(0, resident[3])
        contact_entry.delete(0, tk.END)
        contact_entry.insert(0, resident[4])

    tree.bind("<Double-1>", load_selected)

    # Context menu (right-click)
    menu = tk.Menu(root, tearoff=0)
    menu.add_command(label="Edit", command=update_resident)
    menu.add_command(label="Delete", command=delete_resident)

    def show_context_menu(event):
        selected = tree.identify_row(event.y)
        if selected:
            tree.selection_set(selected)
            menu.post(event.x_root, event.y_root)

    tree.bind("<Button-3>", show_context_menu)  # right-click

    # Buttons
    tk.Button(root, text="Add", command=add_resident).grid(row=4, column=0, sticky="ew", padx=5, pady=5)
    tk.Button(root, text="Update", command=update_resident).grid(row=4, column=1, sticky="ew", padx=5, pady=5)
    tk.Button(root, text="Delete", command=delete_resident).grid(row=4, column=2, sticky="ew", padx=5, pady=5)
    tk.Button(root, text="Back", command=go_back).grid(row=4, column=3, sticky="ew", padx=5, pady=5)

    # Keyboard bindings
    contact_entry.bind("<Return>", add_resident)  # Enter adds resident
    root.bind("<Delete>", delete_resident)       # Delete key removes resident
    root.bind("<Control-e>", update_resident)    # Ctrl+E edits

    refresh_table()
    root.mainloop()
