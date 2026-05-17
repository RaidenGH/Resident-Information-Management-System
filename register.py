import tkinter as tk
from tkinter import messagebox
import users_database


def run_register(return_to_login):
    users_database.create_users_table()

    # ── Palette ──────────────────────────────────────────────────────────────
    BG        = "#0d0f14"   # near-black canvas
    CARD      = "#13161e"   # card surface
    PANEL     = "#1a1e2b"   # input background
    BORDER    = "#2a2f42"   # subtle divider
    ACCENT    = "#4f8ef7"   # electric blue
    ACCENT2   = "#7c5cfc"   # violet secondary
    TEXT      = "#e8ecf4"   # primary text
    MUTED     = "#6b7490"   # secondary text
    SUCCESS   = "#4fc97e"   # green confirm
    DANGER    = "#f74f6a"   # error red

    # ── Root window ──────────────────────────────────────────────────────────
    root = tk.Tk()
    root.title("Create Account")
    root.configure(bg=BG)
    root.geometry("460x660")
    root.minsize(420, 580)
    root.resizable(True, True)

    # Center window on screen
    root.update_idletasks()
    x = (root.winfo_screenwidth() - 460) // 2
    y = (root.winfo_screenheight() - 660) // 2
    root.geometry(f"460x660+{x}+{y}")

    # ── Scrollable canvas ────────────────────────────────────────────────────
    canvas = tk.Canvas(root, bg=BG, highlightthickness=0)
    scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview,
                             troughcolor=BG, bg=BORDER, relief="flat",
                             width=6, highlightthickness=0)
    scroll_frame = tk.Frame(canvas, bg=BG)

    scroll_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    window_id = canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    # Stretch scroll_frame to match canvas width whenever window resizes
    def _on_canvas_resize(event):
        canvas.itemconfig(window_id, width=event.width)
    canvas.bind("<Configure>", _on_canvas_resize)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    canvas.bind_all("<MouseWheel>", _on_mousewheel)

    # ── Accent bar at top ────────────────────────────────────────────────────
    accent_bar = tk.Frame(scroll_frame, bg=ACCENT, height=3)
    accent_bar.pack(fill="x")

    # ── Logo / brand mark ────────────────────────────────────────────────────
    brand_frame = tk.Frame(scroll_frame, bg=BG)
    brand_frame.pack(pady=(28, 0), padx=36, anchor="w")

    # Decorative dot cluster
    dot_canvas = tk.Canvas(brand_frame, width=32, height=32,
                           bg=BG, highlightthickness=0)
    dot_canvas.pack(side="left", padx=(0, 10))
    dot_canvas.create_oval(0, 0, 14, 14, fill=ACCENT, outline="")
    dot_canvas.create_oval(18, 0, 32, 14, fill=ACCENT2, outline="")
    dot_canvas.create_oval(9, 18, 23, 32, fill=SUCCESS, outline="")

    tk.Label(brand_frame, text="BRGY",
             font=("Courier", 11, "bold"),
             fg=ACCENT, bg=BG).pack(side="left")
    tk.Label(brand_frame, text=" SYSTEM",
             font=("Courier", 11),
             fg=MUTED, bg=BG).pack(side="left")

    # ── Heading ──────────────────────────────────────────────────────────────
    heading_frame = tk.Frame(scroll_frame, bg=BG)
    heading_frame.pack(pady=(18, 2), padx=36, anchor="w")

    tk.Label(heading_frame, text="Create",
             font=("Georgia", 26, "bold"),
             fg=TEXT, bg=BG).pack(side="left")
    tk.Label(heading_frame, text=" Account",
             font=("Georgia", 26, "italic"),
             fg=ACCENT, bg=BG).pack(side="left")

    tk.Label(scroll_frame, text="Fill in your details below to get started",
             font=("Courier", 9),
             fg=MUTED, bg=BG).pack(anchor="w", padx=36, pady=(0, 20))

    # ── Card container ───────────────────────────────────────────────────────
    card = tk.Frame(scroll_frame, bg=CARD,
                    highlightthickness=1,
                    highlightbackground=BORDER, bd=0)
    card.pack(padx=26, fill="x")

    # ── Section label helper ─────────────────────────────────────────────────
    def section_label(parent, text):
        row = tk.Frame(parent, bg=CARD)
        row.pack(fill="x", padx=18, pady=(14, 0))
        tk.Label(row, text="▸ " + text,
                 font=("Courier", 8, "bold"),
                 fg=ACCENT, bg=CARD).pack(side="left")
        tk.Frame(row, bg=BORDER, height=1).pack(
            side="left", fill="x", expand=True, padx=(8, 0), pady=6)

    # ── Entry factory ────────────────────────────────────────────────────────
    entries = {}

    def make_entry(parent, key, placeholder="", show=None):
        wrap = tk.Frame(parent, bg=CARD)
        wrap.pack(fill="x", padx=18, pady=5)

        tk.Label(wrap, text=key,
                 font=("Courier", 8, "bold"),
                 fg=MUTED, bg=CARD).pack(anchor="w")

        inner = tk.Frame(wrap, bg=PANEL,
                         highlightthickness=1,
                         highlightbackground=BORDER)
        inner.pack(fill="x", pady=(2, 0))

        entry = tk.Entry(inner, show=show,
                         bg=PANEL, fg=TEXT,
                         font=("Courier", 10),
                         relief="flat",
                         insertbackground=ACCENT,
                         bd=0)
        entry.pack(fill="x", padx=10, pady=7)

        # Focus glow effect
        def on_focus_in(e):
            inner.config(highlightbackground=ACCENT)
        def on_focus_out(e):
            inner.config(highlightbackground=BORDER)

        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)

        entries[key] = entry

    # ── Personal info section ────────────────────────────────────────────────
    section_label(card, "PERSONAL INFO")
    make_entry(card, "First Name")
    make_entry(card, "Last Name")

    # ── Contact section ──────────────────────────────────────────────────────
    section_label(card, "CONTACT")
    make_entry(card, "Email")
    make_entry(card, "Phone")

    # ── Credentials section ──────────────────────────────────────────────────
    section_label(card, "CREDENTIALS")
    make_entry(card, "Username")
    make_entry(card, "Password", show="●")

    # ── Role section ─────────────────────────────────────────────────────────
    section_label(card, "ROLE")

    role_wrap = tk.Frame(card, bg=CARD)
    role_wrap.pack(fill="x", padx=18, pady=5)
    tk.Label(role_wrap, text="Role",
             font=("Courier", 8, "bold"),
             fg=MUTED, bg=CARD).pack(anchor="w")

    role_var = tk.StringVar(value="Select Role")

    role_inner = tk.Frame(role_wrap, bg=PANEL,
                          highlightthickness=1,
                          highlightbackground=BORDER)
    role_inner.pack(fill="x", pady=(2, 0))

    role_dropdown = tk.OptionMenu(role_inner, role_var,
                                  "Barangay Official", "Barangay Worker")
    role_dropdown.config(
        bg=PANEL, fg=TEXT,
        font=("Courier", 10),
        relief="flat", bd=0,
        activebackground=ACCENT,
        activeforeground=TEXT,
        highlightthickness=0,
        anchor="w"
    )
    role_dropdown["menu"].config(
        bg=PANEL, fg=TEXT,
        font=("Courier", 10),
        relief="flat",
        activebackground=ACCENT,
        activeforeground="white"
    )
    role_dropdown.pack(fill="x", padx=4, pady=3)

    # Bottom card padding
    tk.Frame(card, bg=CARD, height=10).pack()

    # ── Action ───────────────────────────────────────────────────────────────
    def create_account():
        first_name = entries["First Name"].get().strip()
        last_name  = entries["Last Name"].get().strip()
        email      = entries["Email"].get().strip()
        phone      = entries["Phone"].get().strip()
        username   = entries["Username"].get().strip()
        password   = entries["Password"].get().strip()
        role       = role_var.get()

        if not all([first_name, last_name, email, phone, username, password]):
            messagebox.showwarning("Missing Fields", "All fields are required.")
            return

        if role not in ["Barangay Official", "Barangay Worker"]:
            messagebox.showerror("Access Denied",
                                 "Only Barangay Officials or Workers can create an account.")
            return

        try:
            users_database.add_user(username, password,
                                    first_name, last_name, email, phone)
            messagebox.showinfo("Success",
                                f"Account created successfully as {role}!")
            root.destroy()
            return_to_login()
        except Exception:
            messagebox.showerror("Error", "Username already exists.")

    def go_back():
        root.destroy()
        return_to_login()

    # ── Buttons ──────────────────────────────────────────────────────────────
    btn_area = tk.Frame(scroll_frame, bg=BG)
    btn_area.pack(padx=26, pady=18, fill="x")

    # Primary button
    create_btn = tk.Button(
        btn_area,
        text="CREATE ACCOUNT  →",
        command=create_account,
        bg=ACCENT, fg="white",
        font=("Courier", 10, "bold"),
        activebackground="#3a7ce8",
        activeforeground="white",
        relief="flat", bd=0,
        cursor="hand2"
    )
    create_btn.pack(fill="x", ipady=10)

    # Divider
    div = tk.Frame(btn_area, bg=BORDER, height=1)
    div.pack(fill="x", pady=10)

    # Ghost back button
    back_btn = tk.Button(
        btn_area,
        text="← Back to Login",
        command=go_back,
        bg=BG, fg=MUTED,
        font=("Courier", 9),
        activebackground=PANEL,
        activeforeground=TEXT,
        relief="flat", bd=0,
        cursor="hand2"
    )
    back_btn.pack(fill="x", ipady=6)

    # Footer note
    tk.Label(scroll_frame,
             text="© Barangay Management System  ·  v1.0",
             font=("Courier", 7),
             fg=BORDER, bg=BG).pack(pady=(0, 14))

    root.mainloop()