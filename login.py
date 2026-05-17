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


# ── Palette — lighter but same theme ─────────────────────────────────────────
BG      = "#1c2030"   # was #0d0f14 — now a visible navy-slate
CARD    = "#252a3a"   # was #13161e — lifted noticeably
PANEL   = "#2d3347"   # was #1a1e2b — much easier on entries
BORDER  = "#4a5270"   # was #2a2f42 — borders now visible
ACCENT  = "#5b9bff"   # slightly brighter blue
ACCENT2 = "#9270ff"   # slightly brighter violet
SUCCESS = "#52d98a"   # brighter green
DANGER  = "#ff5c78"
TEXT    = "#f0f4ff"   # near-white, crisper
MUTED   = "#9ba8c8"   # was #6b7490 — much more readable muted text
LABEL   = "#c8d0e8"   # new: for form labels, between MUTED and TEXT


# ── Inline logo drawing ───────────────────────────────────────────────────────
def _draw_logo(canvas, x=0, y=0, scale=1.0):
    ox, oy = x, y
    def s(v): return v * scale
    def pt(px, py): return ox + s(px), oy + s(py)

    outer = [ox+s(42), oy+s(0),  ox+s(84), oy+s(24),
             ox+s(84), oy+s(72), ox+s(42), oy+s(96),
             ox+s(0),  oy+s(72), ox+s(0),  oy+s(24)]
    canvas.create_polygon(outer, fill="", outline=BORDER, width=max(1, int(1.5*scale)))

    inner = [ox+s(42), oy+s(12), ox+s(76), oy+s(30),
             ox+s(76), oy+s(66), ox+s(42), oy+s(84),
             ox+s(8),  oy+s(66), ox+s(8),  oy+s(30)]
    canvas.create_polygon(inner, fill=CARD, outline=BORDER, width=max(1, int(scale)))

    for ly in [s(42), s(54), s(66)]:
        canvas.create_line(ox+s(15), oy+ly, ox+s(69), oy+ly, fill=BORDER, width=1)

    nodes = {
        "top": pt(42, 30), "ml": pt(27, 24), "mr": pt(57, 24),
        "cl":  pt(27, 54), "cr": pt(57, 54), "bot": pt(42, 66),
    }
    for a, b in [("ml","top"),("top","mr"),("ml","cl"),("mr","cr"),
                 ("cl","bot"),("cr","bot"),("top","bot"),("cl","cr")]:
        canvas.create_line(*nodes[a], *nodes[b], fill=BORDER, width=max(1, int(scale)))

    def dot(k, col, r=5):
        cx, cy = nodes[k]; r = s(r)
        canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill=col, outline="")

    dot("top", ACCENT, 5);  dot("ml", ACCENT, 3.5); dot("mr", ACCENT, 3.5)
    dot("cl", ACCENT2, 3.5); dot("cr", ACCENT2, 3.5); dot("bot", SUCCESS, 5)

    for px, py, col in [(84,24,ACCENT),(0,72,SUCCESS)]:
        cx,cy = ox+s(px), oy+s(py); r=s(4)
        canvas.create_oval(cx-r,cy-r,cx+r,cy+r, fill=col, outline="", stipple="gray50")

    divx = ox + s(100)
    canvas.create_line(divx, oy+s(4), divx, oy+s(92), fill=BORDER, width=1)

    wx, wy = ox+s(112), oy+s(60)
    fs = max(10, int(36*scale))
    canvas.create_text(wx,                           wy, text="R",  font=("Georgia", fs, "bold"),        fill=TEXT,   anchor="w")
    canvas.create_text(wx+int(fs*.68),               wy, text="I",  font=("Georgia", fs, "bold italic"),  fill=ACCENT, anchor="w")
    canvas.create_text(wx+int(fs*.68)+int(fs*.38),   wy, text="MS", font=("Georgia", fs, "bold"),        fill=TEXT,   anchor="w")

    canvas.create_line(wx, oy+s(68), wx+s(160), oy+s(68), fill=ACCENT, width=max(1,int(2*scale)))
    canvas.create_text(wx, oy+s(80),
                       text="RESIDENT INFORMATION MANAGEMENT SYSTEM",
                       font=("Courier", max(7, int(8*scale))),
                       fill=MUTED, anchor="w")


# ── Main login window ─────────────────────────────────────────────────────────
def run_login():
    users_database.create_users_table()
    database.create_tables()

    if platform.system() == "Windows":
        _set_app_user_model_id("com.rims.barangay")

    WIN_W, WIN_H = 780, 540
    root = tk.Tk()
    root.title("RIMS — Login")
    root.configure(bg=BG)
    root.resizable(False, False)
    root.overrideredirect(True)

    sx, sy = root.winfo_screenwidth(), root.winfo_screenheight()
    root.geometry(f"{WIN_W}x{WIN_H}+{(sx-WIN_W)//2}+{(sy-WIN_H)//2}")
    root.update_idletasks()
    _ensure_taskbar_entry(root)

    # ── Outer border shell ────────────────────────────────────────
    shell = tk.Frame(root, bg=BG,
                     highlightbackground=BORDER, highlightthickness=1)
    shell.pack(fill="both", expand=True)

    # Top accent stripe — two-tone
    stripe = tk.Frame(shell, bg=ACCENT, height=3)
    stripe.pack(fill="x")

    # ── Title bar (draggable) ─────────────────────────────────────
    titlebar = tk.Frame(shell, bg=CARD, height=36)
    titlebar.pack(fill="x")
    titlebar.pack_propagate(False)

    tk.Label(titlebar, text="RIMS  ·  Barangay Edition",
             font=("Courier", 9, "bold"), fg=MUTED, bg=CARD).pack(side="left", padx=14)

    ctrl = tk.Frame(titlebar, bg=CARD)
    ctrl.pack(side="right", padx=8, pady=6)

    def _min(): root.overrideredirect(False); root.iconify()
    def _close(): root.destroy()

    for sym, cmd, hov in [("─", _min, BORDER), ("✕", _close, DANGER)]:
        b = tk.Button(ctrl, text=sym, command=cmd,
                      bg=CARD, fg=MUTED,
                      activebackground=hov, activeforeground=TEXT,
                      font=("Courier", 10), relief="flat", bd=0,
                      cursor="hand2", width=3)
        b.pack(side="left", ipady=1)

    def _drag_start(e): root._dx, root._dy = e.x, e.y
    def _drag_move(e):
        root.geometry(f"+{root.winfo_x()+e.x-root._dx}+{root.winfo_y()+e.y-root._dy}")
    titlebar.bind("<ButtonPress-1>", _drag_start)
    titlebar.bind("<B1-Motion>",     _drag_move)

    # ── Body — two column layout ──────────────────────────────────
    body = tk.Frame(shell, bg=BG)
    body.pack(fill="both", expand=True)

    # ── LEFT PANEL ────────────────────────────────────────────────
    left = tk.Frame(body, bg=BG)
    left.pack(side="left", fill="both", expand=True, padx=(36, 18), pady=20)

    # Logo
    logo_canvas = tk.Canvas(left, width=340, height=110,
                            bg=BG, highlightthickness=0)
    logo_canvas.pack(anchor="w")
    _draw_logo(logo_canvas, x=0, y=8, scale=0.72)

    # Divider under logo
    tk.Frame(left, bg=BORDER, height=1).pack(fill="x", pady=(10, 18))

    # Section label
    tk.Label(left, text="▸  SIGN IN TO YOUR ACCOUNT",
             font=("Courier", 9, "bold"),
             fg=ACCENT, bg=BG).pack(anchor="w", pady=(0, 14))

    # ── Entry factory ─────────────────────────────────────────────
    def make_entry(parent, label, show=None):
        tk.Label(parent, text=label,
                 font=("Courier", 9, "bold"),
                 fg=LABEL, bg=BG).pack(anchor="w")

        wrap = tk.Frame(parent, bg=PANEL,
                        highlightthickness=1, highlightbackground=BORDER)
        wrap.pack(fill="x", pady=(4, 14))

        row = tk.Frame(wrap, bg=PANEL)
        row.pack(fill="x", padx=10, pady=7)

        # Icon prefix
        icon = "👤" if label == "USERNAME" else "🔒"
        tk.Label(row, text=icon, font=("Courier", 10),
                 fg=MUTED, bg=PANEL).pack(side="left", padx=(0, 6))

        e = tk.Entry(row, show=show, bg=PANEL, fg=TEXT,
                     font=("Courier", 11), relief="flat",
                     insertbackground=ACCENT, bd=0)
        e.pack(side="left", fill="x", expand=True)

        def _in(ev):  wrap.config(highlightbackground=ACCENT, bg="#333d57"); row.config(bg="#333d57"); e.config(bg="#333d57")
        def _out(ev): wrap.config(highlightbackground=BORDER, bg=PANEL);     row.config(bg=PANEL);     e.config(bg=PANEL)
        e.bind("<FocusIn>",  _in)
        e.bind("<FocusOut>", _out)
        return e

    username_entry = make_entry(left, "USERNAME")
    password_entry = make_entry(left, "PASSWORD", show="●")

    # Remember me
    remember_var = tk.BooleanVar()
    rm = tk.Checkbutton(left, text="Remember me",
                        variable=remember_var,
                        font=("Courier", 9),
                        fg=MUTED, bg=BG,
                        activebackground=BG, activeforeground=TEXT,
                        selectcolor=PANEL,
                        relief="flat", bd=0)
    rm.pack(anchor="w", pady=(0, 16))

    # ── Login button ──────────────────────────────────────────────
    def login(event=None):
        u = username_entry.get().strip()
        p = password_entry.get().strip()
        if not u or not p:
            messagebox.showwarning("Missing Fields", "Please fill in both fields.")
            return
        if users_database.validate_login(u, p):
            root.destroy()
            run_purok_window()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    login_btn = tk.Button(left, text="SIGN IN  →",
                          command=login,
                          bg=ACCENT, fg="white",
                          activebackground="#3a7ce8", activeforeground="white",
                          font=("Courier", 11, "bold"),
                          relief="flat", bd=0, cursor="hand2")
    login_btn.pack(fill="x", ipady=11)

    def _btn_enter(e): login_btn.config(bg="#4a8aee")
    def _btn_leave(e): login_btn.config(bg=ACCENT)
    login_btn.bind("<Enter>", _btn_enter)
    login_btn.bind("<Leave>", _btn_leave)

    # Footer link
    foot = tk.Frame(left, bg=BG)
    foot.pack(anchor="w", pady=(14, 0))
    tk.Label(foot, text="Don't have an account?",
             font=("Courier", 9), fg=MUTED, bg=BG).pack(side="left")
    tk.Button(foot, text="  Create Account →",
              command=lambda: [root.destroy(), register.run_register(run_login)],
              bg=BG, fg=ACCENT,
              activebackground=BG, activeforeground=TEXT,
              font=("Courier", 9, "bold"),
              relief="flat", bd=0, cursor="hand2").pack(side="left")

    password_entry.bind("<Return>", login)

    # ── RIGHT PANEL — system overview ─────────────────────────────
    right = tk.Frame(body, bg=CARD, width=230,
                     highlightthickness=1, highlightbackground=BORDER)
    right.pack(side="right", fill="y", padx=(0, 28), pady=28)
    right.pack_propagate(False)

    tk.Frame(right, bg=ACCENT2, height=3).pack(fill="x")

    tk.Label(right, text="▸  SYSTEM OVERVIEW",
             font=("Courier", 8, "bold"),
             fg=ACCENT, bg=CARD).pack(anchor="w", padx=16, pady=(14, 4))

    tk.Frame(right, bg=BORDER, height=1).pack(fill="x", padx=16, pady=(0, 10))

    total_residents = database.count_residents()
    total_puroks    = database.count_puroks()
    pending_updates = 0
    last_sync       = datetime.now().strftime("%b %d, %Y")

    stats = [
        ("Total Residents",   str(total_residents), SUCCESS),
        ("Registered Puroks", str(total_puroks),    ACCENT),
        ("Pending Updates",   str(pending_updates), MUTED),
        ("Last Sync",         last_sync,            MUTED),
    ]

    for label, value, val_color in stats:
        row = tk.Frame(right, bg=PANEL,
                       highlightthickness=1, highlightbackground=BORDER)
        row.pack(fill="x", padx=14, pady=4)
        tk.Label(row, text=label,
                 font=("Courier", 8, "bold"),
                 fg=LABEL, bg=PANEL).pack(anchor="w", padx=10, pady=(7, 0))
        tk.Label(row, text=value,
                 font=("Courier", 14, "bold"),
                 fg=val_color, bg=PANEL).pack(anchor="w", padx=10, pady=(0, 7))

    tk.Frame(right, bg=CARD).pack(fill="both", expand=True)

    tk.Frame(right, bg=BORDER, height=1).pack(fill="x", padx=16)
    tk.Label(right,
             text="© Created by: Reynald & Arl",
             font=("Courier", 7),
             fg=MUTED, bg=CARD).pack(pady=10)

    root.mainloop()


if __name__ == "__main__":
    run_login()