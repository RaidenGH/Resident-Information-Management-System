import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import users_database as database
from purok import run_purok_window
import register

def run_login():
    database.create_users_table()

    root = tk.Tk()
    root.title("Member Login")
    root.geometry("420x420")
    root.resizable(False, False)

    # --- Gradient Background ---
    gradient = tk.Canvas(root, width=420, height=420, highlightthickness=0)
    gradient.pack(fill="both", expand=True)

    # Create vertical gradient (blue to cyan)
    for i in range(420):
        r = 0
        g = int(150 + (i / 420) * 105)
        b = 255
        color = f"#{r:02x}{g:02x}{b:02x}"
        gradient.create_line(0, i, 420, i, fill=color)

    # --- Logo (HCDC) ---
    try:
        logo_img = Image.open("hcdc_logo.png")
        logo_img = logo_img.resize((80, 80), Image.LANCZOS)
        logo = ImageTk.PhotoImage(logo_img)
        gradient.create_image(210, 70, image=logo)
    except Exception:
        gradient.create_text(210, 70, text="👥", font=("Arial", 40), fill="white")

    # --- Entry Fields ---
    entry_bg = "#ffffff"
    entry_fg = "#000000"

    # Username field
    username_frame = tk.Frame(root, bg="white", highlightbackground="white", highlightthickness=2)
    username_frame.place(x=80, y=150, width=260, height=35)
    tk.Label(username_frame, text="👤", bg="white", fg="#0099ff", font=("Arial", 12)).place(x=5, y=6)
    username_entry = tk.Entry(username_frame, bg="white", fg="black", font=("Poppins", 10), relief="flat")
    username_entry.place(x=35, y=6, width=210)

    # Password field
    password_frame = tk.Frame(root, bg="white", highlightbackground="white", highlightthickness=2)
    password_frame.place(x=80, y=200, width=260, height=35)
    tk.Label(password_frame, text="🔒", bg="white", fg="#0099ff", font=("Arial", 12)).place(x=5, y=6)
    password_entry = tk.Entry(password_frame, bg="white", fg="black", font=("Poppins", 10), show="*", relief="flat")
    password_entry.place(x=35, y=6, width=210)

    # --- Buttons ---
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

    # Login button with hover effect
    login_btn = tk.Button(root, text="Login Now", command=login,
                          bg="#ffcc00", fg="#000000", font=("Poppins", 11, "bold"),
                          relief="flat", bd=0)
    login_btn.place(x=80, y=260, width=260, height=35)

    def on_hover_login(e): login_btn.config(bg="#ffdd33")
    def on_leave_login(e): login_btn.config(bg="#ffcc00")
    login_btn.bind("<Enter>", on_hover_login)
    login_btn.bind("<Leave>", on_leave_login)

    # --- Footer: "Not a member?" above "Create Account" ---
    footer_frame = tk.Frame(root, bg="#00aaff")
    footer_frame.place(x=0, y=330, width=420, height=70)

    tk.Label(footer_frame, text="Not a member?", font=("Poppins", 9),
             fg="white", bg="#00aaff").pack(pady=(10, 0))

    create_btn = tk.Button(footer_frame, text="Create account", command=open_register,
                           bg="#00aaff", fg="white", font=("Poppins", 9, "bold"),
                           relief="flat", bd=0, cursor="hand2")
    create_btn.pack(pady=(5, 0))

    def on_hover_create(e): create_btn.config(bg="#00ccff")
    def on_leave_create(e): create_btn.config(bg="#00aaff")
    create_btn.bind("<Enter>", on_hover_create)
    create_btn.bind("<Leave>", on_leave_create)

    password_entry.bind("<Return>", login)
    root.mainloop()
