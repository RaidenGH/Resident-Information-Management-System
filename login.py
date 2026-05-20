import tkinter as tk
from tkinter import messagebox
import users_database
import database
from purok import run_purok_window
import register
from datetime import datetime
import platform

if platform.system() == "Windows":
    import ctypes

# ── Windows taskbar helpers ───────────────────────────────────────────────────
def _set_app_user_model_id(app_id: str):
    if platform.system() != "Windows":
        return
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
    except Exception:
        pass

def _ensure_taskbar_entry(win):
    if platform.system() != "Windows":
        return
    try:
        GWL_EXSTYLE    = -20
        WS_EX_APPWINDOW  = 0x00040000
        WS_EX_TOOLWINDOW = 0x00000080
        SWP_FLAGS = 0x0001 | 0x0002 | 0x0004 | 0x0020
        hwnd = win.winfo_id()
        ex   = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE,
                                            (ex | WS_EX_APPWINDOW) & ~WS_EX_TOOLWINDOW)
        ctypes.windll.user32.SetWindowPos(hwnd, 0, 0, 0, 0, 0, SWP_FLAGS)
    except Exception:
        pass


# ── Inline logo drawing ───────────────────────────────────────────────────────
def _draw_logo(canvas, x=0, y=0, scale=1.0):
    import theme as _t
    ox, oy = x, y
    def s(v): return v * scale
    def pt(px, py): return ox + s(px), oy + s(py)

    outer = [ox+s(42), oy+s(0),  ox+s(84), oy+s(24),
             ox+s(84), oy+s(72), ox+s(42), oy+s(96),
             ox+s(0),  oy+s(72), ox+s(0),  oy+s(24)]
    canvas.create_polygon(outer, fill="", outline=_t.BORDER, width=max(1, int(1.5*scale)))

    inner = [ox+s(42), oy+s(12), ox+s(76), oy+s(30),
             ox+s(76), oy+s(66), ox+s(42), oy+s(84),
             ox+s(8),  oy+s(66), ox+s(8),  oy+s(30)]
    canvas.create_polygon(inner, fill=_t.CARD, outline=_t.BORDER, width=max(1, int(scale)))

    for ly in [s(42), s(54), s(66)]:
        canvas.create_line(ox+s(15), oy+ly, ox+s(69), oy+ly, fill=_t.BORDER, width=1)

    nodes = {
        "top": pt(42, 30), "ml": pt(27, 24), "mr": pt(57, 24),
        "cl":  pt(27, 54), "cr": pt(57, 54), "bot": pt(42, 66),
    }
    for a, b in [("ml","top"),("top","mr"),("ml","cl"),("mr","cr"),
                 ("cl","bot"),("cr","bot"),("top","bot"),("cl","cr")]:
        canvas.create_line(*nodes[a], *nodes[b], fill=_t.BORDER, width=max(1, int(scale)))

    def dot(k, col, r=5):
        cx, cy = nodes[k]; r = s(r)
        canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill=col, outline="")

    dot("top", _t.ACCENT, 5);  dot("ml", _t.ACCENT, 3.5); dot("mr", _t.ACCENT, 3.5)
    dot("cl", _t.ACCENT2, 3.5); dot("cr", _t.ACCENT2, 3.5); dot("bot", _t.SUCCESS, 5)

    for px, py, col in [(84,24,_t.ACCENT),(0,72,_t.SUCCESS)]:
        cx,cy = ox+s(px), oy+s(py); r=s(4)
        canvas.create_oval(cx-r,cy-r,cx+r,cy+r, fill=col, outline="", stipple="gray50")

    divx = ox + s(100)
    canvas.create_line(divx, oy+s(4), divx, oy+s(92), fill=_t.BORDER, width=1)

    wx, wy = ox+s(112), oy+s(60)
    fs = max(10, int(36*scale))
    canvas.create_text(wx,                           wy, text="R",           font=_t.font("Georgia", fs, "bold"),        fill=_t.TEXT,   anchor="w")
    canvas.create_text(wx+int(fs*.68),               wy, text="I",  font=_t.font("Georgia", fs, "bold italic"),  fill=_t.ACCENT, anchor="w")
    canvas.create_text(wx+int(fs*.68)+int(fs*.38),   wy, text="MS", font=_t.font("Georgia", fs, "bold"),        fill=_t.TEXT,   anchor="w")

    canvas.create_line(wx, oy+s(68), wx+s(160), oy+s(68), fill=_t.ACCENT, width=max(1,int(2*scale)))
    canvas.create_text(wx, oy+s(80),
                       text="RESIDENT INFORMATION MANAGEMENT SYSTEM",
                       font=_t.font("Courier", max(7, int(8*scale))),
                       fill=_t.MUTED, anchor="w")


# ── Main login window ─────────────────────────────────────────────────────────
def run_login():
    import theme as _t

    users_database.create_users_table()
    database.create_tables()

    if platform.system() == "Windows":
        _set_app_user_model_id("com.rims.barangay")

    WIN_W, WIN_H = 780, 540
    root = tk.Tk()
    root.title("RIMS — Login")
    root.configure(bg=_t.BG)
    root.resizable(False, False)
    root.overrideredirect(True)

    sx, sy = root.winfo_screenwidth(), root.winfo_screenheight()
    root.geometry(f"{WIN_W}x{WIN_H}+{(sx-WIN_W)//2}+{(sy-WIN_H)//2}")
    root.update_idletasks()
    _ensure_taskbar_entry(root)

    # ── Outer border shell ────────────────────────────────────────
    shell = tk.Frame(root, bg=_t.BG,
                     highlightbackground=_t.BORDER, highlightthickness=1)
    shell.pack(fill="both", expand=True)

    # Top accent stripe — two-tone
    stripe = tk.Frame(shell, bg=_t.ACCENT, height=3)
    stripe.pack(fill="x")

    # ── Title bar (draggable) ─────────────────────────────────────
    titlebar = tk.Frame(shell, bg=_t.CARD, height=36)
    titlebar.pack(fill="x")
    titlebar.pack_propagate(False)

    tk.Label(titlebar, text="RIMS  ·  Barangay Edition",
             font=_t.font("Courier", 9, "bold"), fg=_t.MUTED, bg=_t.CARD).pack(side="left", padx=14)

    # Theme toggle button — cycles dark → light → forest → dark
    _THEME_CYCLE = ["dark", "light", "forest"]
    _THEME_ICONS = {"dark": "☀", "light": "🌲", "forest": "☾"}

    def _toggle_theme():
        current = _t.get_current_theme()
        idx = _THEME_CYCLE.index(current) if current in _THEME_CYCLE else 0
        new = _THEME_CYCLE[(idx + 1) % len(_THEME_CYCLE)]
        _t.set_theme(new)
        try:
            users_database.set_theme_preference(new)
        except Exception:
            pass
        root.destroy()
        run_login()

    current_theme = _t.get_current_theme()
    toggle_text = _THEME_ICONS.get(current_theme, "☀")
    toggle_btn = tk.Button(titlebar, text=toggle_text,
                           command=_toggle_theme,
                           bg=_t.CARD, fg=_t.MUTED,
                           activebackground=_t.BORDER, activeforeground=_t.TEXT,
                           font=_t.font("Courier", 10), relief="flat", bd=0,
                           cursor="hand2", width=3)
    toggle_btn.pack(side="right", padx=(0, 2), pady=6, ipady=1)

    # ── Font scale controls (A⁻ / A / A⁺) ────────────────────────
    font_frame = tk.Frame(titlebar, bg=_t.CARD)
    font_frame.pack(side="right", padx=(0, 4), pady=6)

    _FONT_LEVELS = ["small", "medium", "large"]
    _FONT_LABELS = {"small": "A⁻", "medium": "A", "large": "A⁺"}

    def _set_font_scale(level):
        _t.set_font_scale(level)
        try:
            users_database.set_font_scale_preference(level)
        except Exception:
            pass
        root.destroy()
        run_login()

    current_fs = _t.get_font_scale()
    for level in _FONT_LEVELS:
        label = _FONT_LABELS[level]
        is_active = (level == current_fs)
        btn = tk.Button(font_frame, text=label,
                        command=lambda l=level: _set_font_scale(l),
                        bg=_t.ACCENT if is_active else _t.CARD,
                        fg="white" if is_active else _t.MUTED,
                        activebackground=_t.BORDER,
                        activeforeground=_t.TEXT,
                        font=_t.font("Courier", 7, "bold"),
                        relief="flat", bd=0, cursor="hand2",
                        width=2, padx=0, pady=0)
        btn.pack(side="left", padx=1, ipady=1)

    ctrl = tk.Frame(titlebar, bg=_t.CARD)
    ctrl.pack(side="right", padx=(0, 8), pady=6)

    def _min(): root.overrideredirect(False); root.iconify()
    def _close(): root.destroy()

    for sym, cmd, hov in [("─", _min, _t.BORDER), ("✕", _close, _t.DANGER)]:
        b = tk.Button(ctrl, text=sym, command=cmd,
                      bg=_t.CARD, fg=_t.MUTED,
                      activebackground=hov, activeforeground=_t.TEXT,
                      font=_t.font("Courier", 10), relief="flat", bd=0,
                      cursor="hand2", width=3)
        b.pack(side="left", ipady=1)

    def _drag_start(e): root._dx, root._dy = e.x, e.y
    def _drag_move(e):
        root.geometry(f"+{root.winfo_x()+e.x-root._dx}+{root.winfo_y()+e.y-root._dy}")
    titlebar.bind("<ButtonPress-1>", _drag_start)
    titlebar.bind("<B1-Motion>",     _drag_move)

    # ── Body — two column layout ──────────────────────────────────
    body = tk.Frame(shell, bg=_t.BG)
    body.pack(fill="both", expand=True)

    # ── LEFT PANEL ────────────────────────────────────────────────
    left = tk.Frame(body, bg=_t.BG)
    left.pack(side="left", fill="both", expand=True, padx=(36, 18), pady=20)

    # Logo
    logo_canvas = tk.Canvas(left, width=340, height=110,
                            bg=_t.BG, highlightthickness=0)
    logo_canvas.pack(anchor="w")
    _draw_logo(logo_canvas, x=0, y=8, scale=0.72)

    # Divider under logo
    tk.Frame(left, bg=_t.BORDER, height=1).pack(fill="x", pady=(10, 18))

    # Section label
    tk.Label(left, text="▸  SIGN IN TO YOUR ACCOUNT",
             font=_t.font("Courier", 9, "bold"),
             fg=_t.ACCENT, bg=_t.BG).pack(anchor="w", pady=(0, 14))

    # ── Entry factory ─────────────────────────────────────────────
    def make_entry(parent, label, show=None):
        import theme as _t2
        tk.Label(parent, text=label,
                 font=_t.font("Courier", 9, "bold"),
                 fg=_t2.LABEL, bg=_t2.BG).pack(anchor="w")

        wrap = tk.Frame(parent, bg=_t2.PANEL,
                        highlightthickness=1, highlightbackground=_t2.BORDER)
        wrap.pack(fill="x", pady=(4, 14))

        row = tk.Frame(wrap, bg=_t2.PANEL)
        row.pack(fill="x", padx=10, pady=7)

        # Icon prefix
        icon = "\U0001f464" if label == "USERNAME" else "\U0001f512"
        tk.Label(row, text=icon, font=_t.font("Courier", 10),
                 fg=_t2.MUTED, bg=_t2.PANEL).pack(side="left", padx=(0, 6))

        e = tk.Entry(row, show=show, bg=_t2.PANEL, fg=_t2.TEXT,
                     font=_t.font("Courier", 11), relief="flat",
                     insertbackground=_t2.ACCENT, bd=0)
        e.pack(side="left", fill="x", expand=True)

        def _in(ev, w=wrap, r=row, ee=e):
            w.config(highlightbackground=_t2.ACCENT, bg=_t2.BORDER);
            r.config(bg=_t2.BORDER);
            ee.config(bg=_t2.BORDER)
        def _out(ev, w=wrap, r=row, ee=e):
            w.config(highlightbackground=_t2.BORDER, bg=_t2.PANEL);
            r.config(bg=_t2.PANEL);
            ee.config(bg=_t2.PANEL)
        e.bind("<FocusIn>",  _in)
        e.bind("<FocusOut>", _out)
        return e

    username_entry = make_entry(left, "USERNAME")
    password_entry = make_entry(left, "PASSWORD", show="\u25cf")

    # Remember me
    remember_var = tk.BooleanVar()
    rm = tk.Checkbutton(left, text="Remember me",
                        variable=remember_var,
                        font=_t.font("Courier", 9),
                        fg=_t.MUTED, bg=_t.BG,
                        activebackground=_t.BG, activeforeground=_t.TEXT,
                        selectcolor=_t.PANEL,
                        relief="flat", bd=0)
    rm.pack(anchor="w", pady=(0, 16))

    # ── Load remembered credentials ──────────────────────────────
    saved_user, saved_pass = users_database.get_remembered_credentials()
    if saved_user and saved_pass:
        username_entry.insert(0, saved_user)
        password_entry.insert(0, saved_pass)
        remember_var.set(True)

    # ── Login button ──────────────────────────────────────────────
    def login(event=None):
        u = username_entry.get().strip()
        p = password_entry.get().strip()
        if not u or not p:
            messagebox.showwarning("Missing Fields", "Please fill in both fields.")
            return
        status = users_database.check_login_status(u, p)
        if status == "approved":
            # Handle Remember Me
            if remember_var.get():
                users_database.save_remembered_credentials(u, p)
            else:
                users_database.clear_remembered_credentials()
            root.destroy()
            run_purok_window(admin_username=u)
        elif status == "pending":
            messagebox.showwarning(
                "Account Pending",
                "Your account has not been approved yet.\n\n"
                "Please wait for an admin to approve your account."
            )
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    login_btn = tk.Button(left, text="SIGN IN  \u2192",
                          command=login,
                          bg=_t.ACCENT, fg="white",
                          activebackground="#3a7ce8", activeforeground="white",
                          font=_t.font("Courier", 11, "bold"),
                          relief="flat", bd=0, cursor="hand2")
    login_btn.pack(fill="x", ipady=11)

    def _btn_enter(e): login_btn.config(bg="#4a8aee")
    def _btn_leave(e): login_btn.config(bg=_t.ACCENT)
    login_btn.bind("<Enter>", _btn_enter)
    login_btn.bind("<Leave>", _btn_leave)

    # Footer link
    foot = tk.Frame(left, bg=_t.BG)
    foot.pack(anchor="w", pady=(14, 0))
    tk.Label(foot, text="Don't have an account?",
             font=_t.font("Courier", 9), fg=_t.MUTED, bg=_t.BG).pack(side="left")
    tk.Button(foot, text="  Create Account \u2192",
              command=lambda: [root.destroy(), register.run_register(run_login)],
              bg=_t.BG, fg=_t.ACCENT,
              activebackground=_t.BG, activeforeground=_t.TEXT,
              font=_t.font("Courier", 9, "bold"),
              relief="flat", bd=0, cursor="hand2").pack(side="left")

    password_entry.bind("<Return>", login)

    # Admin Panel button (at the bottom of the left panel)
    def open_admin_panel():
        admin_username = username_entry.get().strip()
        admin_password = password_entry.get().strip()

        if not admin_username or not admin_password:
            messagebox.showwarning(
                "Login Required",
                "Enter your admin credentials first, then click Admin Panel."
            )
            return

        # Verify they have admin panel access
        if not users_database.can_access_admin_panel(admin_username):
            messagebox.showerror(
                "Access Denied",
                "Only approved Admins, Barangay Officials, or Staff can access the Admin Panel."
            )
            return

        if not users_database.validate_login(admin_username, admin_password):
            messagebox.showerror("Access Denied", "Invalid credentials.")
            return

        # Open admin panel
        root.withdraw()
        try:
            import admin_panel
            admin_panel.run_admin_panel(admin_username, lambda: _restore_login())
        except ImportError:
            messagebox.showerror("Error", "admin_panel.py not found.")
            root.deiconify()

    def _restore_login():
        root.deiconify()
        root.lift()

    admin_btn_outer = tk.Frame(left, bg=_t.PANEL,
                               highlightthickness=1, highlightbackground=_t.ACCENT2)
    admin_btn_outer.pack(fill="x", pady=(10, 0))
    admin_btn = tk.Button(admin_btn_outer, text="\u2699  ADMIN PANEL",
                          command=open_admin_panel,
                          bg=_t.PANEL, fg=_t.ACCENT2,
                          activebackground=_t.BORDER, activeforeground=_t.TEXT,
                          font=_t.font("Courier", 9, "bold"),
                          relief="flat", bd=0, cursor="hand2", padx=12, pady=7)
    admin_btn.pack()
    def _ad_in(e):  admin_btn_outer.config(highlightbackground=_t.TEXT); admin_btn.config(fg=_t.TEXT)
    def _ad_out(e): admin_btn_outer.config(highlightbackground=_t.ACCENT2);    admin_btn.config(fg=_t.ACCENT2)
    admin_btn.bind("<Enter>", _ad_in); admin_btn.bind("<Leave>", _ad_out)

    # ── RIGHT PANEL — dashboard with charts ────────────────────────
    right = tk.Frame(body, bg=_t.CARD, width=280,
                     highlightthickness=1, highlightbackground=_t.BORDER)
    right.pack(side="right", fill="y", padx=(0, 28), pady=28)
    right.pack_propagate(False)

    # Scrollable chart area
    chart_canvas = tk.Canvas(right, bg=_t.CARD, highlightthickness=0)
    chart_scroll = tk.Scrollbar(right, orient="vertical",
                                 bg=_t.BORDER, troughcolor=_t.CARD,
                                 width=4, relief="flat", highlightthickness=0)
    chart_canvas.pack(side="left", fill="both", expand=True)
    chart_scroll.pack(side="right", fill="y")
    chart_canvas.configure(yscrollcommand=chart_scroll.set)
    chart_scroll.config(command=chart_canvas.yview)

    chart_inner = tk.Frame(chart_canvas, bg=_t.CARD)
    chart_inner_id = chart_canvas.create_window((0, 0), window=chart_inner,
                                                 anchor="nw", width=265)

    def _configure_chart_inner(event):
        chart_canvas.configure(scrollregion=chart_canvas.bbox("all"))
        chart_canvas.itemconfig(chart_inner_id, width=event.width)
    chart_inner.bind("<Configure>", _configure_chart_inner)

    def _on_mousewheel(event):
        chart_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    chart_canvas.bind("<Enter>",
                       lambda e: chart_canvas.bind_all("<MouseWheel>", _on_mousewheel))
    chart_canvas.bind("<Leave>",
                       lambda e: chart_canvas.unbind_all("<MouseWheel>"))

    tk.Frame(chart_inner, bg=_t.ACCENT2, height=3).pack(fill="x")

    tk.Label(chart_inner, text="\u25b8  DASHBOARD",
             font=_t.font("Courier", 9, "bold"),
             fg=_t.ACCENT, bg=_t.CARD).pack(anchor="w", padx=16, pady=(12, 2))

    tk.Frame(chart_inner, bg=_t.BORDER, height=1).pack(fill="x", padx=16, pady=(0, 10))

    dashboard = database.get_full_dashboard_stats()

    def draw_stat_card(parent, title, value, color):
        card = tk.Frame(parent, bg=_t.PANEL,
                        highlightthickness=1, highlightbackground=_t.BORDER)
        card.pack(fill="x", padx=14, pady=3)
        tk.Label(card, text=title, font=_t.font("Courier", 7, "bold"),
                 fg=_t.LABEL, bg=_t.PANEL).pack(anchor="w", padx=10, pady=(5, 0))
        tk.Label(card, text=str(value), font=_t.font("Courier", 14, "bold"),
                 fg=color, bg=_t.PANEL).pack(anchor="w", padx=10, pady=(0, 5))

    # Quick stats row
    quick = tk.Frame(chart_inner, bg=_t.CARD)
    quick.pack(fill="x", padx=14, pady=2)
    left_q = tk.Frame(quick, bg=_t.CARD)
    left_q.pack(side="left", fill="x", expand=True)
    right_q = tk.Frame(quick, bg=_t.CARD)
    right_q.pack(side="right", fill="x", expand=True)
    draw_stat_card(left_q,  "TOTAL RESIDENTS", dashboard["total"], _t.SUCCESS)
    draw_stat_card(right_q, "PUROKS",          dashboard["puroks"], _t.ACCENT)

    # ── Chart drawing helpers ────────────────────────────────────
    BAR_MAX_W = 168
    BAR_H     = 14
    BAR_GAP   = 20
    PAD_LEFT  = 56
    PAD_TOP   = 4
    CHART_H   = 14  # header height

    chart_colors = {
        "Registered": _t.SUCCESS,
        "Pending":    _t.WARN,
        "Inactive":   _t.DANGER,
        "Male":       "#5b9bff",
        "Female":     "#fc5cbc",
        "Other":      _t.MUTED,
        "0-17":       _t.ACCENT,
        "18-30":      "#5b9bff",
        "31-45":      _t.ACCENT2,
        "46-60":      _t.WARN,
        "60+":        _t.DANGER,
    }

    def draw_hbar_chart(parent, title, data, icon="\U0001f4ca"):
        """Draw a horizontal bar chart directly on a Canvas widget."""
        if not data:
            data = [("No data", 0)]

        # Chart container
        chart_frame = tk.Frame(parent, bg=_t.CARD)
        chart_frame.pack(fill="x", padx=14, pady=(8, 2))

        # Title
        tk.Label(chart_frame, text=f"{icon}  {title}",
                 font=_t.font("Courier", 8, "bold"),
                 fg=_t.LABEL, bg=_t.CARD).pack(anchor="w")

        max_val = max(d[1] for d in data) or 1
        canvas_w = 245
        canvas_h = PAD_TOP + CHART_H + len(data) * BAR_GAP + 6

        cv = tk.Canvas(chart_frame, width=canvas_w, height=canvas_h,
                       bg=_t.CARD, highlightthickness=0)
        cv.pack()

        # Y-axis baseline
        baseline_x = PAD_LEFT - 4
        cv.create_line(baseline_x, PAD_TOP + CHART_H - 4,
                       baseline_x, PAD_TOP + CHART_H + len(data) * BAR_GAP,
                       fill=_t.BORDER, width=1)

        for i, (label, val) in enumerate(data):
            y0 = PAD_TOP + CHART_H + i * BAR_GAP
            bar_w = int((val / max_val) * BAR_MAX_W) if max_val > 0 else 0
            if bar_w < 2 and val > 0:
                bar_w = 2  # minimum visible bar

            color = chart_colors.get(label, _t.ACCENT)

            # Label text
            cv.create_text(PAD_LEFT - 6, y0 + BAR_H // 2,
                           text=label, font=_t.font("Courier", 7, "bold"),
                           fill=_t.MUTED, anchor="e")

            # Bar
            if bar_w > 0:
                cv.create_rectangle(baseline_x + 2, y0 + 2,
                                    baseline_x + 2 + bar_w, y0 + BAR_H - 2,
                                    fill=color, outline="", width=0)
                # Value label at end of bar
                cv.create_text(baseline_x + 4 + bar_w, y0 + BAR_H // 2,
                               text=str(val), font=_t.font("Courier", 8, "bold"),
                               fill=color, anchor="w")

            # Grid line
            cv.create_line(baseline_x, y0 + BAR_H + 2,
                           baseline_x + BAR_MAX_W + 4, y0 + BAR_H + 2,
                           fill=_t.BORDER, width=1)

    # ── Status Distribution ───────────────────────────────────────
    draw_hbar_chart(chart_inner, "Status Distribution",
                    dashboard["status"], icon="\u25cf")

    # ── Gender Distribution ───────────────────────────────────────
    draw_hbar_chart(chart_inner, "Gender Distribution",
                    dashboard["gender"], icon="\U0001f464")

    # ── Age Group Distribution ────────────────────────────────────
    draw_hbar_chart(chart_inner, "Age Groups",
                    dashboard["age_groups"], icon="\U0001f4c5")

    # ── Footer spacer ─────────────────────────────────────────────
    tk.Frame(chart_inner, bg=_t.CARD, height=6).pack()
    tk.Frame(chart_inner, bg=_t.BORDER, height=1).pack(fill="x", padx=16)
    tk.Label(chart_inner,
             text="\u00a9 Created by: Reynald & Arl",
             font=_t.font("Courier", 7),
             fg=_t.MUTED, bg=_t.CARD).pack(pady=8)

    # Refresh dashboard button
    refresh_btn = tk.Button(chart_inner, text="\u21bb  Refresh",
                            font=_t.font("Courier", 7, "bold"),
                            bg=_t.PANEL, fg=_t.ACCENT,
                            activebackground=_t.ACCENT, activeforeground="white",
                            relief="flat", bd=0, cursor="hand2",
                            padx=10, pady=3)
    refresh_btn.pack(pady=(0, 6))

    def _refresh_dashboard():
        """Rebuild all dashboard stat cards and charts in place."""
        # Collect all children to remove except title and separator
        to_remove = []
        for w in chart_inner.winfo_children():
            if w not in (refresh_btn,):
                to_remove.append(w)
        for w in to_remove:
            w.destroy()

        # Rebuild everything
        tk.Frame(chart_inner, bg=_t.ACCENT2, height=3).pack(fill="x")
        tk.Label(chart_inner, text="\u25b8  DASHBOARD",
                 font=_t.font("Courier", 9, "bold"),
                 fg=_t.ACCENT, bg=_t.CARD).pack(anchor="w", padx=16, pady=(12, 2))
        tk.Frame(chart_inner, bg=_t.BORDER, height=1).pack(fill="x", padx=16, pady=(0, 10))

        dash = database.get_full_dashboard_stats()

        quick = tk.Frame(chart_inner, bg=_t.CARD)
        quick.pack(fill="x", padx=14, pady=2)
        left_q = tk.Frame(quick, bg=_t.CARD)
        left_q.pack(side="left", fill="x", expand=True)
        right_q = tk.Frame(quick, bg=_t.CARD)
        right_q.pack(side="right", fill="x", expand=True)
        draw_stat_card(left_q,  "TOTAL RESIDENTS", dash["total"], _t.SUCCESS)
        draw_stat_card(right_q, "PUROKS",          dash["puroks"], _t.ACCENT)

        draw_hbar_chart(chart_inner, "Status Distribution", dash["status"], icon="\u25cf")
        draw_hbar_chart(chart_inner, "Gender Distribution", dash["gender"], icon="\U0001f464")
        draw_hbar_chart(chart_inner, "Age Groups", dash["age_groups"], icon="\U0001f4c5")

        tk.Frame(chart_inner, bg=_t.CARD, height=6).pack()
        tk.Frame(chart_inner, bg=_t.BORDER, height=1).pack(fill="x", padx=16)
        tk.Label(chart_inner, text="\u00a9 Created by: Reynald & Arl",
                 font=_t.font("Courier", 7), fg=_t.MUTED, bg=_t.CARD).pack(pady=8)

        refresh_btn.pack(pady=(0, 6))

    refresh_btn.config(command=_refresh_dashboard)

    # Mousewheel scroll on right panel
    def _scroll_charts(event):
        chart_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    right.bind("<Enter>",
               lambda e: right.bind_all("<MouseWheel>", _scroll_charts))
    right.bind("<Leave>",
               lambda e: right.unbind_all("<MouseWheel>"))

    root.mainloop()


if __name__ == "__main__":
    run_login()
