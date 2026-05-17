import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import database
import csv
import purok


def run_app(purok_id, purok_name):

    # ── Palette ───────────────────────────────────────────────────────────────
    BG      = "#0d0f14"
    CARD    = "#13161e"
    PANEL   = "#1a1e2b"
    BORDER  = "#2a2f42"
    ACCENT  = "#4f8ef7"
    ACCENT2 = "#7c5cfc"
    SUCCESS = "#4fc97e"
    DANGER  = "#f74f6a"
    WARN    = "#f7a94f"
    TEXT    = "#e8ecf4"
    MUTED   = "#6b7490"

    # ── Root ─────────────────────────────────────────────────────────────────
    root = tk.Tk()
    root.title(f"Residents — {purok_name}")
    root.configure(bg=BG)
    root.geometry("1060x660")
    root.minsize(800, 520)
    root.resizable(True, True)

    root.update_idletasks()
    sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
    root.geometry(f"1060x660+{(sw-1060)//2}+{(sh-660)//2}")

    # Root grid: left sidebar | right main
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=1)

    # ═══════════════════════════════════════════════════════════════
    # LEFT SIDEBAR
    # ═══════════════════════════════════════════════════════════════
    sidebar = tk.Frame(root, bg=CARD, width=260,
                       highlightthickness=1, highlightbackground=BORDER)
    sidebar.grid(row=0, column=0, sticky="nsew")
    sidebar.grid_propagate(False)
    sidebar.grid_columnconfigure(0, weight=1)

    # Top accent stripe
    tk.Frame(sidebar, bg=ACCENT, height=3).grid(row=0, column=0, sticky="ew")

    # Brand header
    brand = tk.Frame(sidebar, bg=CARD)
    brand.grid(row=1, column=0, sticky="ew", padx=18, pady=(20, 4))

    dot_c = tk.Canvas(brand, width=24, height=24, bg=CARD, highlightthickness=0)
    dot_c.pack(side="left", padx=(0, 8))
    dot_c.create_oval(0,  0, 10, 10, fill=ACCENT,  outline="")
    dot_c.create_oval(13, 0, 23, 10, fill=ACCENT2, outline="")
    dot_c.create_oval(6, 13, 16, 23, fill=SUCCESS,  outline="")

    hf = tk.Frame(brand, bg=CARD)
    hf.pack(side="left")
    tk.Label(hf, text="Residents", font=("Georgia", 13, "bold"),
             fg=TEXT, bg=CARD).pack(anchor="w")
    tk.Label(hf, text=purok_name,  font=("Courier", 8),
             fg=ACCENT, bg=CARD).pack(anchor="w")

    # Divider
    tk.Frame(sidebar, bg=BORDER, height=1).grid(
        row=2, column=0, sticky="ew", padx=18, pady=(10, 0))

    # ── Form section label ────────────────────────────────────────
    def sidebar_section(row, text):
        f = tk.Frame(sidebar, bg=CARD)
        f.grid(row=row, column=0, sticky="ew", padx=18, pady=(14, 0))
        tk.Label(f, text="▸ " + text,
                 font=("Courier", 7, "bold"),
                 fg=ACCENT, bg=CARD).pack(side="left")
        tk.Frame(f, bg=BORDER, height=1).pack(
            side="left", fill="x", expand=True, padx=(6, 0), pady=5)

    sidebar_section(3, "RESIDENT DETAILS")

    # ── Entry factory ─────────────────────────────────────────────
    entries = {}

    def make_sidebar_entry(grid_row, key, show=None):
        wrap = tk.Frame(sidebar, bg=CARD)
        wrap.grid(row=grid_row, column=0, sticky="ew", padx=18, pady=4)
        wrap.grid_columnconfigure(0, weight=1)

        tk.Label(wrap, text=key,
                 font=("Courier", 8, "bold"),
                 fg=MUTED, bg=CARD).pack(anchor="w")

        inner = tk.Frame(wrap, bg=PANEL,
                         highlightthickness=1, highlightbackground=BORDER)
        inner.pack(fill="x", pady=(2, 0))

        e = tk.Entry(inner, show=show, bg=PANEL, fg=TEXT,
                     font=("Courier", 10), relief="flat",
                     insertbackground=ACCENT, bd=0)
        e.pack(fill="x", padx=8, pady=6)

        def _in(ev):  inner.config(highlightbackground=ACCENT)
        def _out(ev): inner.config(highlightbackground=BORDER)
        e.bind("<FocusIn>",  _in)
        e.bind("<FocusOut>", _out)
        entries[key] = e

    make_sidebar_entry(4, "First Name")
    make_sidebar_entry(5, "Last Name")
    make_sidebar_entry(6, "Age")
    make_sidebar_entry(7, "Contact")

    # ── Action buttons ────────────────────────────────────────────
    sidebar_section(8, "ACTIONS")

    def make_btn(row, label, color, active_color, cmd, fg_color="white"):
        btn = tk.Button(sidebar, text=label, command=cmd,
                        bg=color, fg=fg_color,
                        activebackground=active_color, activeforeground=fg_color,
                        font=("Courier", 9, "bold"),
                        relief="flat", bd=0, cursor="hand2")
        btn.grid(row=row, column=0, sticky="ew",
                 padx=18, pady=3, ipady=8)
        return btn

    def add_resident(event=None):
        fn = entries["First Name"].get().strip()
        ln = entries["Last Name"].get().strip()
        ag = entries["Age"].get().strip()
        ct = entries["Contact"].get().strip()
        if not all([fn, ln, ag, ct]):
            messagebox.showwarning("Missing Fields", "All fields are required.")
            return
        database.add_resident(fn, ln, ag, ct, purok_id)
        clear_form()
        refresh_table()
        status_msg("Resident added successfully.", SUCCESS)

    def update_resident(event=None):
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Select a resident to update.")
            return
        rid = tree.item(sel[0])["values"][0]
        fn = entries["First Name"].get().strip()
        ln = entries["Last Name"].get().strip()
        ag = entries["Age"].get().strip()
        ct = entries["Contact"].get().strip()
        if not all([fn, ln, ag, ct]):
            messagebox.showwarning("Missing Fields", "All fields are required.")
            return
        database.update_resident(rid, fn, ln, ag, ct)
        clear_form()
        refresh_table()
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
            clear_form()
            refresh_table()
            status_msg(f"Deleted: {name}", DANGER)

    def go_back():
        root.destroy()
        purok.run_purok_window()

    make_btn(9,  "＋  Add Resident",    ACCENT,   "#3a7ce8", add_resident)
    make_btn(10, "✎  Update Selected", WARN,     "#d9903a", update_resident, "#0d0f14")
    make_btn(11, "✕  Delete Selected", DANGER,   "#d93a52", delete_resident)

    tk.Frame(sidebar, bg=BORDER, height=1).grid(
        row=12, column=0, sticky="ew", padx=18, pady=(12, 0))

    make_btn(13, "← Back to Puroks", PANEL, BORDER, go_back, MUTED)

    # Spacer
    sidebar.grid_rowconfigure(14, weight=1)

    # Footer
    tk.Label(sidebar, text="© BRGY System  v1.0",
             font=("Courier", 7), fg=BORDER, bg=CARD).grid(
                 row=15, column=0, pady=(0, 10))

    # ═══════════════════════════════════════════════════════════════
    # RIGHT MAIN PANEL
    # ═══════════════════════════════════════════════════════════════
    main = tk.Frame(root, bg=BG)
    main.grid(row=0, column=1, sticky="nsew")
    main.grid_rowconfigure(3, weight=1)   # treeview row expands
    main.grid_columnconfigure(0, weight=1)

    # Top accent stripe
    tk.Frame(main, bg=ACCENT2, height=3).grid(row=0, column=0, sticky="ew")

    # ── Toolbar row ───────────────────────────────────────────────
    toolbar = tk.Frame(main, bg=BG)
    toolbar.grid(row=1, column=0, sticky="ew", padx=20, pady=(14, 8))
    toolbar.grid_columnconfigure(1, weight=1)

    # Title
    tf = tk.Frame(toolbar, bg=BG)
    tf.grid(row=0, column=0, sticky="w")
    tk.Label(tf, text="Resident", font=("Georgia", 18, "bold"),
             fg=TEXT, bg=BG).pack(side="left")
    tk.Label(tf, text=" Registry", font=("Georgia", 18, "italic"),
             fg=ACCENT, bg=BG).pack(side="left")

    # Right-side toolbar buttons
    tools = tk.Frame(toolbar, bg=BG)
    tools.grid(row=0, column=2, sticky="e")

    def make_tool_btn(parent, text, color, cmd):
        b = tk.Button(parent, text=text, command=cmd,
                      bg=PANEL, fg=color,
                      activebackground=BORDER, activeforeground=color,
                      font=("Courier", 8, "bold"),
                      relief="flat", bd=0, cursor="hand2",
                      highlightthickness=1, highlightbackground=BORDER)
        b.pack(side="left", padx=3, ipady=5, ipadx=10)
        return b

    # ── Search bar ────────────────────────────────────────────────
    search_wrap = tk.Frame(toolbar, bg=PANEL,
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

    def _search_focus_in(e):
        if search_entry.get() == "Search residents...":
            search_entry.delete(0, tk.END)
        search_wrap.config(highlightbackground=ACCENT)
    def _search_focus_out(e):
        if not search_entry.get():
            search_entry.insert(0, "Search residents...")
        search_wrap.config(highlightbackground=BORDER)

    search_entry.bind("<FocusIn>",  _search_focus_in)
    search_entry.bind("<FocusOut>", _search_focus_out)

    def _on_search(*args):
        q = search_var.get().lower().strip()
        if q == "search residents...":
            q = ""
        refresh_table(query=q)
    search_var.trace_add("write", _on_search)

    # Export / Import buttons
    def export_csv():
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Export Residents"
        )
        if not path:
            return
        residents = database.get_residents_by_purok(purok_id)
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "First Name", "Last Name", "Age", "Contact"])
            writer.writerows(residents)
        status_msg(f"Exported {len(residents)} records.", SUCCESS)

    def import_csv():
        path = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv")],
            title="Import Residents"
        )
        if not path:
            return
        added = 0
        skipped = 0
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    database.add_resident(
                        row["First Name"].strip(),
                        row["Last Name"].strip(),
                        row["Age"].strip(),
                        row["Contact"].strip(),
                        purok_id
                    )
                    added += 1
                except Exception:
                    skipped += 1
        refresh_table()
        status_msg(f"Imported {added} records. ({skipped} skipped)", WARN)

    make_tool_btn(tools, "⬆  Export CSV", SUCCESS, export_csv)
    make_tool_btn(tools, "⬇  Import CSV", ACCENT,  import_csv)

    # ── Stats strip ───────────────────────────────────────────────
    stats_bar = tk.Frame(main, bg=CARD,
                         highlightthickness=1, highlightbackground=BORDER)
    stats_bar.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 8))
    # (populated after table)

    count_lbl  = tk.Label(stats_bar, text="",
                          font=("Courier", 8), fg=MUTED, bg=CARD)
    count_lbl.pack(side="left", padx=14, pady=5)

    status_lbl = tk.Label(stats_bar, text="",
                          font=("Courier", 8), fg=SUCCESS, bg=CARD)
    status_lbl.pack(side="right", padx=14, pady=5)

    def status_msg(msg, color=SUCCESS):
        status_lbl.config(text=msg, fg=color)
        root.after(4000, lambda: status_lbl.config(text=""))

    # ── Treeview ──────────────────────────────────────────────────
    tree_frame = tk.Frame(main, bg=CARD,
                          highlightthickness=1, highlightbackground=BORDER)
    tree_frame.grid(row=3, column=0, sticky="nsew", padx=20, pady=(0, 14))
    tree_frame.grid_rowconfigure(0, weight=1)
    tree_frame.grid_columnconfigure(0, weight=1)

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Res.Treeview",
                    background=PANEL,
                    foreground=TEXT,
                    fieldbackground=PANEL,
                    borderwidth=0,
                    font=("Courier", 10),
                    rowheight=32)
    style.configure("Res.Treeview.Heading",
                    background=CARD,
                    foreground=ACCENT,
                    font=("Courier", 9, "bold"),
                    borderwidth=0, relief="flat")
    style.map("Res.Treeview",
              background=[("selected", ACCENT)],
              foreground=[("selected", "white")])
    style.map("Res.Treeview.Heading",
              background=[("active", PANEL)])

    vsb = tk.Scrollbar(tree_frame, orient="vertical",
                       bg=BORDER, troughcolor=CARD,
                       width=6, relief="flat", highlightthickness=0)
    vsb.grid(row=0, column=1, sticky="ns")

    hsb = tk.Scrollbar(tree_frame, orient="horizontal",
                       bg=BORDER, troughcolor=CARD,
                       width=6, relief="flat", highlightthickness=0)
    hsb.grid(row=1, column=0, sticky="ew")

    cols = ("ID", "First Name", "Last Name", "Age", "Contact")
    tree = ttk.Treeview(tree_frame, columns=cols, show="headings",
                        style="Res.Treeview",
                        yscrollcommand=vsb.set,
                        xscrollcommand=hsb.set)

    col_widths = {"ID": 50, "First Name": 160, "Last Name": 160,
                  "Age": 60, "Contact": 140}
    col_anchor = {"ID": "center", "Age": "center"}
    for col in cols:
        tree.heading(col, text=col,
                     command=lambda c=col: sort_by(c))
        tree.column(col,
                    width=col_widths.get(col, 130),
                    anchor=col_anchor.get(col, "w"),
                    stretch=(col == "Contact"))

    tree.grid(row=0, column=0, sticky="nsew")
    vsb.config(command=tree.yview)
    hsb.config(command=tree.xview)

    tree.tag_configure("odd",  background=PANEL)
    tree.tag_configure("even", background="#161a26")

    # ── Sorting ───────────────────────────────────────────────────
    _sort_state = {"col": None, "rev": False}

    def sort_by(col):
        rows = [(tree.set(iid, col), iid) for iid in tree.get_children()]
        rev  = (_sort_state["col"] == col) and not _sort_state["rev"]
        try:
            rows.sort(key=lambda x: int(x[0]), reverse=rev)
        except ValueError:
            rows.sort(key=lambda x: x[0].lower(), reverse=rev)
        for i, (_, iid) in enumerate(rows):
            tree.move(iid, "", i)
            tree.item(iid, tags=("odd" if i % 2 == 0 else "even",))
        _sort_state["col"] = col
        _sort_state["rev"] = rev

    # ── Refresh ───────────────────────────────────────────────────
    def refresh_table(query=""):
        for row in tree.get_children():
            tree.delete(row)
        residents = database.get_residents_by_purok(purok_id)
        residents.sort(key=lambda r: r[2].lower())
        if query:
            residents = [r for r in residents
                         if query in " ".join(str(v) for v in r).lower()]
        for i, r in enumerate(residents):
            tag = "odd" if i % 2 == 0 else "even"
            tree.insert("", "end", values=r, tags=(tag,))
        count_lbl.config(
            text=f"{len(residents)} resident{'s' if len(residents) != 1 else ''}"
        )

    # ── Form helpers ──────────────────────────────────────────────
    def clear_form():
        for e in entries.values():
            e.delete(0, tk.END)

    def load_selected(event=None):
        sel = tree.selection()
        if not sel:
            return
        r = tree.item(sel[0])["values"]
        clear_form()
        for key, val in zip(("First Name", "Last Name", "Age", "Contact"),
                            (r[1], r[2], r[3], r[4])):
            entries[key].insert(0, val)

    # ── Context menu ──────────────────────────────────────────────
    ctx = tk.Menu(root, tearoff=0,
                  bg=PANEL, fg=TEXT,
                  activebackground=ACCENT, activeforeground="white",
                  font=("Courier", 9), relief="flat", bd=0)
    ctx.add_command(label="✎  Edit",   command=lambda: (load_selected(), None))
    ctx.add_command(label="✕  Delete", command=delete_resident)
    ctx.add_separator()
    ctx.add_command(label="＋  Add New", command=lambda: clear_form())

    def show_ctx(event):
        iid = tree.identify_row(event.y)
        if iid:
            tree.selection_set(iid)
            ctx.post(event.x_root, event.y_root)

    tree.bind("<Double-1>",  load_selected)
    tree.bind("<Button-3>",  show_ctx)

    # ── Keyboard shortcuts ────────────────────────────────────────
    entries["Contact"].bind("<Return>", add_resident)
    root.bind("<Delete>",    delete_resident)
    root.bind("<Control-e>", update_resident)
    root.bind("<Escape>",    lambda e: clear_form())

    refresh_table()
    root.mainloop()