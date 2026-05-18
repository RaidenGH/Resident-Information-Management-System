import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import database
import csv
import purok
from logo import make_logo_canvas
from datetime import date, datetime
import calendar as cal


def run_app(purok_id, purok_name):

    # ── Palette ───────────────────────────────────────────────────────────────
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
    PENDING_C  = "#f7a94f"
    INACTIVE_C = "#f74f6a"

    # ── Root — fullscreen ─────────────────────────────────────────────────────
    root = tk.Tk()
    root.title(f"Residents — {purok_name}")
    root.configure(bg=BG)
    root.state("zoomed")
    root.resizable(True, True)

    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=1)

    # ═══════════════════════════════════════════════════════════════
    # LEFT SIDEBAR
    # ═══════════════════════════════════════════════════════════════
    sidebar = tk.Frame(root, bg=CARD, width=270,
                       highlightthickness=1, highlightbackground=BORDER)
    sidebar.grid(row=0, column=0, sticky="nsew")
    sidebar.grid_propagate(False)
    sidebar.grid_columnconfigure(0, weight=1)

    tk.Frame(sidebar, bg=ACCENT, height=3).grid(row=0, column=0, sticky="ew")

    logo_c = make_logo_canvas(sidebar, scale=0.52, bg=CARD)
    logo_c.grid(row=1, column=0, sticky="ew", padx=10, pady=(14, 0))

    tk.Label(sidebar, text=f"▸  {purok_name}",
             font=("Courier", 8, "bold"),
             fg=ACCENT, bg=CARD).grid(row=2, column=0, sticky="w", padx=18, pady=(2, 0))

    tk.Frame(sidebar, bg=BORDER, height=1).grid(
        row=3, column=0, sticky="ew", padx=18, pady=(8, 0))

    def sidebar_section(row, text):
        f = tk.Frame(sidebar, bg=CARD)
        f.grid(row=row, column=0, sticky="ew", padx=18, pady=(14, 0))
        tk.Label(f, text="▸ " + text, font=("Courier", 7, "bold"),
                 fg=ACCENT, bg=CARD).pack(side="left")
        tk.Frame(f, bg=BORDER, height=1).pack(
            side="left", fill="x", expand=True, padx=(6, 0), pady=5)

    sidebar_section(4, "RESIDENT DETAILS")

    entries = {}

    def make_sidebar_entry(grid_row, key, show=None):
        wrap = tk.Frame(sidebar, bg=CARD)
        wrap.grid(row=grid_row, column=0, sticky="ew", padx=18, pady=3)
        wrap.grid_columnconfigure(0, weight=1)
        tk.Label(wrap, text=key, font=("Courier", 8, "bold"),
                 fg=MUTED, bg=CARD).pack(anchor="w")
        inner = tk.Frame(wrap, bg=PANEL,
                         highlightthickness=1, highlightbackground=BORDER)
        inner.pack(fill="x", pady=(2, 0))
        e = tk.Entry(inner, show=show, bg=PANEL, fg=TEXT,
                     font=("Courier", 10), relief="flat",
                     insertbackground=ACCENT, bd=0)
        e.pack(fill="x", padx=8, pady=5)
        def _in(ev):  inner.config(highlightbackground=ACCENT)
        def _out(ev): inner.config(highlightbackground=BORDER)
        e.bind("<FocusIn>",  _in)
        e.bind("<FocusOut>", _out)
        entries[key] = e

    make_sidebar_entry(5, "First Name")
    make_sidebar_entry(6, "Last Name")

    # ── Birthdate + auto-age with custom calendar ─────────────────────────────
    bd_wrap = tk.Frame(sidebar, bg=CARD)
    bd_wrap.grid(row=7, column=0, sticky="ew", padx=18, pady=3)
    bd_wrap.grid_columnconfigure(0, weight=1)
    tk.Label(bd_wrap, text="Birthdate",
             font=("Courier", 8, "bold"), fg=MUTED, bg=CARD).pack(anchor="w")

    bd_control = tk.Frame(bd_wrap, bg=CARD)
    bd_control.pack(fill="x", pady=(2, 0))
    bd_control.grid_columnconfigure(0, weight=1)

    # Date display
    bd_display = tk.Label(bd_control, text="Select date...",
                          font=("Courier", 9), fg=TEXT, bg=PANEL,
                          relief="solid", bd=1, highlightthickness=1,
                          highlightbackground=BORDER)
    bd_display.grid(row=0, column=0, sticky="ew", padx=0, pady=0, ipady=4)

    # Calendar state
    calendar_state = {
        "year": date.today().year,
        "month": date.today().month,
        "selected_date": date.today(),
        "temp_date": date.today(),
    }

    # Calendar window reference
    calendar_window_ref = [None]

    def open_calendar():
        if calendar_window_ref[0] is not None and calendar_window_ref[0].winfo_exists():
            calendar_window_ref[0].destroy()

        cal_win = tk.Toplevel(root)
        cal_win.title("Select Date")
        cal_win.geometry("380x250")
        cal_win.resizable(False, False)
        cal_win.configure(bg=CARD)
        cal_win.grab_set()

        # Make window appear near the calendar button
        cal_win.transient(root)

        calendar_window_ref[0] = cal_win

        # ── Header with year/month selectors ──────────────────────────────────
        header = tk.Frame(cal_win, bg=CARD)
        header.pack(fill="x", padx=8, pady=8)

        # Left arrow
        def prev_month():
            if calendar_state["month"] == 1:
                calendar_state["month"] = 12
                calendar_state["year"] -= 1
            else:
                calendar_state["month"] -= 1
            refresh_calendar()

        tk.Button(header, text="◀", command=prev_month,
                  bg=PANEL, fg=ACCENT, font=("Courier", 10, "bold"),
                  relief="flat", bd=0, cursor="hand2", width=2, padx=2, pady=1).pack(side="left", padx=2)

        # Year selector with SCROLLABLE list
        def open_year_picker():
            year_win = tk.Toplevel(cal_win)
            year_win.title("Select Year")
            year_win.geometry("125x300")
            year_win.configure(bg=CARD)
            year_win.resizable(False, False)
            year_win.grab_set()

            tk.Label(year_win, text="Year", font=("Courier", 10, "bold"),
                     fg=TEXT, bg=CARD).pack(pady=5)

            # Scrollable year list
            frame = tk.Frame(year_win, bg=CARD)
            frame.pack(fill="both", expand=True, padx=8, pady=8)

            canvas = tk.Canvas(frame, bg=PANEL, highlightthickness=1,
                               highlightbackground=BORDER, height=200)
            scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview,
                                     bg=BORDER, troughcolor=CARD, width=4,
                                     relief="flat", highlightthickness=0)
            scrollable_frame = tk.Frame(canvas, bg=PANEL)

            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )

            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)

            # Mouse wheel scrolling
            def _on_mousewheel(event):
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            canvas.bind_all("<MouseWheel>", _on_mousewheel)

            # Generate year buttons (50 years back to 50 years forward)
            start_year = date.today().year - 50
            end_year = date.today().year + 50

            for y in range(start_year, end_year + 1):
                btn_color = ACCENT if y == calendar_state["year"] else PANEL
                btn_fg = "white" if y == calendar_state["year"] else TEXT

                def select_year(year=y):
                    calendar_state["year"] = year
                    year_win.destroy()
                    refresh_calendar()

                btn = tk.Button(scrollable_frame, text=str(y),
                                command=select_year,
                                bg=btn_color, fg=btn_fg,
                                font=("Courier", 8),
                                relief="flat", bd=0, cursor="hand2",
                                width=12)
                btn.pack(pady=1)

            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            # Scroll to current year
            def scroll_to_current(*args):
                year_index = calendar_state["year"] - start_year
                canvas.yview_moveto((year_index) / (end_year - start_year))
            
            root.after(100, scroll_to_current)

        year_btn = tk.Button(header, text=str(calendar_state["year"]),
                             command=open_year_picker,
                             bg=PANEL, fg=ACCENT, font=("Courier", 9, "bold"),
                             relief="flat", bd=0, cursor="hand2", width=4, padx=2, pady=1)
        year_btn.pack(side="left", padx=3)

        # Month selector with SCROLLABLE list
        def open_month_picker():
            month_win = tk.Toplevel(cal_win)
            month_win.title("Select Month")
            month_win.geometry("150x320")
            month_win.configure(bg=CARD)
            month_win.resizable(False, False)
            month_win.grab_set()

            tk.Label(month_win, text="Month", font=("Courier", 10, "bold"),
                     fg=TEXT, bg=CARD).pack(pady=5)

            # Scrollable month list
            frame = tk.Frame(month_win, bg=CARD)
            frame.pack(fill="both", expand=True, padx=8, pady=8)

            canvas = tk.Canvas(frame, bg=PANEL, highlightthickness=1,
                               highlightbackground=BORDER)
            scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview,
                                     bg=BORDER, troughcolor=CARD, width=4,
                                     relief="flat", highlightthickness=0)
            scrollable_frame = tk.Frame(canvas, bg=PANEL)

            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )

            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)

            # Mouse wheel scrolling
            def _on_mousewheel(event):
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            canvas.bind_all("<MouseWheel>", _on_mousewheel)

            month_names = ["January", "February", "March", "April", "May", "June",
                           "July", "August", "September", "October", "November", "December"]

            for i, month_name in enumerate(month_names):
                btn_color = ACCENT if i + 1 == calendar_state["month"] else PANEL
                btn_fg = "white" if i + 1 == calendar_state["month"] else TEXT

                def select_month(m=i + 1):
                    calendar_state["month"] = m
                    month_win.destroy()
                    refresh_calendar()

                btn = tk.Button(scrollable_frame, text=month_name,
                                command=select_month,
                                bg=btn_color, fg=btn_fg,
                                font=("Courier", 8),
                                relief="flat", bd=0, cursor="hand2",
                                width=14)
                btn.pack(pady=1)

            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

        month_btn = tk.Button(header, text=cal.month_name[calendar_state["month"]],
                              command=open_month_picker,
                              bg=PANEL, fg=ACCENT, font=("Courier", 9, "bold"),
                              relief="flat", bd=0, cursor="hand2", width=10, padx=2, pady=1)
        month_btn.pack(side="left", padx=3, fill="x", expand=True)

        # Right arrow
        def next_month():
            if calendar_state["month"] == 12:
                calendar_state["month"] = 1
                calendar_state["year"] += 1
            else:
                calendar_state["month"] += 1
            refresh_calendar()

        tk.Button(header, text="▶", command=next_month,
                  bg=PANEL, fg=ACCENT, font=("Courier", 10, "bold"),
                  relief="flat", bd=0, cursor="hand2", width=2, padx=2, pady=1).pack(side="left", padx=2)

        # Today button
        def go_today():
            today = date.today()
            calendar_state["year"] = today.year
            calendar_state["month"] = today.month
            calendar_state["temp_date"] = today
            refresh_calendar()

        tk.Button(header, text="Today", command=go_today,
                  bg=SUCCESS, fg="white", font=("Courier", 7, "bold"),
                  relief="flat", bd=0, cursor="hand2", padx=3, pady=1).pack(side="right", padx=2)

        # ── Calendar grid ─────────────────────────────────────────────────────
        calendar_frame = tk.Frame(cal_win, bg=CARD)
        calendar_frame.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        calendar_frame.grid_columnconfigure(list(range(7)), weight=1)

        # Weekday headers
        weekdays = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
        for i, day in enumerate(weekdays):
            tk.Label(calendar_frame, text=day,
                     font=("Courier", 8, "bold"), fg=ACCENT, bg=CARD).grid(
                         row=0, column=i, sticky="nsew", padx=1, pady=2)

        # Day buttons (will be updated by refresh_calendar)
        calendar_buttons = []

        def refresh_calendar():
            # Clear previous buttons
            for btn in calendar_buttons:
                btn.destroy()
            calendar_buttons.clear()

            # Update header buttons
            year_btn.config(text=str(calendar_state["year"]))
            month_btn.config(text=cal.month_name[calendar_state["month"]])

            # Get calendar for the month
            month_cal = cal.monthcalendar(calendar_state["year"], calendar_state["month"])
            today = date.today()

            for week_num, week in enumerate(month_cal):
                for day_num, day in enumerate(week):
                    if day == 0:
                        # Empty cell for days from other months
                        empty = tk.Label(calendar_frame, text="", bg=CARD)
                        empty.grid(row=week_num + 1, column=day_num, sticky="nsew", padx=1, pady=1)
                        calendar_buttons.append(empty)
                    else:
                        current_date = date(calendar_state["year"], calendar_state["month"], day)

                        # Determine button color
                        if current_date == today:
                            btn_bg = ACCENT2  # Today
                            btn_fg = "white"
                        elif current_date == calendar_state["temp_date"]:
                            btn_bg = ACCENT  # Selected
                            btn_fg = "white"
                        else:
                            btn_bg = PANEL
                            btn_fg = TEXT

                        def select_date(d=day, cd=current_date):
                            calendar_state["temp_date"] = cd
                            refresh_calendar()

                        btn = tk.Button(calendar_frame, text=str(day),
                                       command=select_date,
                                       bg=btn_bg, fg=btn_fg,
                                       font=("Courier", 8, "bold"),
                                       relief="flat", bd=0, cursor="hand2",
                                       width=3, height=1)
                        btn.grid(row=week_num + 1, column=day_num, sticky="nsew", padx=1, pady=1)
                        calendar_buttons.append(btn)

        # ── Footer with Confirm/Cancel ────────────────────────────────────────
        footer = tk.Frame(cal_win, bg=CARD)
        footer.pack(fill="x", padx=8, pady=(0, 8))
        footer.grid_columnconfigure([0, 1], weight=1)

        def confirm():
            calendar_state["selected_date"] = calendar_state["temp_date"]
            bd_display.config(text=calendar_state["selected_date"].strftime("%Y-%m-%d"))
            entries["Birthdate"] = calendar_state["selected_date"].strftime("%Y-%m-%d")
            _calc_age()
            cal_win.destroy()

        def cancel():
            calendar_state["temp_date"] = calendar_state["selected_date"]
            cal_win.destroy()

        tk.Button(footer, text="✓ Confirm", command=confirm,
                  bg=SUCCESS, fg="white", font=("Courier", 8, "bold"),
                  relief="flat", bd=0, cursor="hand2", padx=8, pady=2).grid(row=0, column=0, sticky="ew", padx=2)

        tk.Button(footer, text="✕ Cancel", command=cancel,
                  bg=DANGER, fg="white", font=("Courier", 8, "bold"),
                  relief="flat", bd=0, cursor="hand2", padx=8, pady=2).grid(row=0, column=1, sticky="ew", padx=2)

        refresh_calendar()

    # Calendar button
    cal_btn = tk.Button(bd_control, text="📅", command=open_calendar,
                        bg=ACCENT, fg="white", font=("Courier", 9, "bold"),
                        relief="flat", bd=0, cursor="hand2", padx=4, pady=2)
    cal_btn.grid(row=0, column=1, sticky="ew", padx=(4, 0), pady=0)
    bd_control.grid_columnconfigure(1, weight=0)

    # Initialize with today's date
    bd_display.config(text=calendar_state["selected_date"].strftime("%Y-%m-%d"))
    entries["Birthdate"] = calendar_state["selected_date"].strftime("%Y-%m-%d")

    age_lbl = tk.Label(bd_wrap, text="Age: —",
                       font=("Courier", 8, "bold"), fg=MUTED, bg=CARD)
    age_lbl.pack(anchor="w", pady=(3, 0))

    def _calc_age():
        try:
            bdate = datetime.strptime(entries["Birthdate"], "%Y-%m-%d").date()
            today = date.today()
            ag = today.year - bdate.year - (
                (today.month, today.day) < (bdate.month, bdate.day))
            age_lbl.config(text=f"Age: {ag} yrs", fg=SUCCESS)
            return ag
        except (ValueError, TypeError):
            age_lbl.config(text="Age: —", fg=MUTED)
            return None

    _calc_age()

    # ── Gender dropdown ───────────────────────────────────────────
    gd_wrap = tk.Frame(sidebar, bg=CARD)
    gd_wrap.grid(row=8, column=0, sticky="ew", padx=18, pady=3)
    tk.Label(gd_wrap, text="Gender", font=("Courier", 8, "bold"),
             fg=MUTED, bg=CARD).pack(anchor="w")
    gender_var = tk.StringVar(value="Select Gender")
    gd_inner = tk.Frame(gd_wrap, bg=PANEL,
                        highlightthickness=1, highlightbackground=BORDER)
    gd_inner.pack(fill="x", pady=(2, 0))
    gd_dd = tk.OptionMenu(gd_inner, gender_var, "Male", "Female", "Other")
    gd_dd.config(bg=PANEL, fg=TEXT, font=("Courier", 9), relief="flat",
                 bd=0, activebackground=ACCENT, activeforeground="white",
                 highlightthickness=0, anchor="w")
    gd_dd["menu"].config(bg=PANEL, fg=TEXT, font=("Courier", 9),
                         relief="flat", activebackground=ACCENT, activeforeground="white")
    gd_dd.pack(fill="x", padx=4, pady=2)

    # ── Status dropdown ───────────────────────────────────────────
    st_wrap = tk.Frame(sidebar, bg=CARD)
    st_wrap.grid(row=9, column=0, sticky="ew", padx=18, pady=3)
    tk.Label(st_wrap, text="Status", font=("Courier", 8, "bold"),
             fg=MUTED, bg=CARD).pack(anchor="w")
    status_var = tk.StringVar(value="Registered")
    st_inner = tk.Frame(st_wrap, bg=PANEL,
                        highlightthickness=1, highlightbackground=BORDER)
    st_inner.pack(fill="x", pady=(2, 0))
    st_dd = tk.OptionMenu(st_inner, status_var, "Registered", "Pending", "Inactive")
    st_dd.config(bg=PANEL, fg=TEXT, font=("Courier", 9), relief="flat",
                 bd=0, activebackground=ACCENT, activeforeground="white",
                 highlightthickness=0, anchor="w")
    st_dd["menu"].config(bg=PANEL, fg=TEXT, font=("Courier", 9),
                         relief="flat", activebackground=ACCENT, activeforeground="white")
    st_dd.pack(fill="x", padx=4, pady=2)

    make_sidebar_entry(10, "Contact")

    sidebar_section(11, "ACTIONS")

    def make_btn(row, label, color, active_color, cmd, fg_color="white"):
        btn = tk.Button(sidebar, text=label, command=cmd,
                        bg=color, fg=fg_color,
                        activebackground=active_color, activeforeground=fg_color,
                        font=("Courier", 9, "bold"),
                        relief="flat", bd=0, cursor="hand2")
        btn.grid(row=row, column=0, sticky="ew", padx=18, pady=2, ipady=7)
        return btn

    # ── CRUD ──────────────────────────────────────────────────────
    def add_resident(event=None):
        fn = entries["First Name"].get().strip()
        ln = entries["Last Name"].get().strip()
        bd = entries["Birthdate"]
        ct = entries["Contact"].get().strip()
        gn = gender_var.get()
        st = status_var.get()
        ag = _calc_age()
        if not all([fn, ln, bd, ct]) or gn == "Select Gender":
            messagebox.showwarning("Missing Fields", "All fields are required.")
            return
        if ag is None:
            messagebox.showwarning("Invalid Date", "Please select a valid birthdate.")
            return
        database.add_resident(fn, ln, str(ag), ct, purok_id,
                               birthdate=bd, gender=gn, status=st)
        clear_form(); refresh_table(); update_stats()
        status_msg("Resident added successfully.", SUCCESS)

    def update_resident(event=None):
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Select a resident to update.")
            return
        rid = tree.item(sel[0])["values"][0]
        fn = entries["First Name"].get().strip()
        ln = entries["Last Name"].get().strip()
        bd = entries["Birthdate"]
        ct = entries["Contact"].get().strip()
        gn = gender_var.get()
        st = status_var.get()
        ag = _calc_age()
        if not all([fn, ln, bd, ct]):
            messagebox.showwarning("Missing Fields", "All fields are required.")
            return
        if ag is None:
            messagebox.showwarning("Invalid Date", "Please select a valid birthdate.")
            return
        database.update_resident(rid, fn, ln, str(ag), ct,
                                  birthdate=bd, gender=gn, status=st)
        clear_form(); refresh_table(); update_stats()
        status_msg("Resident updated.", WARN)

    def delete_resident(event=None):
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Select a resident to delete.")
            return
        rid  = tree.item(sel[0])["values"][0]
        name = f"{tree.item(sel[0])['values'][1]} {tree.item(sel[0])['values'][2]}"
        if messagebox.askyesno("Confirm Delete", f"Delete {name}?"):
            database.delete_resident(rid)
            clear_form(); refresh_table(); update_stats()
            status_msg(f"Deleted: {name}", DANGER)

    def go_back():
        root.destroy()
        purok.run_purok_window()

    def logout():
        if messagebox.askyesno("Logout", "Are you sure you want to log out?"):
            root.destroy()
            import login
            login.run_login()

    make_btn(12, "＋  Add Resident",    ACCENT,  "#3a7ce8", add_resident)
    make_btn(13, "✎  Update Selected", WARN,    "#d9903a", update_resident, "#0d0f14")
    make_btn(14, "✕  Delete Selected", DANGER,  "#d93a52", delete_resident)

    tk.Frame(sidebar, bg=BORDER, height=1).grid(
        row=15, column=0, sticky="ew", padx=18, pady=(10, 0))
    make_btn(16, "← Back to Puroks", PANEL, BORDER, go_back, MUTED)

    sidebar.grid_rowconfigure(17, weight=1)
    tk.Label(sidebar, text="© BRGY System  v1.0",
             font=("Courier", 7), fg=BORDER, bg=CARD).grid(
                 row=18, column=0, pady=(0, 10))

    # ═══════════════════════════════════════════════════════════════
    # RIGHT MAIN PANEL
    # ═══════════════════════════════════════════════════════════════
    main = tk.Frame(root, bg=BG)
    main.grid(row=0, column=1, sticky="nsew")
    main.grid_rowconfigure(4, weight=1)
    main.grid_columnconfigure(0, weight=1)

    tk.Frame(main, bg=ACCENT2, height=3).grid(row=0, column=0, sticky="ew")

    # ── Topbar ────────────────────────────────────────────────────
    topbar = tk.Frame(main, bg=BG)
    topbar.grid(row=1, column=0, sticky="ew", padx=20, pady=(14, 8))
    topbar.grid_columnconfigure(1, weight=1)

    tf = tk.Frame(topbar, bg=BG)
    tf.grid(row=0, column=0, sticky="w")
    tk.Label(tf, text="Resident", font=("Georgia", 20, "bold"),
             fg=TEXT, bg=BG).pack(side="left")
    tk.Label(tf, text=" Registry", font=("Georgia", 20, "italic"),
             fg=ACCENT, bg=BG).pack(side="left")

    search_wrap = tk.Frame(topbar, bg=PANEL,
                           highlightthickness=1, highlightbackground=BORDER)
    search_wrap.grid(row=0, column=1, sticky="ew", padx=(20, 12))
    tk.Label(search_wrap, text="⌕", font=("Courier", 11),
             fg=MUTED, bg=PANEL).pack(side="left", padx=(8, 2))
    search_var = tk.StringVar()
    search_entry = tk.Entry(search_wrap, textvariable=search_var,
                            bg=PANEL, fg=TEXT, font=("Courier", 10),
                            relief="flat", insertbackground=ACCENT, bd=0)
    search_entry.pack(side="left", fill="x", expand=True, pady=6, padx=(0, 8))
    search_entry.insert(0, "Search residents...")

    def _sf_in(e):
        if search_entry.get() == "Search residents...":
            search_entry.delete(0, tk.END)
        search_wrap.config(highlightbackground=ACCENT)
    def _sf_out(e):
        if not search_entry.get():
            search_entry.insert(0, "Search residents...")
        search_wrap.config(highlightbackground=BORDER)
    search_entry.bind("<FocusIn>",  _sf_in)
    search_entry.bind("<FocusOut>", _sf_out)
    def _on_search(*a):
        q = search_var.get().lower().strip()
        if q == "search residents...": q = ""
        refresh_table(query=q)
    search_var.trace_add("write", _on_search)

    right_tools = tk.Frame(topbar, bg=BG)
    right_tools.grid(row=0, column=2, sticky="e")

    def make_tool_btn(parent, text, color, cmd):
        b = tk.Button(parent, text=text, command=cmd,
                      bg=PANEL, fg=color,
                      activebackground=BORDER, activeforeground=color,
                      font=("Courier", 8, "bold"),
                      relief="flat", bd=0, cursor="hand2",
                      highlightthickness=1, highlightbackground=BORDER)
        b.pack(side="left", padx=3, ipady=5, ipadx=10)
        return b

    def export_csv():
        path = filedialog.asksaveasfilename(
            defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not path: return
        residents = database.get_residents_by_purok(purok_id)
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["ID","First Name","Last Name","Age",
                             "Contact","Birthdate","Gender","Status"])
            writer.writerows(residents)
        status_msg(f"Exported {len(residents)} records.", SUCCESS)

    def import_csv():
        path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not path: return
        added = skipped = 0
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    database.add_resident(
                        row["First Name"].strip(), row["Last Name"].strip(),
                        row.get("Age","").strip(), row["Contact"].strip(),
                        purok_id,
                        birthdate=row.get("Birthdate","").strip(),
                        gender=row.get("Gender","").strip(),
                        status=row.get("Status","Registered").strip()
                    )
                    added += 1
                except Exception:
                    skipped += 1
        refresh_table(); update_stats()
        status_msg(f"Imported {added} records. ({skipped} skipped)", WARN)

    def print_list():
        import tempfile, webbrowser
        residents = database.get_residents_by_purok(purok_id)
        tab = active_tab.get()
        if tab != "All":
            residents = [r for r in residents if _status_of(r) == tab]

        rows_html = ""
        for i, r in enumerate(residents):
            st = _status_of(r)
            sc = {"Registered": "#4fc97e",
                  "Pending":    "#f7a94f",
                  "Inactive":   "#f74f6a"}.get(st, "#aaa")
            bg = "#13161e" if i % 2 == 0 else "#0d0f14"
            rows_html += f"""<tr style="background:{bg}">
              <td>{str(r[0]).zfill(3)}</td>
              <td>{r[1]}</td><td>{r[2]}</td>
              <td>{r[3]}</td>
              <td>{r[7] if len(r) > 7 else ''}</td>
              <td>{r[6] if len(r) > 6 else ''}</td>
              <td>{r[4]}</td>
              <td style="color:{sc};font-weight:bold">{st}</td>
            </tr>"""

        html = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
        <title>Resident List — {purok_name}</title>
        <style>
          body{{font-family:monospace;background:#0d0f14;color:#e8ecf4;padding:30px;margin:0}}
          h2{{color:#4f8ef7;margin-bottom:4px}} p{{color:#6b7490;font-size:12px;margin-top:0}}
          table{{width:100%;border-collapse:collapse;margin-top:16px}}
          th{{background:#13161e;color:#4f8ef7;padding:10px 12px;text-align:left;
              font-size:11px;letter-spacing:1px;border-bottom:2px solid #2a2f42}}
          td{{padding:10px 12px;font-size:12px;border-bottom:1px solid #1a1e2b}}
          @media print{{
            body{{background:white;color:#111;padding:20px}}
            h2{{color:#1a56db}} p{{color:#555}}
            th{{background:#f0f4ff;color:#1a56db;border-bottom:2px solid #c7d7f9}}
            td{{border-bottom:1px solid #e5e9f2;color:#222}}
            tr{{background:white!important}}
          }}
        </style></head><body>
        <h2>🏛 RIMS — Resident Registry</h2>
        <p>Purok: <b>{purok_name}</b> &nbsp;·&nbsp; Total: <b>{len(residents)}</b>
           &nbsp;·&nbsp; {datetime.now().strftime('%B %d, %Y  %I:%M %p')}</p>
        <table><thead><tr>
          <th>ID</th><th>FIRST NAME</th><th>LAST NAME</th>
          <th>AGE</th><th>BIRTHDATE</th><th>GENDER</th>
          <th>CONTACT</th><th>STATUS</th>
        </tr></thead><tbody>{rows_html}</tbody></table>
        <script>window.onload=()=>window.print()</script>
        </body></html>"""

        with tempfile.NamedTemporaryFile("w", suffix=".html",
                                         delete=False, encoding="utf-8") as tmp:
            tmp.write(html)
            webbrowser.open(f"file://{tmp.name}")

    make_tool_btn(right_tools, "⬆  Export", SUCCESS, export_csv)
    make_tool_btn(right_tools, "⬇  Import", ACCENT,  import_csv)
    make_tool_btn(right_tools, "🖨  Print",  WARN,    print_list)

    # Logout pill
    lo_outer = tk.Frame(right_tools, bg="#3d0b14",
                        highlightthickness=1, highlightbackground="#7a1a2e")
    lo_outer.pack(side="left", padx=(10, 0))
    lo_btn = tk.Button(lo_outer, text="⏻  LOG OUT", command=logout,
                       bg="#1e0a10", fg=DANGER,
                       activebackground="#3d0b14", activeforeground="#ff8099",
                       font=("Courier", 8, "bold"),
                       relief="flat", bd=0, cursor="hand2", padx=12, pady=5)
    lo_btn.pack()
    def _lo_in(e):  lo_outer.config(highlightbackground=DANGER);   lo_btn.config(bg="#2d0f1a", fg="#ff6b85")
    def _lo_out(e): lo_outer.config(highlightbackground="#7a1a2e"); lo_btn.config(bg="#1e0a10", fg=DANGER)
    lo_btn.bind("<Enter>", _lo_in); lo_btn.bind("<Leave>", _lo_out)
    lo_outer.bind("<Enter>", _lo_in); lo_outer.bind("<Leave>", _lo_out)

    # ── Quick Stats bar ───────────────────────────────────────────
    stats_frame = tk.Frame(main, bg=CARD,
                           highlightthickness=1, highlightbackground=BORDER)
    stats_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 8))

    stat_labels = {}

    def make_stat(parent, key, title, color):
        f = tk.Frame(parent, bg=PANEL,
                     highlightthickness=1, highlightbackground=BORDER)
        f.pack(side="left", padx=8, pady=8, ipadx=10, ipady=4)
        tk.Label(f, text=title, font=("Courier", 7, "bold"),
                 fg=MUTED, bg=PANEL).pack(anchor="w", padx=8, pady=(5, 0))
        lbl = tk.Label(f, text="0", font=("Courier", 20, "bold"),
                       fg=color, bg=PANEL)
        lbl.pack(anchor="w", padx=8, pady=(0, 5))
        stat_labels[key] = lbl

    make_stat(stats_frame, "total",      "TOTAL RESIDENTS", ACCENT)
    make_stat(stats_frame, "registered", "REGISTERED",      SUCCESS)
    make_stat(stats_frame, "pending",    "PENDING",         WARN)
    make_stat(stats_frame, "inactive",   "INACTIVE",        DANGER)
    make_stat(stats_frame, "seniors",    "SENIORS  60+",    ACCENT2)
    make_stat(stats_frame, "male",       "MALE",            "#5b9bff")
    make_stat(stats_frame, "female",     "FEMALE",          "#fc5cbc")

    time_lbl = tk.Label(stats_frame, text="",
                        font=("Courier", 8), fg=MUTED, bg=CARD)
    time_lbl.pack(side="right", padx=16, pady=8)

    def _tick():
        time_lbl.config(
            text="Last updated: " + datetime.now().strftime("Today, %I:%M %p"))
        root.after(60000, _tick)
    _tick()

    sort_info = tk.Label(stats_frame, text="Sorted by: Last Name ↑",
                         font=("Courier", 8), fg=ACCENT, bg=CARD)
    sort_info.pack(side="right", padx=4, pady=8)

    def _status_of(row):
        try: return row[8] if len(row) > 8 else "Registered"
        except: return "Registered"

    def _gender_of(row):
        try: return row[6] if len(row) > 6 else ""
        except: return ""

    def _is_senior(row):
        try: return int(row[3]) >= 60
        except: return False

    def update_stats():
        residents = database.get_residents_by_purok(purok_id)
        stat_labels["total"].config(text=str(len(residents)))
        stat_labels["registered"].config(
            text=str(sum(1 for r in residents if _status_of(r) == "Registered")))
        stat_labels["pending"].config(
            text=str(sum(1 for r in residents if _status_of(r) == "Pending")))
        stat_labels["inactive"].config(
            text=str(sum(1 for r in residents if _status_of(r) == "Inactive")))
        stat_labels["seniors"].config(
            text=str(sum(1 for r in residents if _is_senior(r))))
        stat_labels["male"].config(
            text=str(sum(1 for r in residents if _gender_of(r) == "Male")))
        stat_labels["female"].config(
            text=str(sum(1 for r in residents if _gender_of(r) == "Female")))

    # ── Tab bar ───────────────────────────────────────────────────
    tab_bar = tk.Frame(main, bg=BG)
    tab_bar.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 4))

    active_tab = tk.StringVar(value="All")
    tab_btns   = {}

    def switch_tab(name):
        active_tab.set(name)
        for n, b in tab_btns.items():
            if n == name:
                b.config(bg=ACCENT, fg="white", highlightbackground=ACCENT)
            else:
                b.config(bg=PANEL, fg=MUTED, highlightbackground=BORDER)
        refresh_table()

    for tab_name, tab_key in [("All Residents","All"),("Registered","Registered"),
                               ("Pending","Pending"),("Inactive","Inactive")]:
        b = tk.Button(tab_bar, text=tab_name,
                      font=("Courier", 9, "bold"),
                      bg=PANEL, fg=MUTED,
                      activebackground=ACCENT, activeforeground="white",
                      relief="flat", bd=0, cursor="hand2",
                      highlightthickness=1, highlightbackground=BORDER,
                      command=lambda k=tab_key: switch_tab(k))
        b.pack(side="left", padx=(0, 6), ipady=6, ipadx=14)
        tab_btns[tab_key] = b
    tab_btns["All"].config(bg=ACCENT, fg="white", highlightbackground=ACCENT)

    status_lbl = tk.Label(tab_bar, text="", font=("Courier", 8),
                          fg=SUCCESS, bg=BG)
    status_lbl.pack(side="right", padx=4)

    def status_msg(msg, color=SUCCESS):
        status_lbl.config(text=msg, fg=color)
        root.after(4000, lambda: status_lbl.config(text=""))

    # ── Treeview ──────────────────────────────────────────────────
    tree_frame = tk.Frame(main, bg=CARD,
                          highlightthickness=1, highlightbackground=BORDER)
    tree_frame.grid(row=4, column=0, sticky="nsew", padx=20, pady=(0, 14))
    tree_frame.grid_rowconfigure(0, weight=1)
    tree_frame.grid_columnconfigure(0, weight=1)

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Res.Treeview",
                    background=PANEL, foreground=TEXT,
                    fieldbackground=PANEL, borderwidth=0,
                    font=("Courier", 10), rowheight=36)
    style.configure("Res.Treeview.Heading",
                    background=CARD, foreground=ACCENT,
                    font=("Courier", 9, "bold"),
                    borderwidth=0, relief="flat")
    style.map("Res.Treeview",
              background=[("selected", "#1e2a42")],
              foreground=[("selected", TEXT)])
    style.map("Res.Treeview.Heading",
              background=[("active", PANEL)])

    vsb = tk.Scrollbar(tree_frame, orient="vertical",
                       bg=BORDER, troughcolor=CARD,
                       width=6, relief="flat", highlightthickness=0)
    vsb.grid(row=0, column=1, sticky="ns")

    cols = ("ID", "First Name", "Last Name", "Age",
            "Birthdate", "Gender", "Contact", "Status")
    tree = ttk.Treeview(tree_frame, columns=cols, show="headings",
                        style="Res.Treeview", yscrollcommand=vsb.set)

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
        tree.heading(col, text=col, anchor="center",
                     command=lambda c=col: sort_by(c))
        tree.column(col, width=w, minwidth=w, anchor=anch, stretch=True)

    tree.grid(row=0, column=0, sticky="nsew")
    vsb.config(command=tree.yview)

    tree.tag_configure("odd",        background=PANEL)
    tree.tag_configure("even",       background="#13172a")
    tree.tag_configure("Registered", foreground=SUCCESS)
    tree.tag_configure("Pending",    foreground=PENDING_C)
    tree.tag_configure("Inactive",   foreground=INACTIVE_C)

    # ── Sorting ───────────────────────────────────────────────────
    _sort_state = {"col": None, "rev": False}

    def sort_by(col):
        rows = [(tree.set(iid, col), iid) for iid in tree.get_children()]
        rev  = (_sort_state["col"] == col) and not _sort_state["rev"]
        try:    rows.sort(key=lambda x: int(x[0]), reverse=rev)
        except: rows.sort(key=lambda x: x[0].lower(), reverse=rev)
        for i, (_, iid) in enumerate(rows):
            tree.move(iid, "", i)
            tree.item(iid, tags=(("odd" if i % 2 == 0 else "even"),
                                  tree.item(iid, "tags")[-1]
                                  if tree.item(iid, "tags") else ""))
        _sort_state["col"] = col
        _sort_state["rev"] = rev
        sort_info.config(text=f"Sorted by: {col} {'↑' if not rev else '↓'}")

    # ── Refresh ───────────────────────────────────────────────────
    def refresh_table(query=""):
        for row in tree.get_children():
            tree.delete(row)
        residents = database.get_residents_by_purok(purok_id)
        residents.sort(key=lambda r: r[2].lower())

        tab = active_tab.get()
        if tab != "All":
            residents = [r for r in residents if _status_of(r) == tab]
        if query:
            residents = [r for r in residents
                         if query in " ".join(str(v) for v in r).lower()]

        for i, r in enumerate(residents):
            st  = _status_of(r)
            bd  = r[7] if len(r) > 7 else ""
            gn  = r[6] if len(r) > 6 else ""
            tag_row  = "odd" if i % 2 == 0 else "even"
            tree.insert("", "end",
                        values=(f"{r[0]:03d}", r[1], r[2], r[3],
                                bd, gn, r[4], st),
                        tags=(tag_row, st))

    # ── Form helpers ──────────────────────────────────────────────
    def clear_form():
        for key, e in entries.items():
            if key != "Birthdate":
                if isinstance(e, str):
                    continue
                e.delete(0, tk.END)
        # Reset birthdate to today
        today = date.today()
        calendar_state["selected_date"] = today
        calendar_state["temp_date"] = today
        calendar_state["year"] = today.year
        calendar_state["month"] = today.month
        bd_display.config(text=today.strftime("%Y-%m-%d"))
        entries["Birthdate"] = today.strftime("%Y-%m-%d")
        gender_var.set("Select Gender")
        status_var.set("Registered")
        age_lbl.config(text="Age: —", fg=MUTED)

    def load_selected(event=None):
        sel = tree.selection()
        if not sel: return
        r = tree.item(sel[0])["values"]
        clear_form()
        entries["First Name"].insert(0, r[1])
        entries["Last Name"].insert(0,  r[2])
        
        # Parse and set birthdate in calendar
        if r[4]:
            try:
                bdate = datetime.strptime(r[4], "%Y-%m-%d").date()
                calendar_state["selected_date"] = bdate
                calendar_state["temp_date"] = bdate
                calendar_state["year"] = bdate.year
                calendar_state["month"] = bdate.month
                bd_display.config(text=bdate.strftime("%Y-%m-%d"))
                entries["Birthdate"] = bdate.strftime("%Y-%m-%d")
            except ValueError:
                pass
        
        entries["Contact"].insert(0,    r[6])
        gender_var.set(r[5] if r[5] else "Select Gender")
        status_var.set(r[7] if r[7] else "Registered")
        _calc_age()

    # ── Context menu ──────────────────────────────────────────────
    ctx = tk.Menu(root, tearoff=0, bg=PANEL, fg=TEXT,
                  activebackground=ACCENT, activeforeground="white",
                  font=("Courier", 9), relief="flat", bd=0)
    ctx.add_command(label="✎  Edit",    command=load_selected)
    ctx.add_command(label="✕  Delete",  command=delete_resident)
    ctx.add_separator()
    ctx.add_command(label="＋  Add New", command=clear_form)

    def show_ctx(event):
        iid = tree.identify_row(event.y)
        if iid:
            tree.selection_set(iid)
            ctx.post(event.x_root, event.y_root)

    tree.bind("<Double-1>", load_selected)
    tree.bind("<Button-3>", show_ctx)

    entries["Contact"].bind("<Return>", add_resident)
    root.bind("<Delete>",    delete_resident)
    root.bind("<Control-e>", update_resident)
    root.bind("<Escape>",    lambda e: clear_form())

    refresh_table()
    update_stats()
    root.mainloop()