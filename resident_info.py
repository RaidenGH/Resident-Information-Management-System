import tkinter as tk
from tkinter import messagebox, filedialog
from datetime import datetime, date
import os
import shutil

try:
    from PIL import Image, ImageTk, ImageDraw, ImageFilter
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

PHOTOS_DIR = "resident_photos"


def _ensure_photos_dir():
    os.makedirs(PHOTOS_DIR, exist_ok=True)


def _make_circle_photo(path, size=200):
    if not PIL_OK or not path or not os.path.exists(path):
        return None
    try:
        img = Image.open(path).convert("RGBA")

        # Smart crop to square from center
        w, h = img.size
        m = min(w, h)
        left  = (w - m) // 2
        top   = (h - m) // 2
        img   = img.crop((left, top, left + m, top + m))
        img   = img.resize((size, size), Image.LANCZOS)

        # Circular mask
        mask = Image.new("L", (size, size), 0)
        ImageDraw.Draw(mask).ellipse((0, 0, size, size), fill=255)
        result = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        result.paste(img, (0, 0), mask)
        return ImageTk.PhotoImage(result)
    except Exception:
        return None


def _make_avatar(name, size=200):
    if not PIL_OK:
        return None
    try:
        initials = "".join(w[0].upper() for w in name.split() if w)[:2]
        img  = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        mask = Image.new("L",    (size, size), 0)
        ImageDraw.Draw(mask).ellipse((0, 0, size, size), fill=255)

        # Gradient-like bg: blend two colors
        bg = Image.new("RGBA", (size, size), (79, 142, 247, 255))
        img.paste(bg, (0, 0), mask)

        draw = ImageDraw.Draw(img)
        try:
            from PIL import ImageFont
            fnt = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                size // 3)
        except Exception:
            fnt = ImageFont.load_default()

        bb = draw.textbbox((0, 0), initials, font=fnt)
        tw, th = bb[2] - bb[0], bb[3] - bb[1]
        draw.text(((size - tw) // 2, (size - th) // 2 - 4),
                  initials, font=fnt, fill="white")
        return ImageTk.PhotoImage(img)
    except Exception:
        return None


def _make_ring(size=200, color="#4f8ef7", thickness=3):
    """Draw a colored ring to surround the photo."""
    if not PIL_OK:
        return None
    try:
        s = size + thickness * 2 + 4
        img  = Image.new("RGBA", (s, s), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.ellipse((0, 0, s - 1, s - 1), outline=color, width=thickness)
        return ImageTk.PhotoImage(img)
    except Exception:
        return None


def open_resident_info(parent, resident_row, purok_name,
                       on_close=None, on_photo_updated=None):
    """
    resident_row = (id, fn, ln, age, contact,
                    purok_id, gender, birthdate, status, photo_path)
    on_photo_updated(new_path) — called when user changes the photo
    """
    _ensure_photos_dir()

    row = list(resident_row) + [""] * max(0, 10 - len(resident_row))
    (rid, fn, ln, age, contact,
     purok_id, gender, birthdate, status, photo_path) = row[:10]

    full_name  = f"{fn} {ln}"
    _cur_photo = [photo_path]

    st_color = {"Registered": SUCCESS,
                "Pending":    WARN,
                "Inactive":   DANGER}.get(status, MUTED)

    # ── Window ────────────────────────────────────────────────────
    win = tk.Toplevel(parent)
    win.title(f"Profile — {full_name}")
    win.configure(bg=BG)
    win.geometry("740x600")
    win.minsize(640, 520)
    win.resizable(True, True)
    win.update_idletasks()
    sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
    win.geometry(f"740x600+{(sw-740)//2}+{(sh-600)//2}")
    win.grab_set()

    # ── Top accent stripe (gradient-like two-tone) ────────────────
    stripe = tk.Frame(win, bg=ACCENT, height=3)
    stripe.pack(fill="x")

    # ── Header ────────────────────────────────────────────────────
    hdr = tk.Frame(win, bg=CARD,
                   highlightthickness=1, highlightbackground=BORDER)
    hdr.pack(fill="x")

    tk.Label(hdr, text="▸  RESIDENT PROFILE",
             font=("Courier", 9, "bold"),
             fg=ACCENT, bg=CARD).pack(side="left", padx=16, pady=10)

    # ID chip
    tk.Label(hdr, text=f"  ID {rid:03d}  ",
             font=("Courier", 8, "bold"),
             fg=MUTED, bg=PANEL).pack(side="left", pady=10)

    # Status badge
    badge_f = tk.Frame(hdr, bg=st_color)
    badge_f.pack(side="right", padx=16, pady=8, ipadx=10, ipady=3)
    tk.Label(badge_f, text=f"● {status.upper()}",
             font=("Courier", 8, "bold"),
             fg="white", bg=st_color).pack()

    # ── Body ──────────────────────────────────────────────────────
    body = tk.Frame(win, bg=BG)
    body.pack(fill="both", expand=True, padx=16, pady=12)
    body.grid_columnconfigure(1, weight=1)
    body.grid_rowconfigure(0, weight=1)

    # ══════════════════════════════════════════════════
    # LEFT CARD — Photo
    # ══════════════════════════════════════════════════
    left = tk.Frame(body, bg=CARD,
                    highlightthickness=1, highlightbackground=BORDER,
                    width=220)
    left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
    left.grid_propagate(False)

    tk.Frame(left, bg=ACCENT2, height=3).pack(fill="x")

    # ── Photo area ────────────────────────────────────
    photo_area = tk.Frame(left, bg=CARD)
    photo_area.pack(pady=(20, 6), padx=10)

    _img_refs = [None, None]   # [photo, ring]
    PHOTO_SIZE = 160

    def _render_photo(path=None):
        for w in photo_area.winfo_children():
            w.destroy()

        p = path or _cur_photo[0]

        # Ring canvas (sits behind photo)
        ring_size = PHOTO_SIZE + 10
        ring_c = tk.Canvas(photo_area, width=ring_size, height=ring_size,
                           bg=CARD, highlightthickness=0)
        ring_c.pack()

        ring_img = _make_ring(PHOTO_SIZE, color=st_color, thickness=3)
        if ring_img:
            _img_refs[1] = ring_img
            ring_c.create_image(ring_size // 2, ring_size // 2,
                                image=ring_img, anchor="center")

        photo_img = (_make_circle_photo(p, PHOTO_SIZE)
                     or _make_avatar(full_name, PHOTO_SIZE))
        if photo_img:
            _img_refs[0] = photo_img
            ring_c.create_image(ring_size // 2, ring_size // 2,
                                image=photo_img, anchor="center")
        else:
            ring_c.create_oval(5, 5, ring_size - 5, ring_size - 5,
                               fill=PANEL, outline=BORDER, width=2)
            ring_c.create_text(ring_size // 2, ring_size // 2,
                               text="👤", font=("Segoe UI Emoji", 36),
                               fill=MUTED)

    _render_photo()

    # Name & ID
    tk.Label(left, text=full_name,
             font=("Georgia", 13, "bold"),
             fg=TEXT, bg=CARD,
             wraplength=190, justify="center").pack(pady=(8, 0), padx=8)
    tk.Label(left, text=f"#{rid:03d}  ·  {purok_name}",
             font=("Courier", 8),
             fg=MUTED, bg=CARD).pack(pady=(2, 0))

    # ── Gender / age chips ────────────────────────────────────────
    chips = tk.Frame(left, bg=CARD)
    chips.pack(pady=(8, 0))

    def _chip(parent, text, color):
        f = tk.Frame(parent, bg=color)
        f.pack(side="left", padx=3, ipadx=6, ipady=2)
        tk.Label(f, text=text, font=("Courier", 7, "bold"),
                 fg="white", bg=color).pack()

    try:
        ai = int(age)
        cat = ("Child" if ai < 18 else "Adult" if ai < 60 else "Senior")
        _chip(chips, f"{ai} yrs", ACCENT2)
        _chip(chips, cat, ACCENT if cat == "Adult" else
                          SUCCESS if cat == "Child" else ACCENT2)
    except Exception:
        pass
    if gender:
        _chip(chips, gender, "#3a5f8a")

    # ── Photo action buttons ──────────────────────────────────────
    tk.Frame(left, bg=BORDER, height=1).pack(fill="x", padx=14, pady=(14, 8))

    tk.Label(left, text="▸  PHOTO",
             font=("Courier", 7, "bold"),
             fg=ACCENT, bg=CARD).pack(anchor="w", padx=14)

    btn_area = tk.Frame(left, bg=CARD)
    btn_area.pack(fill="x", padx=14, pady=(6, 0))
    btn_area.grid_columnconfigure(0, weight=1)
    btn_area.grid_columnconfigure(1, weight=1)

    def _browse_and_update():
        """Browse for a photo and save it to resident_photos/."""
        fp = filedialog.askopenfilename(
            parent=win,
            title="Select Photo",
            filetypes=[
                ("Images", "*.jpg *.jpeg *.png *.bmp *.webp *.gif"),
                ("All files", "*.*"),
            ]
        )
        if not fp:
            return
        ext   = os.path.splitext(fp)[1].lower() or ".jpg"
        fname = f"resident_{rid:03d}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
        dest  = os.path.join(PHOTOS_DIR, fname)
        try:
            shutil.copy2(fp, dest)
        except Exception as e:
            messagebox.showerror("Error", f"Could not copy file:\n{e}")
            return
        _cur_photo[0] = dest
        _render_photo(dest)
        photo_note.config(text="✓ Photo updated", fg=SUCCESS)
        # Persist to DB
        try:
            import database
            database.update_photo(rid, dest)
        except Exception:
            pass
        if on_photo_updated:
            on_photo_updated(dest)

    def _open_cam():
        """Open camera window; on confirm updates the info photo too."""
        try:
            from camera_capture import open_camera_window
        except ImportError:
            messagebox.showerror("Missing", "camera_capture.py not found.")
            return

        def _on_taken(path):
            _cur_photo[0] = path
            _render_photo(path)
            photo_note.config(text="✓ Photo updated", fg=SUCCESS)
            try:
                import database
                database.update_photo(rid, path)
            except Exception:
                pass
            if on_photo_updated:
                on_photo_updated(path)

        open_camera_window(win, _on_taken)

    # Browse button
    browse_b = tk.Button(btn_area, text="📁  Browse",
                         command=_browse_and_update,
                         bg=PANEL, fg=ACCENT,
                         activebackground=BORDER, activeforeground=TEXT,
                         font=("Courier", 8, "bold"),
                         relief="flat", bd=0, cursor="hand2",
                         highlightthickness=1, highlightbackground=BORDER)
    browse_b.grid(row=0, column=0, sticky="ew", padx=(0, 3), ipady=6)

    # Camera button
    cam_b = tk.Button(btn_area, text="📷  Camera",
                      command=_open_cam,
                      bg=PANEL, fg=ACCENT2,
                      activebackground=BORDER, activeforeground=TEXT,
                      font=("Courier", 8, "bold"),
                      relief="flat", bd=0, cursor="hand2",
                      highlightthickness=1, highlightbackground=BORDER)
    cam_b.grid(row=0, column=1, sticky="ew", padx=(3, 0), ipady=6)

    # Hover effects
    for b, c in [(browse_b, ACCENT), (cam_b, ACCENT2)]:
        b.bind("<Enter>", lambda e, btn=b, col=c: btn.config(bg=col, fg="white"))
        b.bind("<Leave>", lambda e, btn=b: btn.config(bg=PANEL, fg=ACCENT
                          if btn is browse_b else ACCENT2))

    photo_note = tk.Label(left, text="", font=("Courier", 7),
                          fg=MUTED, bg=CARD)
    photo_note.pack(pady=(4, 0))

    # Spacer
    tk.Frame(left, bg=CARD).pack(fill="both", expand=True)

    # ══════════════════════════════════════════════════
    # RIGHT CARD — Details
    # ══════════════════════════════════════════════════
    right = tk.Frame(body, bg=CARD,
                     highlightthickness=1, highlightbackground=BORDER)
    right.grid(row=0, column=1, sticky="nsew")
    right.grid_columnconfigure(1, weight=1)

    tk.Frame(right, bg=ACCENT, height=3).pack(fill="x")

    scroll_c = tk.Canvas(right, bg=CARD, highlightthickness=0)
    scroll_c.pack(fill="both", expand=True, padx=0, pady=0)

    inner = tk.Frame(scroll_c, bg=CARD)
    scroll_c.create_window((0, 0), window=inner, anchor="nw")
    inner.bind("<Configure>",
               lambda e: scroll_c.configure(
                   scrollregion=scroll_c.bbox("all")))
    inner.grid_columnconfigure(1, weight=1)

    row_i = [0]

    def section(title):
        tk.Label(inner, text=f"▸  {title}",
                 font=("Courier", 8, "bold"),
                 fg=ACCENT, bg=CARD).grid(
                     row=row_i[0], column=0, columnspan=2,
                     sticky="w", padx=20, pady=(16, 4))
        row_i[0] += 1
        tk.Frame(inner, bg=BORDER, height=1).grid(
            row=row_i[0], column=0, columnspan=2,
            sticky="ew", padx=20, pady=(0, 8))
        row_i[0] += 1

    def detail(label, value, color=TEXT):
        tk.Label(inner, text=label,
                 font=("Courier", 8, "bold"),
                 fg=MUTED, bg=CARD,
                 width=13, anchor="w").grid(
                     row=row_i[0], column=0,
                     sticky="w", padx=(20, 4), pady=5)
        tk.Label(inner, text=str(value) if value else "—",
                 font=("Courier", 11, "bold"),
                 fg=color, bg=CARD, anchor="w").grid(
                     row=row_i[0], column=1,
                     sticky="w", padx=(0, 20), pady=5)
        row_i[0] += 1

    section("PERSONAL INFORMATION")
    detail("Full Name",  full_name,   TEXT)
    detail("Birthdate",  birthdate,   TEXT)
    detail("Gender",     gender,      TEXT)

    section("CONTACT & STATUS")
    detail("Contact",    contact,     SUCCESS)
    detail("Status",     status,      st_color)
    detail("Purok",      purok_name,  ACCENT)

    # ── Age indicator ─────────────────────────────────
    section("AGE INDICATOR")
    try:
        age_int = int(age)
        bar_color = (SUCCESS if age_int < 18 else
                     ACCENT   if age_int < 60 else ACCENT2)
        cat_txt   = ("Child (0–17)"   if age_int < 18 else
                     "Adult (18–59)"  if age_int < 60 else
                     "Senior (60+)")

        detail("Age", f"{age_int} yrs  ·  {cat_txt}", bar_color)

        # Progress bar
        bar_wrap = tk.Frame(inner, bg=PANEL,
                            highlightthickness=1, highlightbackground=BORDER,
                            height=14)
        bar_wrap.grid(row=row_i[0], column=0, columnspan=2,
                      sticky="ew", padx=20, pady=(0, 8))
        bar_wrap.grid_propagate(False)
        row_i[0] += 1

        pct = min(age_int / 100.0, 1.0)

        def _draw(e=None):
            bar_wrap.update_idletasks()
            w = int(bar_wrap.winfo_width() * pct)
            for c in bar_wrap.winfo_children():
                c.destroy()
            tk.Frame(bar_wrap, bg=bar_color,
                     width=w, height=14).place(x=0, y=0)

        bar_wrap.bind("<Configure>", _draw)
        win.after(120, _draw)
    except (ValueError, TypeError):
        pass

    # ── Footer ────────────────────────────────────────────────────
    footer = tk.Frame(win, bg=BG)
    footer.pack(fill="x", padx=16, pady=(0, 12))

    tk.Button(footer, text="✕  Close",
              command=win.destroy,
              bg=PANEL, fg=MUTED,
              activebackground=BORDER, activeforeground=TEXT,
              font=("Courier", 9, "bold"),
              relief="flat", bd=0, cursor="hand2").pack(
                  side="right", ipady=7, ipadx=16)

    if on_close:
        win.protocol("WM_DELETE_WINDOW",
                     lambda: (on_close(), win.destroy()))