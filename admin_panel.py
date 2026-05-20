import tkinter as tk
from tkinter import ttk, messagebox
import users_database


def run_admin_panel(admin_username, on_close):
    """Open the admin panel window for managing users and settings."""

    import theme as _font
    BG = _font.BG; CARD = _font.CARD; PANEL = _font.PANEL
    BORDER = _font.BORDER; ACCENT = _font.ACCENT; ACCENT2 = _font.ACCENT2
    SUCCESS = _font.SUCCESS; DANGER = _font.DANGER; WARN = _font.WARN
    TEXT = _font.TEXT; MUTED = _font.MUTED

    # ── Window ────────────────────────────────────────────────────
    root = tk.Toplevel()
    root.title("RIMS — Admin Panel")
    root.configure(bg=BG)
    root.geometry("680x720")
    root.minsize(600, 620)
    root.resizable(True, True)

    root.update_idletasks()
    sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
    root.geometry(f"680x720+{(sw-680)//2}+{(sh-720)//2}")
    root.grab_set()

    def _back():
        root.destroy()
        on_close()

    root.protocol("WM_DELETE_WINDOW", _back)

    # ── Top accent stripe ─────────────────────────────────────────
    tk.Frame(root, bg=ACCENT2, height=3).pack(fill="x")

    # ── Header ────────────────────────────────────────────────────
    hdr = tk.Frame(root, bg=BG)
    hdr.pack(fill="x", padx=24, pady=(16, 4))
    hdr.grid_columnconfigure(0, weight=1)

    tf = tk.Frame(hdr, bg=BG)
    tf.grid(row=0, column=0, sticky="w")
    tk.Label(tf, text="Admin Panel",
             font=_font.font("Georgia", 20, "bold"),
             fg=TEXT, bg=BG).pack(side="left")
    tk.Label(tf, text="  ⚙",
             font=_font.font("Courier", 16),
             fg=ACCENT2, bg=BG).pack(side="left")

    tk.Label(hdr, text=f"Logged in as: {admin_username}",
             font=_font.font("Courier", 8),
             fg=MUTED, bg=BG).grid(row=1, column=0, sticky="w")

    # ── Determine user role for conditional access ───────────────
    user_role = users_database.get_user_role(admin_username)
    is_high_admin = users_database.has_permission(admin_username, "Barangay Official")
    is_staff = users_database.has_permission(admin_username, "Staff") and not is_high_admin

    role_label = tk.Label(hdr,
                          text=f"Role: {user_role}",
                          font=_font.font("Courier", 8, "bold"),
                          fg=ACCENT2 if is_high_admin else WARN,
                          bg=BG)
    role_label.grid(row=1, column=1, sticky="e", padx=(10, 0))

    # ── Notebook (tabs) ───────────────────────────────────────────
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Admin.TNotebook",
                    background=BG, borderwidth=0)
    style.configure("Admin.TNotebook.Tab",
                    background=PANEL, foreground=MUTED,
                    font=_font.font("Courier", 9, "bold"),
                    padding=(16, 6),
                    borderwidth=0)
    style.map("Admin.TNotebook.Tab",
              background=[("selected", CARD)],
              foreground=[("selected", ACCENT)])

    nb = ttk.Notebook(root, style="Admin.TNotebook")
    nb.pack(fill="both", expand=True, padx=20, pady=(8, 12))

    # ══════════════════════════════════════════════════════════════
    # TAB 1 — Pending Approvals  (hidden for Staff)
    # ══════════════════════════════════════════════════════════════
    if is_high_admin:
        pending_tab = tk.Frame(nb, bg=BG)
        nb.add(pending_tab, text="Pending Approvals")

    # ── Info label ────────────────────────────────────────────────
    info_lbl = tk.Label(pending_tab,
                        text="Review and approve new account requests below.",
                        font=_font.font("Courier", 9),
                        fg=MUTED, bg=BG)
    info_lbl.pack(anchor="w", padx=16, pady=(12, 4))

    # ── Pending count badge ───────────────────────────────────────
    count_frame = tk.Frame(pending_tab, bg=BG)
    count_frame.pack(fill="x", padx=16, pady=(0, 8))

    pending_count_lbl = tk.Label(count_frame, text="0 pending",
                                 font=_font.font("Courier", 9, "bold"),
                                 fg=WARN, bg=BG)
    pending_count_lbl.pack(side="left")

    # ── Treeview card ─────────────────────────────────────────────
    tree_card = tk.Frame(pending_tab, bg=CARD,
                         highlightthickness=1, highlightbackground=BORDER)
    tree_card.pack(fill="both", expand=True, padx=16, pady=(0, 10))
    tree_card.grid_rowconfigure(0, weight=1)
    tree_card.grid_columnconfigure(0, weight=1)

    # Treeview style
    style.configure("Admin.Treeview",
                    background=PANEL, foreground=TEXT,
                    fieldbackground=PANEL, borderwidth=0,
                    font=_font.font("Courier", 9), rowheight=34)
    style.configure("Admin.Treeview.Heading",
                    background=CARD, foreground=ACCENT,
                    font=_font.font("Courier", 8, "bold"),
                    borderwidth=0, relief="flat")
    style.map("Admin.Treeview",
              background=[("selected", ACCENT)],
              foreground=[("selected", "white")])
    style.map("Admin.Treeview.Heading",
              background=[("active", PANEL)])

    vsb = tk.Scrollbar(tree_card, orient="vertical",
                       bg=BORDER, troughcolor=CARD,
                       width=6, relief="flat", highlightthickness=0)
    vsb.grid(row=0, column=1, sticky="ns")

    cols = ("ID", "Username", "First Name", "Last Name",
            "Email", "Phone", "Role")
    tree = ttk.Treeview(tree_card, columns=cols, show="headings",
                        style="Admin.Treeview", yscrollcommand=vsb.set,
                        height=8)

    col_cfg = {
        "ID":         (50,  "center"),
        "Username":   (120, "w"),
        "First Name": (120, "w"),
        "Last Name":  (120, "w"),
        "Email":      (160, "w"),
        "Phone":      (120, "center"),
        "Role":       (120, "w"),
    }
    for col in cols:
        w, anch = col_cfg[col]
        tree.heading(col, text=col)
        tree.column(col, width=w, minwidth=w, anchor=anch, stretch=True)

    tree.grid(row=0, column=0, sticky="nsew")
    vsb.config(command=tree.yview)
    tree.tag_configure("odd",  background=PANEL)
    tree.tag_configure("even", background="#161a26")

    # ── Action buttons ────────────────────────────────────────────
    action_frame = tk.Frame(pending_tab, bg=BG)
    action_frame.pack(fill="x", padx=16, pady=(0, 12))

    def refresh_pending():
        for row in tree.get_children():
            tree.delete(row)
        pending = users_database.get_pending_users()
        for i, p in enumerate(pending):
            tag = "odd" if i % 2 == 0 else "even"
            tree.insert("", "end", values=p[:7], tags=(tag,))
        n = len(pending)
        pending_count_lbl.config(
            text=f"{n} pending {'request' if n == 1 else 'requests'}")
        approve_btn.config(state="normal" if n > 0 else "disabled")
        reject_btn.config(state="normal" if n > 0 else "disabled")

    def _get_selected():
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Select a user first.")
            return None
        vals = tree.item(sel[0])["values"]
        return vals[0]  # user ID

    def approve_selected():
        uid = _get_selected()
        if uid is None:
            return
        users_database.approve_user(uid, acted_by=admin_username)
        refresh_pending()
        refresh_audit_log()
        messagebox.showinfo("Approved", "User has been approved.")

    def reject_selected():
        uid = _get_selected()
        if uid is None:
            return
        # Get username for confirmation message
        sel = tree.selection()
        username = tree.item(sel[0])["values"][1] if sel else "this user"

        confirm = messagebox.askyesno(
            "Reject User",
            f"Reject and delete '{username}'?\n\n"
            "This cannot be undone."
        )
        if confirm:
            users_database.reject_user(uid, acted_by=admin_username)
            refresh_pending()
            refresh_audit_log()
            messagebox.showinfo("Rejected", "User has been rejected.")

    def select_all():
        for child in tree.get_children():
            tree.selection_add(child)

    def deselect_all():
        for child in tree.get_children():
            tree.selection_remove(child)

    tree.bind("<Double-1>", lambda e: approve_selected())

    # Approve / Reject buttons
    approve_btn = tk.Button(action_frame, text="✓  Approve Selected",
                            command=approve_selected,
                            bg=SUCCESS, fg="#0d0f14",
                            activebackground="#3ab868",
                            activeforeground="#0d0f14",
                            font=_font.font("Courier", 9, "bold"),
                            relief="flat", bd=0, cursor="hand2",
                            state="disabled")
    approve_btn.pack(side="left", padx=(0, 6), ipady=7, ipadx=16)

    reject_btn = tk.Button(action_frame, text="✕  Reject Selected",
                           command=reject_selected,
                           bg=DANGER, fg="white",
                           activebackground="#d93a52",
                           font=_font.font("Courier", 9, "bold"),
                           relief="flat", bd=0, cursor="hand2",
                           state="disabled")
    reject_btn.pack(side="left", padx=(0, 12), ipady=7, ipadx=16)

    # Selection helpers
    tk.Button(action_frame, text="Select All",
              command=select_all,
              bg=PANEL, fg=MUTED,
              activebackground=BORDER, activeforeground=TEXT,
              font=_font.font("Courier", 8),
              relief="flat", bd=0, cursor="hand2").pack(
                  side="right", padx=(4, 0), ipady=7, ipadx=10)

    tk.Button(action_frame, text="Deselect",
              command=deselect_all,
              bg=PANEL, fg=MUTED,
              activebackground=BORDER, activeforeground=TEXT,
              font=_font.font("Courier", 8),
              relief="flat", bd=0, cursor="hand2").pack(
                  side="right", padx=(4, 0), ipady=7, ipadx=10)

    # ══════════════════════════════════════════════════════════════
    # TAB 2 — Audit Log
    # ══════════════════════════════════════════════════════════════
    audit_tab = tk.Frame(nb, bg=BG)
    nb.add(audit_tab, text="Audit Log")

    # ── Info label ────────────────────────────────────────────────
    tk.Label(audit_tab,
             text="Record of all account approvals and rejections.",
             font=_font.font("Courier", 9),
             fg=MUTED, bg=BG).pack(anchor="w", padx=16, pady=(12, 6))

    # ── Treeview card ─────────────────────────────────────────────
    audit_card = tk.Frame(audit_tab, bg=CARD,
                          highlightthickness=1, highlightbackground=BORDER)
    audit_card.pack(fill="both", expand=True, padx=16, pady=(0, 10))
    audit_card.grid_rowconfigure(0, weight=1)
    audit_card.grid_columnconfigure(0, weight=1)

    audit_vsb = tk.Scrollbar(audit_card, orient="vertical",
                             bg=BORDER, troughcolor=CARD,
                             width=6, relief="flat", highlightthickness=0)
    audit_vsb.grid(row=0, column=1, sticky="ns")

    audit_cols = ("ID", "Timestamp", "Action", "User", "Acted By")
    audit_tree = ttk.Treeview(audit_card, columns=audit_cols, show="headings",
                              style="Admin.Treeview", yscrollcommand=audit_vsb.set,
                              height=10)

    audit_col_cfg = {
        "ID":        (40,  "center"),
        "Timestamp": (140, "center"),
        "Action":    (100, "center"),
        "User":      (140, "w"),
        "Acted By":  (140, "w"),
    }
    for col in audit_cols:
        w, anch = audit_col_cfg[col]
        audit_tree.heading(col, text=col)
        audit_tree.column(col, width=w, minwidth=w, anchor=anch, stretch=True)

    audit_tree.grid(row=0, column=0, sticky="nsew")
    audit_vsb.config(command=audit_tree.yview)
    audit_tree.tag_configure("odd",  background=PANEL)
    audit_tree.tag_configure("even", background="#161a26")
    audit_tree.tag_configure("approved", foreground=SUCCESS)
    audit_tree.tag_configure("rejected", foreground="#ff6b6b")

    def refresh_audit_log():
        for row in audit_tree.get_children():
            audit_tree.delete(row)
        entries = users_database.get_audit_log()
        for i, e in enumerate(entries):
            tag = "odd" if i % 2 == 0 else "even"
            action_tag = e[2]  # "approved" or "rejected"
            audit_tree.insert("", "end", values=e[:5],
                              tags=(tag, action_tag))

    # ── Refresh button ────────────────────────────────────────────
    audit_actions = tk.Frame(audit_tab, bg=BG)
    audit_actions.pack(fill="x", padx=16, pady=(0, 12))

    tk.Button(audit_actions, text="↻  Refresh",
              command=refresh_audit_log,
              bg=PANEL, fg=TEXT,
              activebackground=BORDER, activeforeground=ACCENT,
              font=_font.font("Courier", 8, "bold"),
              relief="flat", bd=0, cursor="hand2").pack(
                  side="left", ipady=7, ipadx=14)

    tk.Label(audit_actions,
             text="* Entries are timestamped automatically",
             font=_font.font("Courier", 7),
             fg=BORDER, bg=BG).pack(side="right", pady=6)

    # ══════════════════════════════════════════════════════════════
    # TAB 3 — Password Reset  (available to Staff, Official, Admin)
    # ══════════════════════════════════════════════════════════════
    reset_tab = tk.Frame(nb, bg=BG)
    nb.add(reset_tab, text="Password Reset")

    # ── Info ──────────────────────────────────────────────────────
    tk.Label(reset_tab,
             text="Reset the password of any approved user.",
             font=_font.font("Courier", 9),
             fg=MUTED, bg=BG).pack(anchor="w", padx=16, pady=(12, 6))

    # ── Main card ─────────────────────────────────────────────────
    reset_card = tk.Frame(reset_tab, bg=CARD,
                          highlightthickness=1, highlightbackground=BORDER)
    reset_card.pack(fill="both", expand=True, padx=16, pady=(0, 10))

    tk.Frame(reset_card, bg=ACCENT, height=3).pack(fill="x")

    tk.Label(reset_card, text="▸  SELECT USER",
             font=_font.font("Courier", 9, "bold"),
             fg=ACCENT, bg=CARD).pack(anchor="w", padx=16, pady=(12, 6))

    # ── User dropdown ─────────────────────────────────────────────
    user_row = tk.Frame(reset_card, bg=CARD)
    user_row.pack(fill="x", padx=16, pady=(0, 10))
    user_row.grid_columnconfigure(1, weight=1)

    tk.Label(user_row, text="User:",
             font=_font.font("Courier", 9, "bold"),
             fg=TEXT, bg=CARD).grid(row=0, column=0, sticky="w", padx=(0, 10))

    user_var = tk.StringVar()
    user_dropdown = ttk.Combobox(user_row, textvariable=user_var,
                                  font=_font.font("Courier", 10),
                                  state="readonly")
    user_dropdown.grid(row=0, column=1, sticky="ew")

    # Style the dropdown
    style.configure("Admin.TCombobox",
                    fieldbackground=PANEL, background=PANEL,
                    foreground=TEXT, arrowcolor=ACCENT,
                    bordercolor=BORDER, lightcolor=BORDER, darkcolor=BORDER)
    user_dropdown.configure(style="Admin.TCombobox")

    # ── New password section ──────────────────────────────────────
    tk.Frame(reset_card, bg=BORDER, height=1).pack(fill="x", padx=16, pady=(0, 10))

    tk.Label(reset_card, text="▸  NEW PASSWORD",
             font=_font.font("Courier", 9, "bold"),
             fg=ACCENT, bg=CARD).pack(anchor="w", padx=16, pady=(0, 6))

    pw1_row = tk.Frame(reset_card, bg=CARD)
    pw1_row.pack(fill="x", padx=16, pady=(0, 8))
    pw1_row.grid_columnconfigure(1, weight=1)

    tk.Label(pw1_row, text="Password:",
             font=_font.font("Courier", 9, "bold"),
             fg=TEXT, bg=CARD).grid(row=0, column=0, sticky="w", padx=(0, 10))

    pw1_wrap = tk.Frame(pw1_row, bg=PANEL,
                        highlightthickness=1, highlightbackground=BORDER)
    pw1_wrap.grid(row=0, column=1, sticky="ew")

    pw1_var = tk.StringVar()
    pw1_entry = tk.Entry(pw1_wrap, textvariable=pw1_var,
                         bg=PANEL, fg=TEXT,
                         font=_font.font("Courier", 11),
                         show="\u2022",
                         relief="flat",
                         insertbackground=ACCENT, bd=0)
    pw1_entry.pack(fill="x", padx=10, pady=6)
    pw1_entry.bind("<FocusIn>",
                    lambda e: pw1_wrap.config(highlightbackground=ACCENT))
    pw1_entry.bind("<FocusOut>",
                    lambda e: pw1_wrap.config(highlightbackground=BORDER))

    pw2_row = tk.Frame(reset_card, bg=CARD)
    pw2_row.pack(fill="x", padx=16, pady=(0, 14))
    pw2_row.grid_columnconfigure(1, weight=1)

    tk.Label(pw2_row, text="Confirm:",
             font=_font.font("Courier", 9, "bold"),
             fg=TEXT, bg=CARD).grid(row=0, column=0, sticky="w", padx=(0, 10))

    pw2_wrap = tk.Frame(pw2_row, bg=PANEL,
                        highlightthickness=1, highlightbackground=BORDER)
    pw2_wrap.grid(row=0, column=1, sticky="ew")

    pw2_var = tk.StringVar()
    pw2_entry = tk.Entry(pw2_wrap, textvariable=pw2_var,
                         bg=PANEL, fg=TEXT,
                         font=_font.font("Courier", 11),
                         show="\u2022",
                         relief="flat",
                         insertbackground=ACCENT, bd=0)
    pw2_entry.pack(fill="x", padx=10, pady=6)
    pw2_entry.bind("<FocusIn>",
                    lambda e: pw2_wrap.config(highlightbackground=ACCENT))
    pw2_entry.bind("<FocusOut>",
                    lambda e: pw2_wrap.config(highlightbackground=BORDER))

    # ── Strength indicator ────────────────────────────────────────
    strength_row = tk.Frame(reset_card, bg=CARD)
    strength_row.pack(fill="x", padx=16, pady=(0, 12))
    strength_row.grid_columnconfigure(1, weight=1)

    tk.Label(strength_row, text="Strength:",
             font=_font.font("Courier", 8, "bold"),
             fg=MUTED, bg=CARD).grid(row=0, column=0, sticky="w", padx=(0, 10))

    strength_bar = tk.Frame(strength_row, bg=PANEL,
                            height=10, width=200,
                            highlightthickness=1, highlightbackground=BORDER)
    strength_bar.grid(row=0, column=1, sticky="w")
    strength_bar.grid_propagate(False)

    strength_fill = tk.Frame(strength_bar, bg=DANGER, height=10, width=0)
    strength_fill.pack(side="left")

    strength_lbl = tk.Label(strength_row, text="",
                            font=_font.font("Courier", 8),
                            fg=MUTED, bg=CARD)
    strength_lbl.grid(row=0, column=2, sticky="w", padx=(8, 0))

    def _update_strength(*_):
        pw = pw1_var.get()
        length = len(pw)
        if length == 0:
            strength_fill.config(width=0, bg=DANGER)
            strength_lbl.config(text="", fg=MUTED)
        elif length < 6:
            strength_fill.config(width=50, bg=DANGER)
            strength_lbl.config(text="Weak", fg=DANGER)
        elif length < 10:
            strength_fill.config(width=100, bg=WARN)
            strength_lbl.config(text="Fair", fg=WARN)
        elif length < 14:
            strength_fill.config(width=150, bg=SUCCESS)
            strength_lbl.config(text="Good", fg=SUCCESS)
        else:
            strength_fill.config(width=200, bg=ACCENT2)
            strength_lbl.config(text="Strong", fg=ACCENT2)

    pw1_var.trace_add("write", _update_strength)

    # ── Reset button ──────────────────────────────────────────────
    btn_row = tk.Frame(reset_card, bg=CARD)
    btn_row.pack(fill="x", padx=16, pady=(0, 16))

    def refresh_user_list():
        users = users_database.get_approved_users()
        names = [f"{u[1]}  —  {u[2]} {u[3]} ({u[4]})" for u in users]
        user_dropdown["values"] = names
        if names and not user_var.get():
            user_dropdown.current(0)

    def do_reset():
        sel = user_var.get()
        if not sel:
            messagebox.showwarning("No User", "Select a user first.")
            return
        username = sel.split("  —  ")[0].strip()

        pw1 = pw1_var.get().strip()
        pw2 = pw2_var.get().strip()

        if not pw1:
            messagebox.showwarning("Missing Password", "Enter a new password.")
            pw1_entry.focus_set()
            return
        if len(pw1) < 6:
            messagebox.showwarning("Too Short", "Password must be at least 6 characters.")
            pw1_entry.focus_set()
            return
        if pw1 != pw2:
            messagebox.showwarning("Mismatch", "Passwords do not match.")
            pw2_entry.focus_set()
            return

        confirm = messagebox.askyesno(
            "Confirm Reset",
            f"Reset password for '{username}'?\n\n"
            "The user will need to use the new password to log in."
        )
        if not confirm:
            return

        success = users_database.reset_password(username, pw1, acted_by=admin_username)
        if success:
            pw1_var.set("")
            pw2_var.set("")
            refresh_audit_log()
            messagebox.showinfo("Password Reset",
                                f"Password for '{username}' has been reset.")
        else:
            messagebox.showerror("Error", f"Could not find user '{username}'.")

    reset_btn = tk.Button(btn_row, text="🔑  Reset Password",
                          command=do_reset,
                          bg=ACCENT, fg="white",
                          activebackground="#3a7ce8",
                          font=_font.font("Courier", 9, "bold"),
                          relief="flat", bd=0, cursor="hand2")
    reset_btn.pack(side="left", ipady=7, ipadx=16)

    tk.Label(btn_row,
             text="The reset will be logged in the Audit Log",
             font=_font.font("Courier", 7),
             fg=BORDER, bg=CARD).pack(side="right", pady=6)

    # ── Info note at bottom ───────────────────────────────────────
    tk.Label(reset_tab,
             text="ℹ  Users are hashed with SHA-256 — the new password cannot be retrieved, only overwritten.",
             font=_font.font("Courier", 8),
             fg=MUTED, bg=BG, wraplength=600, justify="left").pack(
                 anchor="w", padx=20, pady=(0, 10))

    # ══════════════════════════════════════════════════════════════
    # TAB 4 — Settings  (hidden for Staff)
    # ══════════════════════════════════════════════════════════════
    if is_high_admin:
        settings_tab = tk.Frame(nb, bg=BG)
        nb.add(settings_tab, text="Settings")

    # ── Registration Code section ─────────────────────────────────
    reg_card = tk.Frame(settings_tab, bg=CARD,
                        highlightthickness=1, highlightbackground=BORDER)
    reg_card.pack(fill="x", padx=16, pady=(16, 8))

    tk.Frame(reg_card, bg=ACCENT2, height=3).pack(fill="x")

    sec_hdr = tk.Frame(reg_card, bg=CARD)
    sec_hdr.pack(fill="x", padx=16, pady=(12, 4))
    tk.Label(sec_hdr, text="▸  REGISTRATION CODE",
             font=_font.font("Courier", 9, "bold"),
             fg=ACCENT, bg=CARD).pack(side="left")

    tk.Label(reg_card,
             text="This code must be entered when creating a new account.\n"
                  "Share it only with trusted Barangay Officials and Workers.",
             font=_font.font("Courier", 8),
             fg=MUTED, bg=CARD, wraplength=580, justify="left").pack(
                 anchor="w", padx=16, pady=(0, 10))

    # Current code display
    code_row = tk.Frame(reg_card, bg=CARD)
    code_row.pack(fill="x", padx=16, pady=(0, 10))
    code_row.grid_columnconfigure(1, weight=1)

    tk.Label(code_row, text="Current code:",
             font=_font.font("Courier", 9, "bold"),
             fg=TEXT, bg=CARD).grid(row=0, column=0, sticky="w", padx=(0, 10))

    code_display = tk.Label(code_row,
                            text=users_database.get_registration_code(),
                            font=_font.font("Courier", 11, "bold"),
                            fg=SUCCESS, bg=PANEL,
                            relief="solid", bd=1,
                            highlightthickness=1, highlightbackground=BORDER,
                            anchor="w", padx=10, pady=4)
    code_display.grid(row=0, column=1, sticky="ew")

    # Change code section
    tk.Frame(reg_card, bg=BORDER, height=1).pack(fill="x", padx=16, pady=(0, 10))

    new_code_row = tk.Frame(reg_card, bg=CARD)
    new_code_row.pack(fill="x", padx=16, pady=(0, 14))
    new_code_row.grid_columnconfigure(1, weight=1)

    tk.Label(new_code_row, text="New code:",
             font=_font.font("Courier", 9, "bold"),
             fg=TEXT, bg=CARD).grid(row=0, column=0, sticky="w", padx=(0, 10))

    code_entry_wrap = tk.Frame(new_code_row, bg=PANEL,
                               highlightthickness=1, highlightbackground=BORDER)
    code_entry_wrap.grid(row=0, column=1, sticky="ew", padx=(0, 8))

    new_code_var = tk.StringVar()
    new_code_entry = tk.Entry(code_entry_wrap,
                              textvariable=new_code_var,
                              bg=PANEL, fg=TEXT,
                              font=_font.font("Courier", 11),
                              relief="flat",
                              insertbackground=ACCENT, bd=0)
    new_code_entry.pack(fill="x", padx=10, pady=6)
    new_code_entry.bind("<FocusIn>",
                        lambda e: code_entry_wrap.config(highlightbackground=ACCENT))
    new_code_entry.bind("<FocusOut>",
                        lambda e: code_entry_wrap.config(highlightbackground=BORDER))

    def update_code():
        new_code = new_code_var.get().strip()
        if not new_code:
            messagebox.showwarning("Missing Code", "Enter a new registration code.")
            return
        if len(new_code) < 4:
            messagebox.showwarning("Too Short", "Code must be at least 4 characters.")
            return
        confirm = messagebox.askyesno(
            "Confirm Change",
            f"Change registration code to:\n\n  {new_code}\n\n"
            "Existing users will not be affected, but new registrations\n"
            "will need the new code."
        )
        if confirm:
            users_database.set_registration_code(new_code)
            code_display.config(text=new_code)
            new_code_var.set("")
            messagebox.showinfo("Updated", "Registration code has been updated.")

    update_btn = tk.Button(new_code_row, text="Update Code",
                           command=update_code,
                           bg=ACCENT, fg="white",
                           activebackground="#3a7ce8",
                           font=_font.font("Courier", 9, "bold"),
                           relief="flat", bd=0, cursor="hand2")
    update_btn.grid(row=0, column=2, ipady=6, ipadx=10)

    # ── Staff info card ───────────────────────────────────────────
    if is_staff:
        staff_info = tk.Frame(reset_tab, bg=CARD,
                              highlightthickness=1, highlightbackground=BORDER)
        staff_info.pack(fill="x", padx=16, pady=(0, 10))
        tk.Frame(staff_info, bg=ACCENT, height=3).pack(fill="x")
        tk.Label(staff_info, text="▸  YOUR ACCESS",
                 font=_font.font("Courier", 9, "bold"),
                 fg=ACCENT, bg=CARD).pack(anchor="w", padx=16, pady=(12, 6))
        tk.Label(staff_info,
                 text="As a Staff member, you can:\n"
                      "  • Reset passwords for any user\n"
                      "  • View the Audit Log\n\n"
                      "For approvals and settings changes, contact a Barangay Official or Admin.",
                 font=_font.font("Courier", 8),
                 fg=TEXT, bg=CARD, wraplength=580, justify="left").pack(
                     anchor="w", padx=16, pady=(0, 12))

    # ── Admin info card (only for high admins) ────────────────────
    if is_high_admin:
        info_card = tk.Frame(settings_tab, bg=CARD,
                             highlightthickness=1, highlightbackground=BORDER)
        info_card.pack(fill="x", padx=16, pady=(0, 10))

    tk.Frame(info_card, bg=ACCENT, height=3).pack(fill="x")

    tk.Label(info_card, text="▸  ADMIN INFORMATION",
             font=_font.font("Courier", 9, "bold"),
             fg=ACCENT, bg=CARD).pack(anchor="w", padx=16, pady=(12, 6))

    admin_count = users_database.count_admins()

    info_items = [
        ("Current Admin", f"{admin_count}"),
        ("Security", "SHA-256 password hashing"),
        ("Account approval", "Required for new users"),
    ]

    for label, value in info_items:
        row_f = tk.Frame(info_card, bg=CARD)
        row_f.pack(fill="x", padx=16, pady=3)
        tk.Label(row_f, text=label,
                 font=_font.font("Courier", 8, "bold"),
                 fg=MUTED, bg=CARD, width=18, anchor="w").pack(side="left")
        tk.Label(row_f, text=value,
                 font=_font.font("Courier", 9),
                 fg=TEXT, bg=CARD).pack(side="left")

    info_card.update_idletasks()
    tk.Frame(info_card, bg=CARD, height=8).pack()

    # ── Footer ────────────────────────────────────────────────────
    foot = tk.Frame(root, bg=BG)
    foot.pack(fill="x", padx=24, pady=(0, 12))

    tk.Button(foot, text="←  Back to Login",
              command=_back,
              bg=PANEL, fg=MUTED,
              activebackground=BORDER, activeforeground=TEXT,
              font=_font.font("Courier", 9, "bold"),
              relief="flat", bd=0, cursor="hand2").pack(
                  side="left", ipady=7, ipadx=16)

    tk.Label(foot, text="© RIMS  ·  Barangay Edition",
             font=_font.font("Courier", 7),
             fg=BORDER, bg=BG).pack(side="right", pady=6)

    # ── Load data ─────────────────────────────────────────────────
    if is_high_admin:
        refresh_pending()
    refresh_audit_log()
    refresh_user_list()
    root.mainloop()
