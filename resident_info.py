import tkinter as tk
from tkinter import messagebox
from datetime import datetime, date
import os

try:
    from PIL import Image, ImageTk, ImageDraw
    PIL_OK = True
except ImportError:
    PIL_OK = False

# ── Palette ───────────────────────────────────────────────────────────────────
BG      = "#0b0d14"
CARD    = "#11141f"
PANEL   = "#181c2a"
BORDER  = "#252c42"
ACCENT  = "#4f8ef7"
ACCENT2 = "#7c5cfc"
SUCCESS = "#4fc97e"
DANGER  = "#f74f6a"
WARN    = "#f7a94f"
TEXT    = "#e8ecf4"
MUTED   = "#6b7490"


def _make_circle_photo(path, size=180):
    """Load and crop an image to a circle. Returns ImageTk.PhotoImage or None."""
    if not PIL_OK or not path or not os.path.exists(path):
        return None
    try:
        img = Image.open(path).convert("RGBA")
        img = img.resize((size, size), Image.LANCZOS)

        # Create circular mask
        mask = Image.new("L", (size, size), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, size, size), fill=255)

        result = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        result.paste(img, (0, 0), mask)
        return ImageTk.PhotoImage(result)
    except Exception:
        return None


def _make_avatar(name, size=180):
    """Generate a letter-based avatar when no photo exists."""
    if not PIL_OK:
        return None
    try:
        initials = "".join(w[0].upper() for w in name.split() if w)[:2]
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))

        # Circle background
        mask = Image.new("L", (size, size), 0)
        draw_m = ImageDraw.Draw(mask)
        draw_m.ellipse((0, 0, size, size), fill=255)

        bg_layer = Image.new("RGBA", (size, size), (79, 142, 247, 255))  # ACCENT
        img.paste(bg_layer, (0, 0), mask)

        # Draw initials
        draw = ImageDraw.Draw(img)
        try:
            from PIL import ImageFont
            fnt = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                size // 3)
        except Exception:
            fnt = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), initials, font=fnt)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text(((size - tw) // 2, (size - th) // 2 - 4),
                  initials, font=fnt, fill="white")
        return ImageTk.PhotoImage(img)
    except Exception:
        return None


def open_resident_info(parent, resident_row, purok_name,
                       on_close=None):
    """
    Opens a styled resident info window.

    resident_row = (id, first_name, last_name, age, contact,
                    purok_id, gender, birthdate, status, photo_path)
    """
    (rid, fn, ln, age, contact,
     purok_id, gender, birthdate, status, photo_path) = resident_row

    full_name = f"{fn} {ln}"

    win = tk.Toplevel(parent)
    win.title(f"Resident Info — {full_name}")
    win.configure(bg=BG)
    win.geometry("680x580")
    win.minsize(580, 500)
    win.resizable(True, True)

    win.update_idletasks()
    sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
    win.geometry(f"680x580+{(sw-680)//2}+{(sh-580)//2}")

    win.grab_set()

    # ── Top accent stripe ─────────────────────────────────────────
    tk.Frame(win, bg=ACCENT, height=3).pack(fill="x")

    # ── Header bar ────────────────────────────────────────────────
    hdr = tk.Frame(win, bg=CARD,
                   highlightthickness=1, highlightbackground=BORDER)
    hdr.pack(fill="x", padx=0, pady=0)

    tk.Label(hdr, text="▸  RESIDENT PROFILE",
             font=("Courier", 9, "bold"),
             fg=ACCENT, bg=CARD).pack(side="left", padx=16, pady=10)

    # Status badge in header
    st_color = {
        "Registered": SUCCESS,
        "Pending":    WARN,
        "Inactive":   DANGER,
    }.get(status, MUTED)

    st_badge = tk.Frame(hdr, bg=st_color, padx=10, pady=3)
    st_badge.pack(side="right", padx=16, pady=8)
    tk.Label(st_badge, text=status.upper(),
             font=("Courier", 8, "bold"),
             fg="white", bg=st_color).pack()

    # ── Body: photo left | details right ──────────────────────────
    body = tk.Frame(win, bg=BG)
    body.pack(fill="both", expand=True, padx=20, pady=16)
    body.grid_columnconfigure(1, weight=1)
    body.grid_rowconfigure(0, weight=1)

    # ── LEFT: Photo panel ─────────────────────────────────────────
    left = tk.Frame(body, bg=CARD,
                    highlightthickness=1, highlightbackground=BORDER)
    left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

    tk.Frame(left, bg=ACCENT2, height=3).pack(fill="x")

    photo_frame = tk.Frame(left, bg=CARD)
    photo_frame.pack(pady=24, padx=20)

    # Photo or avatar
    _photo_img = [None]

    def _load_photo(path=None):
        for w in photo_frame.winfo_children():
            w.destroy()

        p = path or photo_path
        img = _make_circle_photo(p, size=160) or _make_avatar(full_name, size=160)

        if img:
            _photo_img[0] = img
            lbl = tk.Label(photo_frame, image=img, bg=CARD)
            lbl.pack()
        else:
            # Fallback plain circle
            c = tk.Canvas(photo_frame, width=160, height=160,
                          bg=CARD, highlightthickness=0)
            c.create_oval(5, 5, 155, 155, fill=PANEL, outline=BORDER, width=2)
            c.create_text(80, 80, text="👤",
                          font=("Segoe UI Emoji", 40), fill=MUTED)
            c.pack()

    _load_photo()

    # Name under photo
    tk.Label(left, text=full_name,
             font=("Georgia", 14, "bold"),
             fg=TEXT, bg=CARD,
             wraplength=180, justify="center").pack(pady=(6, 2), padx=10)

    tk.Label(left, text=f"ID: {rid:03d}",
             font=("Courier", 9),
             fg=MUTED, bg=CARD).pack()

    tk.Label(left, text=f"Purok: {purok_name}",
             font=("Courier", 8),
             fg=ACCENT, bg=CARD).pack(pady=(2, 16))

    # ── RIGHT: Details panel ──────────────────────────────────────
    right = tk.Frame(body, bg=CARD,
                     highlightthickness=1, highlightbackground=BORDER)
    right.grid(row=0, column=1, sticky="nsew")
    right.grid_columnconfigure(1, weight=1)

    tk.Frame(right, bg=ACCENT, height=3).pack(fill="x")

    details_inner = tk.Frame(right, bg=CARD)
    details_inner.pack(fill="both", expand=True, padx=20, pady=16)

    def detail_row(parent, label, value, value_color=TEXT, row=0):
        tk.Label(parent, text=label,
                 font=("Courier", 8, "bold"),
                 fg=MUTED, bg=CARD,
                 width=14, anchor="w").grid(
                     row=row, column=0, sticky="w", pady=6)
        tk.Label(parent, text=str(value) if value else "—",
                 font=("Courier", 11, "bold"),
                 fg=value_color, bg=CARD,
                 anchor="w").grid(
                     row=row, column=1, sticky="w", padx=(8, 0), pady=6)

    tk.Label(details_inner, text="▸  PERSONAL INFORMATION",
             font=("Courier", 8, "bold"),
             fg=ACCENT, bg=CARD).grid(
                 row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))

    detail_row(details_inner, "Full Name",  full_name,  TEXT,    row=1)
    detail_row(details_inner, "Age",        f"{age} yrs", ACCENT2, row=2)
    detail_row(details_inner, "Birthday",   birthdate,  TEXT,    row=3)
    detail_row(details_inner, "Gender",     gender,     TEXT,    row=4)

    tk.Frame(details_inner, bg=BORDER, height=1).grid(
        row=5, column=0, columnspan=2, sticky="ew", pady=10)

    tk.Label(details_inner, text="▸  CONTACT & STATUS",
             font=("Courier", 8, "bold"),
             fg=ACCENT, bg=CARD).grid(
                 row=6, column=0, columnspan=2, sticky="w", pady=(0, 8))

    detail_row(details_inner, "Contact",    contact,    SUCCESS, row=7)
    detail_row(details_inner, "Status",     status,     st_color, row=8)
    detail_row(details_inner, "Purok",      purok_name, ACCENT,  row=9)

    # ── Age bar (visual) ──────────────────────────────────────────
    tk.Frame(details_inner, bg=BORDER, height=1).grid(
        row=10, column=0, columnspan=2, sticky="ew", pady=10)

    try:
        age_int = int(age)
        tk.Label(details_inner, text="▸  AGE INDICATOR",
                 font=("Courier", 8, "bold"),
                 fg=ACCENT, bg=CARD).grid(
                     row=11, column=0, columnspan=2, sticky="w", pady=(0, 6))

        bar_frame = tk.Frame(details_inner, bg=PANEL,
                             highlightthickness=1, highlightbackground=BORDER,
                             height=16)
        bar_frame.grid(row=12, column=0, columnspan=2, sticky="ew", pady=(0, 2))
        bar_frame.grid_propagate(False)

        pct = min(age_int / 100, 1.0)
        bar_color = (SUCCESS if age_int < 18 else
                     ACCENT   if age_int < 60 else ACCENT2)

        def _draw_bar(e=None):
            bar_frame.update_idletasks()
            w = int(bar_frame.winfo_width() * pct)
            for c in bar_frame.winfo_children():
                c.destroy()
            tk.Frame(bar_frame, bg=bar_color, width=w,
                     height=16).place(x=0, y=0)

        bar_frame.bind("<Configure>", _draw_bar)
        win.after(100, _draw_bar)

        category = ("Child (0–17)"   if age_int < 18 else
                    "Adult (18–59)"  if age_int < 60 else
                    "Senior (60+)")
        tk.Label(details_inner, text=f"{age_int} yrs · {category}",
                 font=("Courier", 8),
                 fg=bar_color, bg=CARD).grid(
                     row=13, column=0, columnspan=2, sticky="w")
    except (ValueError, TypeError):
        pass

    # ── Footer buttons ────────────────────────────────────────────
    footer = tk.Frame(win, bg=BG)
    footer.pack(fill="x", padx=20, pady=(0, 16))

    tk.Button(footer, text="✕  Close",
              command=win.destroy,
              bg=PANEL, fg=MUTED,
              activebackground=BORDER, activeforeground=TEXT,
              font=("Courier", 9, "bold"),
              relief="flat", bd=0, cursor="hand2").pack(
                  side="right", ipady=7, ipadx=16)

    if on_close:
        win.protocol("WM_DELETE_WINDOW", lambda: (on_close(), win.destroy()))