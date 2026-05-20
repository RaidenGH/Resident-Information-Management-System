import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import database
import csv
import purok
import users_database
from logo import make_logo_canvas
from datetime import date, datetime
import calendar as cal
import os
import shutil

from resident_info import open_resident_info
from camera_capture import open_camera_window
import theme as _t

try:
    from PIL import Image, ImageTk
    PIL_OK = True
except ImportError:
    PIL_OK = False

PHOTOS_DIR = "resident_photos"


def _ensure_photos_dir():
    os.makedirs(PHOTOS_DIR, exist_ok=True)


def run_app(purok_id, purok_name, admin_username=None):
    """Entry point -- creates and runs the ResidentApp. Kept for backward compatibility."""
    app = ResidentApp(purok_id, purok_name, admin_username)
    app.run()


# ═══════════════════════════════════════════════════════════════════════════════
# ResidentApp -- class-based resident management application
# ═══════════════════════════════════════════════════════════════════════════════

class ResidentApp:
    """Full-screen resident registry for a single purok."""

    def __init__(self, purok_id, purok_name, admin_username=None):
        self.purok_id = purok_id
        self.purok_name = purok_name
        self.admin_username = admin_username

        # ── Theme ─────────────────────────────────────────────────
        self.BG = _t.BG; self.CARD = _t.CARD; self.PANEL = _t.PANEL
        self.BORDER = _t.BORDER; self.ACCENT = _t.ACCENT; self.ACCENT2 = _t.ACCENT2
        self.SUCCESS = _t.SUCCESS; self.DANGER = _t.DANGER; self.WARN = _t.WARN
        self.TEXT = _t.TEXT; self.MUTED = _t.MUTED
        self.PENDING = _t.PENDING; self.INACTIVE = _t.INACTIVE

        _ensure_photos_dir()

        # ── State ─────────────────────────────────────────────────
        self.current_photo = {"path": ""}
        self._thumb_img = [None]
        self.entries = {}
        self.stat_labels = {}
        self.tab_btns = {}
        self._sort_state = {"col": None, "rev": False}

        self.calendar_state = {
            "year": date.today().year,
            "month": date.today().month,
            "selected_date": date.today(),
            "temp_date": date.today(),
        }
        self.calendar_window_ref = [None]

        # ── Build UI ──────────────────────────────────────────────
        self._setup_root()
        self.active_tab = tk.StringVar(value="All")
        self._build_sidebar()
        self._build_main_panel()
        self._bind_events()

        self.refresh_table()
        self.update_stats()

    # ── Root window ────────────────────────────────────────────────
    def _setup_root(self):
        self.root = tk.Tk()
        self.root.title(f"Residents -- {self.purok_name}")
        self.root.configure(bg=self.BG)
        self.root.state("zoomed")
        self.root.resizable(True, True)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

    # ═══════════════════════════════════════════════════════════════
    # LEFT SIDEBAR
    # ═══════════════════════════════════════════════════════════════
    def _build_sidebar(self):
        s = tk.Frame(self.root, bg=self.CARD, width=275,
                     highlightthickness=1, highlightbackground=self.BORDER)
        s.grid(row=0, column=0, sticky="nsew")
        s.grid_propagate(False)
        s.grid_columnconfigure(0, weight=1)
        self.sidebar = s

        tk.Frame(s, bg=self.ACCENT, height=3).grid(row=0, column=0, sticky="ew")

        logo_c = make_logo_canvas(s, scale=0.52, bg=self.CARD)
        logo_c.grid(row=1, column=0, sticky="ew", padx=10, pady=(14, 0))

        tk.Label(s, text=f"\u25b8  {self.purok_name}",
                 font=_t.font("Courier", 8, "bold"),
                 fg=self.ACCENT, bg=self.CARD).grid(row=2, column=0, sticky="w", padx=18, pady=(2, 0))

        tk.Frame(s, bg=self.BORDER, height=1).grid(
            row=3, column=0, sticky="ew", padx=18, pady=(8, 0))

        self._make_sidebar_section(s, 4, "RESIDENT DETAILS")
        self._make_sidebar_entry(5, "First Name")
        self._make_sidebar_entry(6, "Last Name")
        self._build_calendar_picker(s, 7)
        self._build_gender_dropdown(s, 8)
        self._build_status_dropdown(s, 9)
        self._make_sidebar_entry(10, "Contact")

        self._build_photo_section(s, 11, 12)
        self._make_sidebar_section(s, 13, "ACTIONS")
        self._build_action_buttons(s)

        s.grid_rowconfigure(19, weight=1)
        tk.Label(s, text="\u00a9 BRGY System  v1.0",
                 font=_t.font("Courier", 7), fg=self.BORDER, bg=self.CARD).grid(
                     row=20, column=0, pady=(0, 8))
        self.sidebar = s

    def _make_sidebar_section(self, parent, row, text):
        f = tk.Frame(parent, bg=self.CARD)
        f.grid(row=row, column=0, sticky="ew", padx=18, pady=(12, 0))
        tk.Label(f, text="\u25b8 " + text, font=_t.font("Courier", 7, "bold"),
                 fg=self.ACCENT, bg=self.CARD).pack(side="left")
        tk.Frame(f, bg=self.BORDER, height=1).pack(
            side="left", fill="x", expand=True, padx=(6, 0), pady=5)

    def _make_sidebar_entry(self, grid_row, key, show=None):
        wrap = tk.Frame(self.sidebar, bg=self.CARD)
        wrap.grid(row=grid_row, column=0, sticky="ew", padx=18, pady=2)
        wrap.grid_columnconfigure(0, weight=1)
        tk.Label(wrap, text=key, font=_t.font("Courier", 8, "bold"),
                 fg=self.MUTED, bg=self.CARD).pack(anchor="w")
        inner = tk.Frame(wrap, bg=self.PANEL,
                         highlightthickness=1, highlightbackground=self.BORDER)
        inner.pack(fill="x", pady=(2, 0))
        e = tk.Entry(inner, show=show, bg=self.PANEL, fg=self.TEXT,
                     font=_t.font("Courier", 10), relief="flat",
                     insertbackground=self.ACCENT, bd=0)
        e.pack(fill="x", padx=8, pady=5)

        def _in(ev):
            inner.config(highlightbackground=self.ACCENT)
        def _out(ev):
            inner.config(highlightbackground=self.BORDER)
        e.bind("<FocusIn>", _in)
        e.bind("<FocusOut>", _out)
        self.entries[key] = e

    # ═══════════════════════════════════════════════════════════════
    # BIRTHDATE CALENDAR
    # ═══════════════════════════════════════════════════════════════
    def _build_calendar_picker(self, parent, row):
        bd_wrap = tk.Frame(parent, bg=self.CARD)
        bd_wrap.grid(row=row, column=0, sticky="ew", padx=18, pady=2)
        bd_wrap.grid_columnconfigure(0, weight=1)
        tk.Label(bd_wrap, text="Birthdate",
                 font=_t.font("Courier", 8, "bold"), fg=self.MUTED, bg=self.CARD).pack(anchor="w")

        bd_control = tk.Frame(bd_wrap, bg=self.CARD)
        bd_control.pack(fill="x", pady=(2, 0))
        bd_control.grid_columnconfigure(0, weight=1)

        self.bd_display = tk.Label(bd_control, text="Select date...",
                                   font=_t.font("Courier", 9), fg=self.TEXT, bg=self.PANEL,
                                   relief="solid", bd=1,
                                   highlightthickness=1, highlightbackground=self.BORDER)
        self.bd_display.grid(row=0, column=0, sticky="ew", ipady=4)

        cal_btn = tk.Button(bd_control, text="\U0001f4c5", command=self._open_calendar,
                            bg=self.ACCENT, fg="white", font=_t.font("Courier", 9, "bold"),
                            relief="flat", bd=0, cursor="hand2", padx=6, pady=2)
        cal_btn.grid(row=0, column=1, sticky="ew", padx=(4, 0))
        bd_control.grid_columnconfigure(1, weight=0)

        self.bd_display.config(text=self.calendar_state["selected_date"].strftime("%Y-%m-%d"))
        self.entries["Birthdate"] = self.calendar_state["selected_date"].strftime("%Y-%m-%d")

        self.age_lbl = tk.Label(bd_wrap, text="Age: \u2014",
                                font=_t.font("Courier", 8, "bold"), fg=self.MUTED, bg=self.CARD)
        self.age_lbl.pack(anchor="w", pady=(3, 0))
        self._calc_age()

    def _open_calendar(self):
        if (self.calendar_window_ref[0] is not None
                and self.calendar_window_ref[0].winfo_exists()):
            self.calendar_window_ref[0].destroy()

        cal_win = tk.Toplevel(self.root)
        cal_win.title("Select Date")
        cal_win.geometry("380x260")
        cal_win.resizable(False, False)
        cal_win.configure(bg=self.CARD)
        cal_win.grab_set()
        cal_win.transient(self.root)
        self.calendar_window_ref[0] = cal_win

        header = tk.Frame(cal_win, bg=self.CARD)
        header.pack(fill="x", padx=8, pady=8)

        def prev_month():
            if self.calendar_state["month"] == 1:
                self.calendar_state["month"] = 12
                self.calendar_state["year"] -= 1
            else:
                self.calendar_state["month"] -= 1
            refresh_calendar()

        def next_month():
            if self.calendar_state["month"] == 12:
                self.calendar_state["month"] = 1
                self.calendar_state["year"] += 1
            else:
                self.calendar_state["month"] += 1
            refresh_calendar()

        tk.Button(header, text="\u25c0", command=prev_month,
                  bg=self.PANEL, fg=self.ACCENT, font=_t.font("Courier", 10, "bold"),
                  relief="flat", bd=0, cursor="hand2", width=2).pack(side="left", padx=2)

        def open_year_picker():
            ywin = tk.Toplevel(cal_win)
            ywin.title("Year"); ywin.geometry("130x300")
            ywin.configure(bg=self.CARD); ywin.resizable(False, False); ywin.grab_set()
            tk.Label(ywin, text="Year", font=_t.font("Courier", 10, "bold"),
                     fg=self.TEXT, bg=self.CARD).pack(pady=5)
            fr = tk.Frame(ywin, bg=self.CARD)
            fr.pack(fill="both", expand=True, padx=8, pady=8)
            cv = tk.Canvas(fr, bg=self.PANEL, highlightthickness=1,
                           highlightbackground=self.BORDER)
            sb = tk.Scrollbar(fr, orient="vertical", command=cv.yview,
                              bg=self.BORDER, troughcolor=self.CARD, width=4,
                              relief="flat", highlightthickness=0)
            sf = tk.Frame(cv, bg=self.PANEL)
            sf.bind("<Configure>", lambda e: cv.configure(scrollregion=cv.bbox("all")))
            cv.create_window((0, 0), window=sf, anchor="nw")
            cv.configure(yscrollcommand=sb.set)
            cv.bind_all("<MouseWheel>",
                        lambda e: cv.yview_scroll(int(-1*(e.delta/120)), "units"))
            sy, ey = date.today().year - 80, date.today().year + 10
            for y in range(sy, ey + 1):
                bc = self.ACCENT if y == self.calendar_state["year"] else self.PANEL
                fc = "white" if y == self.calendar_state["year"] else self.TEXT

                def _sel(yr=y):
                    self.calendar_state["year"] = yr
                    ywin.destroy()
                    refresh_calendar()
                tk.Button(sf, text=str(y), command=_sel,
                          bg=bc, fg=fc, font=_t.font("Courier", 8),
                          relief="flat", bd=0, cursor="hand2", width=12).pack(pady=1)
            cv.pack(side="left", fill="both", expand=True)
            sb.pack(side="right", fill="y")
            self.root.after(100, lambda: cv.yview_moveto(
                (self.calendar_state["year"]-sy)/(ey-sy)))

        year_btn = tk.Button(header, text=str(self.calendar_state["year"]),
                             command=open_year_picker,
                             bg=self.PANEL, fg=self.ACCENT, font=_t.font("Courier", 9, "bold"),
                             relief="flat", bd=0, cursor="hand2", width=5)
        year_btn.pack(side="left", padx=3)

        def open_month_picker():
            mwin = tk.Toplevel(cal_win)
            mwin.title("Month"); mwin.geometry("155x320")
            mwin.configure(bg=self.CARD); mwin.resizable(False, False); mwin.grab_set()
            tk.Label(mwin, text="Month", font=_t.font("Courier", 10, "bold"),
                     fg=self.TEXT, bg=self.CARD).pack(pady=5)
            for i, mn in enumerate(["January", "February", "March", "April", "May", "June",
                                     "July", "August", "September", "October", "November", "December"]):
                bc = self.ACCENT if i+1 == self.calendar_state["month"] else self.PANEL
                fc = "white" if i+1 == self.calendar_state["month"] else self.TEXT

                def _sel(m=i+1):
                    self.calendar_state["month"] = m
                    mwin.destroy()
                    refresh_calendar()
                tk.Button(mwin, text=mn, command=_sel,
                          bg=bc, fg=fc, font=_t.font("Courier", 8),
                          relief="flat", bd=0, cursor="hand2", width=16).pack(pady=2)

        month_btn = tk.Button(header, text=cal.month_name[self.calendar_state["month"]],
                              command=open_month_picker,
                              bg=self.PANEL, fg=self.ACCENT, font=_t.font("Courier", 9, "bold"),
                              relief="flat", bd=0, cursor="hand2", width=10)
        month_btn.pack(side="left", padx=3, fill="x", expand=True)

        tk.Button(header, text="\u25b6", command=next_month,
                  bg=self.PANEL, fg=self.ACCENT, font=_t.font("Courier", 10, "bold"),
                  relief="flat", bd=0, cursor="hand2", width=2).pack(side="left", padx=2)

        def go_today():
            t = date.today()
            self.calendar_state.update(year=t.year, month=t.month, temp_date=t)
            refresh_calendar()

        tk.Button(header, text="Today", command=go_today,
                  bg=self.SUCCESS, fg="white", font=_t.font("Courier", 7, "bold"),
                  relief="flat", bd=0, cursor="hand2", padx=3, pady=1).pack(side="right", padx=2)

        cal_frame = tk.Frame(cal_win, bg=self.CARD)
        cal_frame.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        for i in range(7):
            cal_frame.grid_columnconfigure(i, weight=1)

        for i, d in enumerate(["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]):
            tk.Label(cal_frame, text=d, font=_t.font("Courier", 8, "bold"),
                     fg=self.ACCENT if i < 5 else self.DANGER,
                     bg=self.CARD).grid(row=0, column=i, sticky="nsew", padx=1, pady=2)

        cal_buttons = []

        def refresh_calendar():
            for b in cal_buttons:
                b.destroy()
            cal_buttons.clear()
            year_btn.config(text=str(self.calendar_state["year"]))
            month_btn.config(text=cal.month_name[self.calendar_state["month"]])
            month_cal = cal.monthcalendar(self.calendar_state["year"],
                                           self.calendar_state["month"])
            today = date.today()
            for wr, week in enumerate(month_cal):
                for dc, day in enumerate(week):
                    if day == 0:
                        lbl = tk.Label(cal_frame, text="", bg=self.CARD)
                        lbl.grid(row=wr+1, column=dc, sticky="nsew", padx=1, pady=1)
                        cal_buttons.append(lbl)
                    else:
                        cd = date(self.calendar_state["year"],
                                  self.calendar_state["month"], day)
                        if cd == today:
                            bc, fc = self.ACCENT2, "white"
                        elif cd == self.calendar_state["temp_date"]:
                            bc, fc = self.ACCENT, "white"
                        else:
                            bc, fc = self.PANEL, self.TEXT

                        def _sel(d2=day, cd2=cd):
                            self.calendar_state["temp_date"] = cd2
                            refresh_calendar()
                        b = tk.Button(cal_frame, text=str(day), command=_sel,
                                      bg=bc, fg=fc, font=_t.font("Courier", 8, "bold"),
                                      relief="flat", bd=0, cursor="hand2",
                                      width=3, height=1)
                        b.grid(row=wr+1, column=dc, sticky="nsew", padx=1, pady=1)
                        cal_buttons.append(b)

        footer_c = tk.Frame(cal_win, bg=self.CARD)
        footer_c.pack(fill="x", padx=8, pady=(0, 8))
        footer_c.grid_columnconfigure([0, 1], weight=1)

        def confirm():
            self.calendar_state["selected_date"] = self.calendar_state["temp_date"]
            self.bd_display.config(text=self.calendar_state["selected_date"].strftime("%Y-%m-%d"))
            self.entries["Birthdate"] = self.calendar_state["selected_date"].strftime("%Y-%m-%d")
            self._calc_age()
            cal_win.destroy()

        def cancel():
            self.calendar_state["temp_date"] = self.calendar_state["selected_date"]
            cal_win.destroy()

        tk.Button(footer_c, text="\u2713 Confirm", command=confirm,
                  bg=self.SUCCESS, fg="white", font=_t.font("Courier", 8, "bold"),
                  relief="flat", bd=0, cursor="hand2",
                  padx=8, pady=3).grid(row=0, column=0, sticky="ew", padx=2)
        tk.Button(footer_c, text="\u2715 Cancel", command=cancel,
                  bg=self.DANGER, fg="white", font=_t.font("Courier", 8, "bold"),
                  relief="flat", bd=0, cursor="hand2",
                  padx=8, pady=3).grid(row=0, column=1, sticky="ew", padx=2)

        refresh_calendar()

    # ═══════════════════════════════════════════════════════════════
    # GENDER & STATUS DROPDOWNS
    # ═══════════════════════════════════════════════════════════════
    def _build_gender_dropdown(self, parent, row):
        wrap = tk.Frame(parent, bg=self.CARD)
        wrap.grid(row=row, column=0, sticky="ew", padx=18, pady=2)
        tk.Label(wrap, text="Gender", font=_t.font("Courier", 8, "bold"),
                 fg=self.MUTED, bg=self.CARD).pack(anchor="w")
        self.gender_var = tk.StringVar(value="Select Gender")
        inner = tk.Frame(wrap, bg=self.PANEL,
                         highlightthickness=1, highlightbackground=self.BORDER)
        inner.pack(fill="x", pady=(2, 0))
        dd = tk.OptionMenu(inner, self.gender_var, "Male", "Female", "Other")
        dd.config(bg=self.PANEL, fg=self.TEXT, font=_t.font("Courier", 9), relief="flat",
                  bd=0, activebackground=self.ACCENT, activeforeground="white",
                  highlightthickness=0, anchor="w")
        dd["menu"].config(bg=self.PANEL, fg=self.TEXT, font=_t.font("Courier", 9),
                          relief="flat", activebackground=self.ACCENT,
                          activeforeground="white")
        dd.pack(fill="x", padx=4, pady=2)

    def _build_status_dropdown(self, parent, row):
        wrap = tk.Frame(parent, bg=self.CARD)
        wrap.grid(row=row, column=0, sticky="ew", padx=18, pady=2)
        tk.Label(wrap, text="Status", font=_t.font("Courier", 8, "bold"),
                 fg=self.MUTED, bg=self.CARD).pack(anchor="w")
        self.status_var = tk.StringVar(value="Registered")
        inner = tk.Frame(wrap, bg=self.PANEL,
                         highlightthickness=1, highlightbackground=self.BORDER)
        inner.pack(fill="x", pady=(2, 0))
        dd = tk.OptionMenu(inner, self.status_var,
                           "Registered", "Pending", "Inactive")
        dd.config(bg=self.PANEL, fg=self.TEXT, font=_t.font("Courier", 9), relief="flat",
                  bd=0, activebackground=self.ACCENT, activeforeground="white",
                  highlightthickness=0, anchor="w")
        dd["menu"].config(bg=self.PANEL, fg=self.TEXT, font=_t.font("Courier", 9),
                          relief="flat", activebackground=self.ACCENT,
                          activeforeground="white")
        dd.pack(fill="x", padx=4, pady=2)

    # ═══════════════════════════════════════════════════════════════
    # PHOTO SECTION
    # ═══════════════════════════════════════════════════════════════
    def _build_photo_section(self, parent, section_row, content_row):
        self._make_sidebar_section(parent, section_row, "PHOTO")

        photo_outer = tk.Frame(parent, bg=self.CARD)
        photo_outer.grid(row=content_row, column=0, sticky="ew", padx=18, pady=(4, 2))
        photo_outer.grid_columnconfigure(1, weight=1)

        # Thumbnail
        self.thumb_border = tk.Frame(photo_outer, bg=self.ACCENT2,
                                     highlightthickness=1, highlightbackground=self.BORDER)
        self.thumb_border.grid(row=0, column=0, rowspan=2, sticky="nw", padx=(0, 10))

        thumb_inner = tk.Frame(self.thumb_border, bg=self.PANEL, width=58, height=58)
        thumb_inner.pack(padx=2, pady=2)
        thumb_inner.pack_propagate(False)

        self.thumb_lbl = tk.Label(thumb_inner, text="\U0001f464",
                                  font=_t.font("Segoe UI Emoji", 20),
                                  bg=self.PANEL, fg=self.MUTED)
        self.thumb_lbl.place(relx=0.5, rely=0.5, anchor="center")

        # Buttons column
        btn_col = tk.Frame(photo_outer, bg=self.CARD)
        btn_col.grid(row=0, column=1, sticky="ew")
        btn_col.grid_columnconfigure(0, weight=1)
        btn_col.grid_columnconfigure(1, weight=1)

        browse_btn = tk.Button(btn_col, text="\U0001f4c1  Browse",
                               command=self._browse_photo,
                               bg=self.PANEL, fg=self.ACCENT,
                               activebackground=self.ACCENT,
                               activeforeground="white",
                               font=_t.font("Courier", 8, "bold"),
                               relief="flat", bd=0, cursor="hand2",
                               highlightthickness=1, highlightbackground=self.BORDER)
        browse_btn.grid(row=0, column=0, sticky="ew", padx=(0, 3), ipady=6)

        cam_btn = tk.Button(btn_col, text="\U0001f4f7  Camera",
                            command=lambda: open_camera_window(
                                self.root, self._on_photo_taken,
                                bg=self.CARD, accent=self.ACCENT, panel=self.PANEL,
                                border=self.BORDER, text=self.TEXT, muted=self.MUTED,
                                success=self.SUCCESS, danger=self.DANGER),
                            bg=self.PANEL, fg=self.ACCENT2,
                            activebackground=self.ACCENT2,
                            activeforeground="white",
                            font=_t.font("Courier", 8, "bold"),
                            relief="flat", bd=0, cursor="hand2",
                            highlightthickness=1, highlightbackground=self.BORDER)
        cam_btn.grid(row=0, column=1, sticky="ew", padx=(3, 0), ipady=6)

        # Hover effects
        browse_btn.bind("<Enter>", lambda e: browse_btn.config(bg=self.ACCENT, fg="white"))
        browse_btn.bind("<Leave>", lambda e: browse_btn.config(bg=self.PANEL, fg=self.ACCENT))
        cam_btn.bind("<Enter>", lambda e: cam_btn.config(bg=self.ACCENT2, fg="white"))
        cam_btn.bind("<Leave>", lambda e: cam_btn.config(bg=self.PANEL, fg=self.ACCENT2))

        self.photo_status_lbl = tk.Label(photo_outer,
                                          text="No photo  \u00b7  browse or use camera",
                                          font=_t.font("Courier", 7), fg=self.MUTED, bg=self.CARD)
        self.photo_status_lbl.grid(row=1, column=1, sticky="w", pady=(4, 0))

    def _update_thumb(self, path):
        if PIL_OK and path and os.path.exists(path):
            try:
                img = Image.open(path).resize((54, 54))
                imgtk = ImageTk.PhotoImage(img)
                self._thumb_img[0] = imgtk
                self.thumb_lbl.config(image=imgtk, text="")
                self.photo_status_lbl.config(text="\u2713 Photo ready", fg=self.SUCCESS)
                self.thumb_border.config(bg=self.SUCCESS)
            except Exception:
                pass

    def _on_photo_taken(self, path):
        self.current_photo["path"] = path
        self._update_thumb(path)

    def _browse_photo(self):
        fp = filedialog.askopenfilename(
            parent=self.root,
            title="Select Resident Photo",
            filetypes=[
                ("Images", "*.jpg *.jpeg *.png *.bmp *.webp *.gif"),
                ("JPEG", "*.jpg *.jpeg"),
                ("PNG", "*.png"),
                ("All files", "*.*"),
            ]
        )
        if not fp:
            return
        ext = os.path.splitext(fp)[1].lower() or ".jpg"
        fname = f"resident_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
        dest = os.path.join(PHOTOS_DIR, fname)
        try:
            shutil.copy2(fp, dest)
            self._on_photo_taken(dest)
        except Exception as e:
            messagebox.showerror("Error", f"Could not copy file:\n{e}")

    # ═══════════════════════════════════════════════════════════════
    # USER ACTIONS
    # ═══════════════════════════════════════════════════════════════
    def _build_action_buttons(self, parent):
        def make_btn(row, label, color, active_color, cmd, fg_color="white"):
            btn = tk.Button(parent, text=label, command=cmd,
                            bg=color, fg=fg_color,
                            activebackground=active_color,
                            activeforeground=fg_color,
                            font=_t.font("Courier", 9, "bold"),
                            relief="flat", bd=0, cursor="hand2")
            btn.grid(row=row, column=0, sticky="ew", padx=18, pady=2, ipady=7)
            return btn

        make_btn(14, "\uff0b  Add Resident",    self.ACCENT,  "#3a7ce8", self.add_resident)
        make_btn(15, "\u270e  Update Selected", self.WARN,    "#d9903a", self.update_resident, "#0d0f14")
        make_btn(16, "\u2715  Delete Selected", self.DANGER,  "#d93a52", self.delete_resident)

        tk.Frame(parent, bg=self.BORDER, height=1).grid(
            row=17, column=0, sticky="ew", padx=18, pady=(10, 0))
        make_btn(18, "\u2190 Back to Puroks", self.PANEL, self.BORDER, self.go_back, self.MUTED)

    # ═══════════════════════════════════════════════════════════════
    # RIGHT MAIN PANEL
    # ═══════════════════════════════════════════════════════════════
    def _build_main_panel(self):
        main = tk.Frame(self.root, bg=self.BG)
        main.grid(row=0, column=1, sticky="nsew")
        main.grid_rowconfigure(4, weight=1)
        main.grid_columnconfigure(0, weight=1)
        self.main = main

        tk.Frame(main, bg=self.ACCENT2, height=3).grid(row=0, column=0, sticky="ew")

        self._build_topbar(main)
        self._build_stats_bar(main)
        self._build_tab_bar(main)
        self._build_batch_bar(main)
        self._build_treeview(main)

    def _build_topbar(self, parent):
        topbar = tk.Frame(parent, bg=self.BG)
        topbar.grid(row=1, column=0, sticky="ew", padx=20, pady=(14, 8))
        topbar.grid_columnconfigure(1, weight=1)

        tf = tk.Frame(topbar, bg=self.BG)
        tf.grid(row=0, column=0, sticky="w")
        tk.Label(tf, text="Resident", font=_t.font("Georgia", 20, "bold"),
                 fg=self.TEXT, bg=self.BG).pack(side="left")
        tk.Label(tf, text=" Registry", font=_t.font("Georgia", 20, "italic"),
                 fg=self.ACCENT, bg=self.BG).pack(side="left")

        # Search
        search_wrap = tk.Frame(topbar, bg=self.PANEL,
                               highlightthickness=1, highlightbackground=self.BORDER)
        search_wrap.grid(row=0, column=1, sticky="ew", padx=(20, 12))
        tk.Label(search_wrap, text="\u2315", font=_t.font("Courier", 11),
                 fg=self.MUTED, bg=self.PANEL).pack(side="left", padx=(8, 2))
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_wrap, textvariable=self.search_var,
                                bg=self.PANEL, fg=self.TEXT, font=_t.font("Courier", 10),
                                relief="flat", insertbackground=self.ACCENT, bd=0)
        search_entry.pack(side="left", fill="x", expand=True, pady=6, padx=(0, 8))
        search_entry.insert(0, "Search residents...")

        def _sf_in(e):
            if search_entry.get() == "Search residents...":
                search_entry.delete(0, tk.END)
            search_wrap.config(highlightbackground=self.ACCENT)

        def _sf_out(e):
            if not search_entry.get():
                search_entry.insert(0, "Search residents...")
            search_wrap.config(highlightbackground=self.BORDER)
        search_entry.bind("<FocusIn>", _sf_in)
        search_entry.bind("<FocusOut>", _sf_out)
        self.search_var.trace_add("write", self._on_search)

        # Toolbar buttons
        right_tools = tk.Frame(topbar, bg=self.BG)
        right_tools.grid(row=0, column=2, sticky="e")

        def make_tool_btn(text, color, cmd):
            b = tk.Button(right_tools, text=text, command=cmd,
                          bg=self.PANEL, fg=color,
                          activebackground=self.BORDER, activeforeground=color,
                          font=_t.font("Courier", 8, "bold"),
                          relief="flat", bd=0, cursor="hand2",
                          highlightthickness=1, highlightbackground=self.BORDER)
            b.pack(side="left", padx=3, ipady=5, ipadx=10)
            return b

        make_tool_btn("\u2b06  Export", self.SUCCESS, self._export_csv)
        make_tool_btn("\u2b07  Import", self.ACCENT, self._import_csv)
        make_tool_btn("\U0001f5a8  Print", self.WARN, self._print_list)

        # Admin Panel button
        if self.admin_username and users_database.can_access_admin_panel(self.admin_username):
            self._build_admin_button(right_tools)

        # Logout
        self._build_logout_button(right_tools)

    def _build_logout_button(self, parent):
        lo_outer = tk.Frame(parent, bg="#3d0b14",
                            highlightthickness=1, highlightbackground="#7a1a2e")
        lo_outer.pack(side="left", padx=(10, 0))
        lo_btn = tk.Button(lo_outer, text="\u23fb  LOG OUT", command=self.logout,
                           bg="#1e0a10", fg=self.DANGER,
                           activebackground="#3d0b14", activeforeground="#ff8099",
                           font=_t.font("Courier", 8, "bold"),
                           relief="flat", bd=0, cursor="hand2", padx=12, pady=5)
        lo_btn.pack()

        def _lo_in(e):
            lo_outer.config(highlightbackground=self.DANGER)
            lo_btn.config(bg="#2d0f1a", fg="#ff6b85")

        def _lo_out(e):
            lo_outer.config(highlightbackground="#7a1a2e")
            lo_btn.config(bg="#1e0a10", fg=self.DANGER)
        lo_btn.bind("<Enter>", _lo_in)
        lo_btn.bind("<Leave>", _lo_out)
        lo_outer.bind("<Enter>", _lo_in)
        lo_outer.bind("<Leave>", _lo_out)

    def _build_admin_button(self, parent):
        def _open():
            pw_win = tk.Toplevel(self.root)
            pw_win.title("Confirm Access")
            pw_win.configure(bg=self.CARD)
            pw_win.geometry("320x180")
            pw_win.resizable(False, False)
            pw_win.grab_set()
            pw_win.transient(self.root)
            sw, sh = pw_win.winfo_screenwidth(), pw_win.winfo_screenheight()
            pw_win.geometry(f"320x180+{(sw-320)//2}+{(sh-180)//2}")

            tk.Label(pw_win, text="Enter your password to continue:",
                     font=_t.font("Courier", 9, "bold"),
                     fg=self.TEXT, bg=self.CARD).pack(pady=(16, 8))

            pw_entry_wrap = tk.Frame(pw_win, bg=self.PANEL,
                                      highlightthickness=1,
                                      highlightbackground=self.BORDER)
            pw_entry_wrap.pack(padx=20, fill="x")
            pw_entry = tk.Entry(pw_entry_wrap, bg=self.PANEL, fg=self.TEXT,
                                font=_t.font("Courier", 11), show="\u25cf",
                                relief="flat", insertbackground=self.ACCENT, bd=0)
            pw_entry.pack(fill="x", padx=8, pady=6)
            pw_entry.focus_set()

            def _confirm_pw():
                p = pw_entry.get().strip()
                if not users_database.validate_login(self.admin_username, p):
                    messagebox.showerror("Access Denied", "Incorrect password.")
                    return
                pw_win.destroy()
                import admin_panel
                admin_panel.run_admin_panel(self.admin_username, lambda: None)

            pw_entry.bind("<Return>", lambda e: _confirm_pw())
            btn_row = tk.Frame(pw_win, bg=self.CARD)
            btn_row.pack(fill="x", padx=20, pady=(12, 0))
            tk.Button(btn_row, text="\u2713  Confirm", command=_confirm_pw,
                      bg=self.ACCENT, fg="white",
                      font=_t.font("Courier", 9, "bold"),
                      relief="flat", bd=0, cursor="hand2",
                      padx=14, pady=5).pack(side="left", padx=(0, 6))
            tk.Button(btn_row, text="\u2715  Cancel", command=pw_win.destroy,
                      bg=self.DANGER, fg="white",
                      font=_t.font("Courier", 9, "bold"),
                      relief="flat", bd=0, cursor="hand2",
                      padx=14, pady=5).pack(side="left")

        admin_outer = tk.Frame(parent, bg="#1a1030",
                               highlightthickness=1,
                               highlightbackground=self.ACCENT2)
        admin_outer.pack(side="left", padx=(10, 0))
        admin_btn = tk.Button(admin_outer, text="\u2699  ADMIN",
                              command=_open,
                              bg="#140b24", fg=self.ACCENT2,
                              activebackground="#2a1a4a",
                              activeforeground="#b090ff",
                              font=_t.font("Courier", 8, "bold"),
                              relief="flat", bd=0, cursor="hand2",
                              padx=10, pady=5)
        admin_btn.pack()

        def _ad_in(e):
            admin_outer.config(highlightbackground="#b090ff")
            admin_btn.config(fg="#c8aaff")

        def _ad_out(e):
            admin_outer.config(highlightbackground=self.ACCENT2)
            admin_btn.config(fg=self.ACCENT2)
        admin_btn.bind("<Enter>", _ad_in)
        admin_btn.bind("<Leave>", _ad_out)

    # ═══════════════════════════════════════════════════════════════
    # STATS BAR
    # ═══════════════════════════════════════════════════════════════
    def _build_stats_bar(self, parent):
        stats_frame = tk.Frame(parent, bg=self.CARD,
                               highlightthickness=1,
                               highlightbackground=self.BORDER)
        stats_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 8))

        def make_stat(key, title, color):
            f = tk.Frame(stats_frame, bg=self.PANEL,
                         highlightthickness=1, highlightbackground=self.BORDER)
            f.pack(side="left", padx=8, pady=8, ipadx=10, ipady=4)
            tk.Label(f, text=title, font=_t.font("Courier", 7, "bold"),
                     fg=self.MUTED, bg=self.PANEL).pack(anchor="w", padx=8, pady=(5, 0))
            lbl = tk.Label(f, text="0", font=_t.font("Courier", 20, "bold"),
                           fg=color, bg=self.PANEL)
            lbl.pack(anchor="w", padx=8, pady=(0, 5))
            self.stat_labels[key] = lbl

        make_stat("total",      "TOTAL RESIDENTS", self.ACCENT)
        make_stat("registered", "REGISTERED",      self.SUCCESS)
        make_stat("pending",    "PENDING",         self.WARN)
        make_stat("inactive",   "INACTIVE",        self.DANGER)
        make_stat("seniors",    "SENIORS  60+",    self.ACCENT2)
        make_stat("male",       "MALE",            "#5b9bff")
        make_stat("female",     "FEMALE",          "#fc5cbc")

        time_lbl = tk.Label(stats_frame, text="",
                            font=_t.font("Courier", 8), fg=self.MUTED, bg=self.CARD)
        time_lbl.pack(side="right", padx=16, pady=8)

        def _tick():
            time_lbl.config(
                text="Last updated: " + datetime.now().strftime("Today, %I:%M %p"))
            self.root.after(60000, _tick)
        _tick()

        self.sort_info = tk.Label(stats_frame, text="Sorted by: Last Name \u2191",
                                  font=_t.font("Courier", 8), fg=self.ACCENT, bg=self.CARD)
        self.sort_info.pack(side="right", padx=4, pady=8)

    # ═══════════════════════════════════════════════════════════════
    # TAB BAR + STATUS
    # ═══════════════════════════════════════════════════════════════
    def _build_tab_bar(self, parent):
        tab_bar = tk.Frame(parent, bg=self.BG)
        tab_bar.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 4))

        for tab_name, tab_key in [("All Residents", "All"), ("Registered", "Registered"),
                                   ("Pending", "Pending"), ("Inactive", "Inactive")]:
            b = tk.Button(tab_bar, text=tab_name,
                          font=_t.font("Courier", 9, "bold"),
                          bg=self.PANEL, fg=self.MUTED,
                          activebackground=self.ACCENT, activeforeground="white",
                          relief="flat", bd=0, cursor="hand2",
                          highlightthickness=1, highlightbackground=self.BORDER,
                          command=lambda k=tab_key: self._switch_tab(k))
            b.pack(side="left", padx=(0, 6), ipady=6, ipadx=14)
            self.tab_btns[tab_key] = b
        self.tab_btns["All"].config(bg=self.ACCENT, fg="white",
                                    highlightbackground=self.ACCENT)

        self.status_lbl = tk.Label(tab_bar, text="", font=_t.font("Courier", 8),
                                   fg=self.SUCCESS, bg=self.BG)
        self.status_lbl.pack(side="right", padx=4)

    def _switch_tab(self, name):
        self.active_tab.set(name)
        for n, b in self.tab_btns.items():
            if n == name:
                b.config(bg=self.ACCENT, fg="white", highlightbackground=self.ACCENT)
            else:
                b.config(bg=self.PANEL, fg=self.MUTED, highlightbackground=self.BORDER)
        self.refresh_table()

    def status_msg(self, msg, color=None):
        if color is None:
            color = self.SUCCESS
        self.status_lbl.config(text=msg, fg=color)
        self.root.after(4000, lambda: self.status_lbl.config(text=""))

    # ═══════════════════════════════════════════════════════════════
    # BATCH ACTION BAR
    # ═══════════════════════════════════════════════════════════════
    def _build_batch_bar(self, parent):
        self.batch_bar = tk.Frame(parent, bg=self.CARD,
                                  highlightthickness=1,
                                  highlightbackground=self.BORDER)
        self.batch_bar.grid(row=5, column=0, sticky="ew", padx=20, pady=(0, 8))
        self.batch_bar.grid_remove()

        tk.Label(self.batch_bar, text="\u26a1  BATCH ACTIONS",
                 font=_t.font("Courier", 8, "bold"),
                 fg=self.ACCENT2, bg=self.CARD).pack(side="left", padx=14)

        self.sel_count_lbl = tk.Label(self.batch_bar, text="0 selected",
                                      font=_t.font("Courier", 9, "bold"),
                                      fg=self.TEXT, bg=self.CARD)
        self.sel_count_lbl.pack(side="left", padx=6)

        for lbl, color, cmd in [
            ("\u2715  Delete Selected", self.DANGER, self.batch_delete),
            ("\u2b06  Export Selected", self.SUCCESS, self.batch_export),
        ]:
            b = tk.Button(self.batch_bar, text=lbl, command=cmd,
                          bg=color, fg="white",
                          activebackground=color, activeforeground="white",
                          font=_t.font("Courier", 8, "bold"),
                          relief="flat", bd=0, cursor="hand2",
                          padx=12, pady=4)
            b.pack(side="left", padx=(6, 0))
            b.bind("<Enter>", lambda e, c=color: e.widget.config(bg=c, fg="white"))
            b.bind("<Leave>", lambda e, c=color: e.widget.config(bg=c, fg="white"))

    def _on_selection_change(self, event=None):
        sel = self.tree.selection()
        count = len(sel)
        if count > 0:
            self.sel_count_lbl.config(text=f"{count} selected")
            self.batch_bar.grid()
        else:
            self.batch_bar.grid_remove()

    # ═══════════════════════════════════════════════════════════════
    # TREEVIEW
    # ═══════════════════════════════════════════════════════════════
    def _build_treeview(self, parent):
        tree_frame = tk.Frame(parent, bg=self.CARD,
                              highlightthickness=1,
                              highlightbackground=self.BORDER)
        tree_frame.grid(row=4, column=0, sticky="nsew", padx=20, pady=(0, 14))
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(5, weight=0)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Res.Treeview",
                        background=self.PANEL, foreground=self.TEXT,
                        fieldbackground=self.PANEL, borderwidth=0,
                        font=_t.font("Courier", 10), rowheight=36)
        style.configure("Res.Treeview.Heading",
                        background=self.CARD, foreground=self.ACCENT,
                        font=_t.font("Courier", 9, "bold"),
                        borderwidth=0, relief="flat")
        # Compute theme-aware alternating row & selection colors
        cur_theme = _t.get_current_theme()
        if cur_theme == "light":
            even_bg = "#e0e3ec"
            sel_bg  = "#d6def5"
        elif cur_theme == "forest":
            even_bg = "#1a2c1a"
            sel_bg  = "#2a4a2a"
        else:
            even_bg = "#13172a"
            sel_bg  = "#1e2a42"

        style.map("Res.Treeview",
                  background=[("selected", sel_bg)],
                  foreground=[("selected", self.TEXT)])
        style.map("Res.Treeview.Heading",
                  background=[("active", self.PANEL)])

        vsb = tk.Scrollbar(tree_frame, orient="vertical",
                           bg=self.BORDER, troughcolor=self.CARD,
                           width=6, relief="flat", highlightthickness=0)
        vsb.grid(row=0, column=1, sticky="ns")

        cols = ("ID", "First Name", "Last Name", "Age",
                "Birthdate", "Gender", "Contact", "Status")
        self.tree = ttk.Treeview(tree_frame, columns=cols, show="headings",
                                 style="Res.Treeview", yscrollcommand=vsb.set,
                                 selectmode="extended")

        col_cfg = {
            "ID":         (60,  "center"),
            "First Name": (160, "w"),
            "Last Name":  (160, "w"),
            "Age":        (80,  "center"),
            "Birthdate":  (120, "center"),
            "Gender":     (90,  "center"),
            "Contact":    (150, "center"),
            "Status":     (110, "center"),
        }
        for col in cols:
            w, anch = col_cfg[col]
            self.tree.heading(col, text=col, anchor="center",
                              command=lambda c=col: self._sort_by(c))
            self.tree.column(col, width=w, minwidth=w, anchor=anch, stretch=True)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.config(command=self.tree.yview)

        self.tree.tag_configure("odd",        background=self.PANEL)
        self.tree.tag_configure("even",       background=even_bg)
        self.tree.tag_configure("Registered", foreground=self.SUCCESS)
        self.tree.tag_configure("Pending",    foreground=self.PENDING)
        self.tree.tag_configure("Inactive",   foreground=self.INACTIVE)

        self.tree.bind("<<TreeviewSelect>>", self._on_selection_change)

    # ═══════════════════════════════════════════════════════════════
    # SORTING
    # ═══════════════════════════════════════════════════════════════
    def _sort_by(self, col):
        rows = [(self.tree.set(iid, col), iid) for iid in self.tree.get_children()]
        rev = (self._sort_state["col"] == col) and not self._sort_state["rev"]
        try:
            rows.sort(key=lambda x: int(x[0]), reverse=rev)
        except ValueError:
            rows.sort(key=lambda x: x[0].lower(), reverse=rev)
        for i, (_, iid) in enumerate(rows):
            self.tree.move(iid, "", i)
        self._sort_state["col"] = col
        self._sort_state["rev"] = rev
        self.sort_info.config(text=f"Sorted by: {col} {'\u2191' if not rev else '\u2193'}")

    # ═══════════════════════════════════════════════════════════════
    # CRUD OPERATIONS
    # ═══════════════════════════════════════════════════════════════
    def _status_of(self, row):
        try:
            return row[8] if len(row) > 8 else "Registered"
        except (IndexError, TypeError):
            return "Registered"

    def _gender_of(self, row):
        try:
            return row[6] if len(row) > 6 else ""
        except (IndexError, TypeError):
            return ""

    def _is_senior(self, row):
        try:
            return int(row[3]) >= 60
        except (ValueError, TypeError, IndexError):
            return False

    def _calc_age(self):
        try:
            bdate = datetime.strptime(self.entries["Birthdate"], "%Y-%m-%d").date()
            today = date.today()
            ag = today.year - bdate.year - (
                (today.month, today.day) < (bdate.month, bdate.day))
            self.age_lbl.config(text=f"Age: {ag} yrs", fg=self.SUCCESS)
            return ag
        except (ValueError, TypeError):
            self.age_lbl.config(text="Age: \u2014", fg=self.MUTED)
            return None

    def add_resident(self, event=None):
        fn = self.entries["First Name"].get().strip()
        ln = self.entries["Last Name"].get().strip()
        bd = self.entries["Birthdate"] if isinstance(self.entries["Birthdate"], str) else ""
        ct = self.entries["Contact"].get().strip()
        gn = self.gender_var.get()
        st = self.status_var.get()
        ag = self._calc_age()
        if not all([fn, ln, bd, ct]) or gn == "Select Gender":
            messagebox.showwarning("Missing Fields", "All fields are required.")
            return
        if ag is None:
            messagebox.showwarning("Invalid Date", "Please select a valid birthdate.")
            return
        database.add_resident(fn, ln, str(ag), ct, self.purok_id,
                               birthdate=bd, gender=gn, status=st,
                               photo_path=self.current_photo["path"])
        self.clear_form()
        self.refresh_table()
        self.update_stats()
        self.status_msg("Resident added successfully.", self.SUCCESS)

    def update_resident(self, event=None):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Select a resident to update.")
            return
        rid = self.tree.item(sel[0])["values"][0]
        fn = self.entries["First Name"].get().strip()
        ln = self.entries["Last Name"].get().strip()
        bd = self.entries["Birthdate"] if isinstance(self.entries["Birthdate"], str) else ""
        ct = self.entries["Contact"].get().strip()
        gn = self.gender_var.get()
        st = self.status_var.get()
        ag = self._calc_age()
        if not all([fn, ln, bd, ct]):
            messagebox.showwarning("Missing Fields", "All fields are required.")
            return
        if ag is None:
            messagebox.showwarning("Invalid Date", "Please select a valid birthdate.")
            return
        photo = self.current_photo["path"] if self.current_photo["path"] else None
        database.update_resident(rid, fn, ln, str(ag), ct,
                                  birthdate=bd, gender=gn, status=st,
                                  photo_path=photo)
        self.clear_form()
        self.refresh_table()
        self.update_stats()
        self.status_msg("Resident updated.", self.WARN)

    def delete_resident(self, event=None):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Select a resident to delete.")
            return
        rid = self.tree.item(sel[0])["values"][0]
        name = f"{self.tree.item(sel[0])['values'][1]} {self.tree.item(sel[0])['values'][2]}"
        if messagebox.askyesno("Confirm Delete", f"Delete {name}?"):
            database.delete_resident(rid)
            self.clear_form()
            self.refresh_table()
            self.update_stats()
            self.status_msg(f"Deleted: {name}", self.DANGER)

    def clear_form(self):
        for key, e in self.entries.items():
            if key == "Birthdate":
                continue
            if hasattr(e, "delete"):
                e.delete(0, tk.END)
        today = date.today()
        self.calendar_state.update(selected_date=today, temp_date=today,
                                    year=today.year, month=today.month)
        self.bd_display.config(text=today.strftime("%Y-%m-%d"))
        self.entries["Birthdate"] = today.strftime("%Y-%m-%d")
        self.gender_var.set("Select Gender")
        self.status_var.set("Registered")
        self.age_lbl.config(text="Age: \u2014", fg=self.MUTED)
        self.current_photo["path"] = ""
        self.thumb_lbl.config(image="", text="\U0001f464")
        self._thumb_img[0] = None
        self.thumb_border.config(bg=self.ACCENT2)
        self.photo_status_lbl.config(
            text="No photo  \u00b7  browse or use camera", fg=self.MUTED)

    def load_selected(self, event=None):
        sel = self.tree.selection()
        if not sel:
            return
        r = self.tree.item(sel[0])["values"]
        self.clear_form()
        self.entries["First Name"].insert(0, r[1])
        self.entries["Last Name"].insert(0,  r[2])
        if r[4]:
            try:
                bdate = datetime.strptime(str(r[4]), "%Y-%m-%d").date()
                self.calendar_state.update(selected_date=bdate, temp_date=bdate,
                                            year=bdate.year, month=bdate.month)
                self.bd_display.config(text=bdate.strftime("%Y-%m-%d"))
                self.entries["Birthdate"] = bdate.strftime("%Y-%m-%d")
            except ValueError:
                pass
        self.entries["Contact"].insert(0, r[6])
        self.gender_var.set(r[5] if r[5] else "Select Gender")
        self.status_var.set(r[7] if r[7] else "Registered")
        self._calc_age()
        row_full = self._get_selected_resident_row()
        if row_full and len(row_full) > 9 and row_full[9]:
            self.current_photo["path"] = row_full[9]
            self._update_thumb(row_full[9])

    # ═══════════════════════════════════════════════════════════════
    # NAVIGATION
    # ═══════════════════════════════════════════════════════════════
    def go_back(self):
        self.root.destroy()
        purok.run_purok_window(admin_username=self.admin_username)

    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to log out?"):
            self.root.destroy()
            import login
            login.run_login()

    # ═══════════════════════════════════════════════════════════════
    # SEARCH
    # ═══════════════════════════════════════════════════════════════
    def _on_search(self, *args):
        q = self.search_var.get().lower().strip()
        if q == "search residents...":
            q = ""
        self.refresh_table(query=q)

    # ═══════════════════════════════════════════════════════════════
    # EXPORT / IMPORT / PRINT
    # ═══════════════════════════════════════════════════════════════
    def _export_csv(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not path:
            return
        residents = database.get_residents_by_purok(self.purok_id)
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "First Name", "Last Name", "Age",
                             "Contact", "Birthdate", "Gender", "Status"])
            writer.writerows(residents)
        self.status_msg(f"Exported {len(residents)} records.", self.SUCCESS)

    def _import_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not path:
            return
        added = skipped = 0
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    database.add_resident(
                        row["First Name"].strip(), row["Last Name"].strip(),
                        row.get("Age", "").strip(), row["Contact"].strip(),
                        self.purok_id,
                        birthdate=row.get("Birthdate", "").strip(),
                        gender=row.get("Gender", "").strip(),
                        status=row.get("Status", "Registered").strip()
                    )
                    added += 1
                except Exception:
                    skipped += 1
        self.refresh_table()
        self.update_stats()
        self.status_msg(f"Imported {added} records. ({skipped} skipped)", self.WARN)

    def _print_list(self):
        residents = database.get_residents_by_purok(self.purok_id)
        tab = self.active_tab.get()
        if tab != "All":
            residents = [r for r in residents if self._status_of(r) == tab]
        rows_html = ""
        for i, r in enumerate(residents):
            st = self._status_of(r)
            sc = {"Registered": "#4fc97e", "Pending": "#f7a94f",
                  "Inactive": "#f74f6a"}.get(st, "#aaa")
            bg = "#13161e" if i % 2 == 0 else "#0d0f14"
            rows_html += (f'<tr style="background:{bg}"><td>{str(r[0]).zfill(3)}</td>'
                          f'<td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td>'
                          f'<td>{r[7] if len(r)>7 else ""}</td>'
                          f'<td>{r[6] if len(r)>6 else ""}</td>'
                          f'<td>{r[4]}</td>'
                          f'<td style="color:{sc};font-weight:bold">{st}</td></tr>')
        html = (f'<!DOCTYPE html><html><head><meta charset="utf-8">'
                f'<title>Resident List</title><style>'
                f'body{{font-family:monospace;background:#0d0f14;color:#e8ecf4;padding:30px}}'
                f'h2{{color:#4f8ef7}}p{{color:#6b7490;font-size:12px}}'
                f'table{{width:100%;border-collapse:collapse;margin-top:16px}}'
                f'th{{background:#13161e;color:#4f8ef7;padding:10px;text-align:left;'
                f'font-size:11px;border-bottom:2px solid #2a2f42}}'
                f'td{{padding:10px;font-size:12px;border-bottom:1px solid #1a1e2b}}'
                f'@media print{{body{{background:white;color:#111}}'
                f'th{{background:#f0f4ff;color:#1a56db}}td{{border-bottom:1px solid #e5e9f2}}'
                f'tr{{background:white!important}}}}</style></head><body>'
                f'<h2>\U0001f3db RIMS -- Resident Registry</h2>'
                f'<p>Purok: <b>{self.purok_name}</b> \u00b7 Total: <b>{len(residents)}</b>'
                f' \u00b7 {datetime.now().strftime("%B %d, %Y %I:%M %p")}</p>'
                f'<table><thead><tr><th>ID</th><th>FIRST NAME</th><th>LAST NAME</th>'
                f'<th>AGE</th><th>BIRTHDATE</th><th>GENDER</th>'
                f'<th>CONTACT</th><th>STATUS</th></tr></thead>'
                f'<tbody>{rows_html}</tbody></table>'
                f'<script>window.onload=()=>window.print()</script></body></html>')
        import tempfile, webbrowser
        with tempfile.NamedTemporaryFile(
                "w", suffix=".html", delete=False, encoding="utf-8") as tmp:
            tmp.write(html)
            webbrowser.open(f"file://{tmp.name}")

    # ═══════════════════════════════════════════════════════════════
    # BATCH OPERATIONS
    # ═══════════════════════════════════════════════════════════════
    def batch_delete(self):
        sel = self.tree.selection()
        if not sel:
            return
        count = len(sel)
        names = []
        for iid in sel:
            vals = self.tree.item(iid)["values"]
            names.append(f"{vals[1]} {vals[2]}")
        if count == 1:
            msg = f"Delete {names[0]}?"
        else:
            preview = "\n  \u2022 " + "\n  \u2022 ".join(names[:10])
            if count > 10:
                preview += f"\n  \u2026 and {count - 10} more"
            msg = f"Delete {count} residents?{preview}"
        if messagebox.askyesno("Batch Delete", msg):
            for iid in sel:
                rid = self.tree.item(iid)["values"][0]
                try:
                    database.delete_resident(int(str(rid).lstrip("0") or "0"))
                except Exception:
                    pass
            self.status_msg(f"Deleted {count} resident(s).", self.DANGER)
            self.refresh_table()
            self.update_stats()

    def batch_export(self):
        sel = self.tree.selection()
        if not sel:
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Export Selected Residents"
        )
        if not path:
            return
        rows = []
        for iid in sel:
            vals = self.tree.item(iid)["values"]
            rows.append((
                str(vals[0]).lstrip("0") or "0",
                vals[1], vals[2], vals[3],
                vals[7], vals[5], vals[4], vals[6]
            ))
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "First Name", "Last Name", "Age",
                             "Status", "Gender", "Birthdate", "Contact"])
            writer.writerows(rows)
        self.status_msg(f"Exported {len(rows)} selected record(s).", self.SUCCESS)

    # ═══════════════════════════════════════════════════════════════
    # REFRESH / STATS
    # ═══════════════════════════════════════════════════════════════
    def update_stats(self):
        residents = database.get_residents_by_purok(self.purok_id)
        self.stat_labels["total"].config(text=str(len(residents)))
        self.stat_labels["registered"].config(
            text=str(sum(1 for r in residents if self._status_of(r) == "Registered")))
        self.stat_labels["pending"].config(
            text=str(sum(1 for r in residents if self._status_of(r) == "Pending")))
        self.stat_labels["inactive"].config(
            text=str(sum(1 for r in residents if self._status_of(r) == "Inactive")))
        self.stat_labels["seniors"].config(
            text=str(sum(1 for r in residents if self._is_senior(r))))
        self.stat_labels["male"].config(
            text=str(sum(1 for r in residents if self._gender_of(r) == "Male")))
        self.stat_labels["female"].config(
            text=str(sum(1 for r in residents if self._gender_of(r) == "Female")))

    def refresh_table(self, query=""):
        for row in self.tree.get_children():
            self.tree.delete(row)
        residents = database.get_residents_by_purok(self.purok_id)
        residents.sort(key=lambda r: r[2].lower())
        tab = self.active_tab.get()
        if tab != "All":
            residents = [r for r in residents if self._status_of(r) == tab]
        if query:
            residents = [r for r in residents
                         if query in " ".join(str(v) for v in r).lower()]
        for i, r in enumerate(residents):
            st = self._status_of(r)
            bd = r[7] if len(r) > 7 else ""
            gn = r[6] if len(r) > 6 else ""
            self.tree.insert("", "end",
                             values=(f"{r[0]:03d}", r[1], r[2], r[3],
                                     bd, gn, r[4], st),
                             tags=("odd" if i % 2 == 0 else "even", st))

    # ═══════════════════════════════════════════════════════════════
    # RESIDENT INFO
    # ═══════════════════════════════════════════════════════════════
    def _get_selected_resident_row(self):
        sel = self.tree.selection()
        if not sel:
            return None
        vals = self.tree.item(sel[0])["values"]
        try:
            rid = int(str(vals[0]).lstrip("0") or "0")
        except ValueError:
            return None
        return database.get_resident_by_id(rid)

    def open_info(self, event=None):
        row = self._get_selected_resident_row()
        if row is None:
            return
        open_resident_info(
            self.root, row, self.purok_name,
            on_close=lambda: self.refresh_table(),
            on_photo_updated=lambda p: self.refresh_table()
        )

    # ═══════════════════════════════════════════════════════════════
    # CONTEXT MENU
    # ═══════════════════════════════════════════════════════════════
    def _build_context_menu(self):
        ctx = tk.Menu(self.root, tearoff=0, bg=self.PANEL, fg=self.TEXT,
                      activebackground=self.ACCENT, activeforeground="white",
                      font=_t.font("Courier", 9), relief="flat", bd=0)
        ctx.add_command(label="\U0001f50d  View Info", command=self.open_info)
        ctx.add_separator()
        ctx.add_command(label="\u270e  Edit", command=self.load_selected)
        ctx.add_command(label="\u2715  Delete", command=self.delete_resident)
        ctx.add_separator()
        ctx.add_command(label="\uff0b  Add New", command=self.clear_form)

        def show_ctx(event):
            iid = self.tree.identify_row(event.y)
            if iid:
                self.tree.selection_set(iid)
                ctx.post(event.x_root, event.y_root)
        return show_ctx

    # ═══════════════════════════════════════════════════════════════
    # EVENT BINDINGS
    # ═══════════════════════════════════════════════════════════════
    def _bind_events(self):
        show_ctx = self._build_context_menu()
        self.tree.bind("<Double-1>", self.open_info)
        self.tree.bind("<Button-3>", show_ctx)
        self.entries["Contact"].bind("<Return>", self.add_resident)
        self.root.bind("<Delete>", self.delete_resident)
        self.root.bind("<Control-e>", self.update_resident)
        self.root.bind("<Escape>", lambda e: self.clear_form())

    # ═══════════════════════════════════════════════════════════════
    # RUN
    # ═══════════════════════════════════════════════════════════════
    def run(self):
        self.root.mainloop()
