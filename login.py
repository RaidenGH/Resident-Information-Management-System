import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk  # Pillow for HD image scaling
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
    for j in range(3):
        root.grid_columnconfigure(j, weight=1)

    # --- HD Logo beside fields ---
    try:
        # Load and resize logo with Pillow for crisp quality
        logo_img = Image.open("hcdc_logo.png")  # place your logo file in same folder
        logo_img = logo_img.resize((80, 80), Image.LANCZOS)  # adjust size as needed
        logo = ImageTk.PhotoImage(logo_img)

        logo_label = tk.Label(root, image=logo)
        logo_label.image = logo  # keep reference
        logo_label.grid(row=0, column=0, rowspan=3, sticky="n", padx=10, pady=10)
    except Exception:
        logo_label = tk.Label(root, text="🏠", font=("Arial", 20))
        logo_label.grid(row=0, column=0, rowspan=3, sticky="n", padx=10, pady=10)

    # --- Username and Password fields ---
    tk.Label(root, text="Username").grid(row=0, column=1, sticky="e", padx=5, pady=5)
    username_entry = tk.Entry(root)
    username_entry.grid(row=0, column=2, sticky="ew", padx=5, pady=5)

    tk.Label(root, text="Password").grid(row=1, column=1, sticky="e", padx=5, pady=5)
    password_entry = tk.Entry(root, show="*")
    password_entry.grid(row=1, column=2, sticky="ew", padx=5, pady=5)

    def login(event=None):
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

    # --- Buttons ---
    tk.Button(root, text="Login", command=login).grid(row=2, column=1, columnspan=2, sticky="ew", padx=5, pady=5)
    tk.Button(root, text="Create Account", command=open_register).grid(row=3, column=1, columnspan=2, sticky="ew", padx=5, pady=5)

    # --- Keyboard Shortcut ---
    password_entry.bind("<Return>", login)

    root.mainloop()
