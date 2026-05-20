import tkinter as tk
from tkinter import messagebox
import users_database
from logo import make_logo_canvas


def run_register(return_to_login):
    users_database.create_users_table()

    import theme as _font
    BG = _font.BG; CARD = _font.CARD; PANEL = _font.PANEL
    BORDER = _font.BORDER; ACCENT = _font.ACCENT; ACCENT2 = _font.ACCENT2
    SUCCESS = _font.SUCCESS; DANGER = _font.DANGER
    TEXT = _font.TEXT; MUTED = _font.MUTED

    # ── Root window ──────────────────────────────────────────────────────────
    root = tk.Tk()
    root.title("Create Account")
    root.configure(bg=BG)
    root.geometry("460x780")
    root.minsize(420, 680)
    root.resizable(True, True)

    root.update_idletasks()
    x = (root.winfo_screenwidth() - 460) // 2
    y = (root.winfo_screenheight() - 780) // 2
    root.geometry(f"460x780+{x}+{y}")

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

    def _on_canvas_resize(event):
        canvas.itemconfig(window_id, width=event.width)
    canvas.bind("<Configure>", _on_canvas_resize)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    canvas.bind_all("<MouseWheel>", _on_mousewheel)

    # ── Top accent stripe ─────────────────────────────────────────────────────
    tk.Frame(scroll_frame, bg=ACCENT, height=3).pack(fill="x")

    # ── RIMS Logo ─────────────────────────────────────────────────────────────
    logo_outer = tk.Frame(scroll_frame, bg=BG)
    logo_outer.pack(fill="x", padx=20, pady=(20, 0))

    logo_c = make_logo_canvas(logo_outer, scale=0.62, bg=BG)
    logo_c.pack(anchor="w")

    # Thin separator under logo
    tk.Frame(scroll_frame, bg=BORDER, height=1).pack(
        fill="x", padx=26, pady=(10, 0))

    # ── Heading ──────────────────────────────────────────────────────────────
    heading_frame = tk.Frame(scroll_frame, bg=BG)
    heading_frame.pack(pady=(16, 2), padx=36, anchor="w")

    tk.Label(heading_frame, text="Create",
             font=_font.font("Georgia", 24, "bold"),
             fg=TEXT, bg=BG).pack(side="left")
    tk.Label(heading_frame, text=" Account",
             font=_font.font("Georgia", 24, "italic"),
             fg=ACCENT, bg=BG).pack(side="left")

    tk.Label(scroll_frame, text="Fill in your details below to get started",
             font=_font.font("Courier", 9),
             fg=MUTED, bg=BG).pack(anchor="w", padx=36, pady=(0, 16))

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
                 font=_font.font("Courier", 8, "bold"),
                 fg=ACCENT, bg=CARD).pack(side="left")
        tk.Frame(row, bg=BORDER, height=1).pack(
            side="left", fill="x", expand=True, padx=(8, 0), pady=6)

    # ── Entry factory ────────────────────────────────────────────────────────
    entries = {}

    def make_entry(parent, key, placeholder="", show=None):
        wrap = tk.Frame(parent, bg=CARD)
        wrap.pack(fill="x", padx=18, pady=5)

        tk.Label(wrap, text=key,
                 font=_font.font("Courier", 8, "bold"),
                 fg=MUTED, bg=CARD).pack(anchor="w")

        inner = tk.Frame(wrap, bg=PANEL,
                         highlightthickness=1,
                         highlightbackground=BORDER)
        inner.pack(fill="x", pady=(2, 0))

        entry = tk.Entry(inner, show=show,
                         bg=PANEL, fg=TEXT,
                         font=_font.font("Courier", 10),
                         relief="flat",
                         insertbackground=ACCENT,
                         bd=0)
        entry.pack(fill="x", padx=10, pady=7)

        def on_focus_in(e):  inner.config(highlightbackground=ACCENT)
        def on_focus_out(e): inner.config(highlightbackground=BORDER)
        entry.bind("<FocusIn>",  on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)

        entries[key] = entry

    # ── Sections ─────────────────────────────────────────────────────────────
    section_label(card, "PERSONAL INFO")
    make_entry(card, "First Name")
    make_entry(card, "Last Name")

    section_label(card, "CONTACT")
    make_entry(card, "Email")
    make_entry(card, "Phone")

    section_label(card, "CREDENTIALS")
    make_entry(card, "Username")
    make_entry(card, "Password", show="●")

    section_label(card, "REGISTRATION CODE")
    make_entry(card, "Registration Code", show="●")

    section_label(card, "ROLE")

    role_wrap = tk.Frame(card, bg=CARD)
    role_wrap.pack(fill="x", padx=18, pady=5)
    tk.Label(role_wrap, text="Role",
             font=_font.font("Courier", 8, "bold"),
             fg=MUTED, bg=CARD).pack(anchor="w")

    role_var = tk.StringVar(value="Select Role")

    role_inner = tk.Frame(role_wrap, bg=PANEL,
                          highlightthickness=1,
                          highlightbackground=BORDER)
    role_inner.pack(fill="x", pady=(2, 0))

    role_dropdown = tk.OptionMenu(role_inner, role_var,
                                  "Barangay Worker", "Staff",
                                  "Barangay Official", "Admin")
    role_dropdown.config(
        bg=PANEL, fg=TEXT,
        font=_font.font("Courier", 10),
        relief="flat", bd=0,
        activebackground=ACCENT,
        activeforeground=TEXT,
        highlightthickness=0,
        anchor="w"
    )
    role_dropdown["menu"].config(
        bg=PANEL, fg=TEXT,
        font=_font.font("Courier", 10),
        relief="flat",
        activebackground=ACCENT,
        activeforeground="white"
    )
    role_dropdown.pack(fill="x", padx=4, pady=3)

    tk.Frame(card, bg=CARD, height=10).pack()

    # ── Actions ──────────────────────────────────────────────────────────────
    def create_account():
        first_name = entries["First Name"].get().strip()
        last_name  = entries["Last Name"].get().strip()
        email      = entries["Email"].get().strip()
        phone      = entries["Phone"].get().strip()
        username   = entries["Username"].get().strip()
        password   = entries["Password"].get().strip()
        reg_code   = entries["Registration Code"].get().strip()
        role       = role_var.get()

        if not all([first_name, last_name, email, phone, username, password]):
            messagebox.showwarning("Missing Fields", "All fields are required.")
            return

        # Validate registration code
        stored_code = users_database.get_registration_code()
        if reg_code != stored_code:
            messagebox.showerror(
                "Invalid Code",
                "The registration code is incorrect.\n"
                "Contact your Barangay Admin for the correct code."
            )
            return

        valid_roles = users_database.ROLES
        if role not in valid_roles:
            messagebox.showerror("Invalid Role",
                                 "Please select a valid role.")
            return

        try:
            users_database.add_user(username, password,
                                    first_name, last_name, email, phone,
                                    role=role)

            # Check if the account was auto-approved (first admin) or pending
            if users_database.check_login_status(username, password) == "approved":
                messagebox.showinfo(
                    "Account Created",
                    f"Welcome! Your account has been created as {role}.\n"
                    "You can now log in."
                )
            else:
                messagebox.showinfo(
                    "Account Pending Approval",
                    f"Your account has been created as {role}.\n\n"
                    "An admin must approve your account before you can log in.\n"
                    "Please wait for approval."
                )

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

    create_btn = tk.Button(
        btn_area,
        text="CREATE ACCOUNT  →",
        command=create_account,
        bg=ACCENT, fg="white",
        font=_font.font("Courier", 10, "bold"),
        activebackground="#3a7ce8",
        activeforeground="white",
        relief="flat", bd=0,
        cursor="hand2"
    )
    create_btn.pack(fill="x", ipady=10)

    def _cbtn_enter(e): create_btn.config(bg="#3a7ce8")
    def _cbtn_leave(e): create_btn.config(bg=ACCENT)
    create_btn.bind("<Enter>", _cbtn_enter)
    create_btn.bind("<Leave>", _cbtn_leave)

    tk.Frame(btn_area, bg=BORDER, height=1).pack(fill="x", pady=10)

    back_btn = tk.Button(
        btn_area,
        text="← Back to Login",
        command=go_back,
        bg=BG, fg=MUTED,
        font=_font.font("Courier", 9),
        activebackground=PANEL,
        activeforeground=TEXT,
        relief="flat", bd=0,
        cursor="hand2"
    )
    back_btn.pack(fill="x", ipady=6)

    tk.Label(scroll_frame,
             text="© Barangay Management System  ·  v1.0",
             font=_font.font("Courier", 7),
             fg=BORDER, bg=BG).pack(pady=(0, 14))

    root.mainloop()