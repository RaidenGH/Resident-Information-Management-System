import tkinter as tk
from tkinter import ttk, messagebox
import database
import ui


def run_purok_window():
    database.create_purok_table()

    # ── Palette (matches system theme) ───────────────────────────────────────
    BG      = "#0d0f14"
    CARD    = "#13161e"
    PANEL   = "#1a1e2b"
    BORDER  = "#2a2f42"
    ACCENT  = "#4f8ef7"
    ACCENT2 = "#7c5cfc"
    SUCCESS = "#4fc97e"
    TEXT    = "#e8ecf4"
    MUTED   = "#6b7490"
    HOVER   = "#1f2538"

    # ── Root window ──────────────────────────────────────────────────────────
    root = tk.Tk()
    root.title("Purok Management")
    root.configure(bg=BG)
    root.geometry("560x620")
    root.minsize(460, 500)
    root.resizable(True, True)

    root.update_idletasks()
    x = (root.winfo_screenwidth()  - 560) // 2
    y = (root.winfo_screenheight() - 620) // 2
    root.geometry(f"560x620+{x}+{y}")

    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    # ── Outer wrapper fills window ────────────────────────────────────────────
    wrapper = tk.Frame(root, bg=BG)
    wrapper.grid(row=0, column=0, sticky="nsew")
    wrapper.grid_rowconfigure(2, weight=1)   # table row expands
    wrapper.grid_columnconfigure(0, weight=1)

    # ── Top accent stripe ─────────────────────────────────────────────────────
    tk.Frame(wrapper, bg=ACCENT, height=3).grid(
        row=0, column=0, sticky="ew")

    # ── Header ───────────────────────────────────────────────────────────────
    header = tk.Frame(wrapper, bg=BG)
    header.grid(row=1, column=0, sticky="ew", padx=26, pady=(22, 10))
    header.grid_columnconfigure(1, weight=1)

    # Dot cluster brand mark
    dot_c = tk.Canvas(header, width=28, height=28, bg=BG, highlightthickness=0)
    dot_c.grid(row=0, column=0, rowspan=2, padx=(0, 12))
    dot_c.create_oval(0,  0, 12, 12, fill=ACCENT,  outline="")
    dot_c.create_oval(15, 0, 27, 12, fill=ACCENT2, outline="")
    dot_c.create_oval(7, 15, 19, 27, fill=SUCCESS,  outline="")

    title_f = tk.Frame(header, bg=BG)
    title_f.grid(row=0, column=1, sticky="w")
    tk.Label(title_f, text="Purok",
             font=("Georgia", 22, "bold"),
             fg=TEXT, bg=BG).pack(side="left")
    tk.Label(title_f, text=" Management",
             font=("Georgia", 22, "italic"),
             fg=ACCENT, bg=BG).pack(side="left")

    tk.Label(header,
             text="Select a purok to view its residents",
             font=("Courier", 8),
             fg=MUTED, bg=BG).grid(row=1, column=1, sticky="w")

    # ── Treeview card ─────────────────────────────────────────────────────────
    tree_card = tk.Frame(wrapper, bg=CARD,
                         highlightthickness=1, highlightbackground=BORDER)
    tree_card.grid(row=2, column=0, sticky="nsew", padx=26, pady=(0, 10))
    tree_card.grid_rowconfigure(1, weight=1)
    tree_card.grid_columnconfigure(0, weight=1)

    # Card header row
    card_hdr = tk.Frame(tree_card, bg=CARD)
    card_hdr.grid(row=0, column=0, columnspan=2, sticky="ew",
                  padx=16, pady=(12, 6))
    card_hdr.grid_columnconfigure(1, weight=1)

    tk.Label(card_hdr, text="▸ PUROK LIST",
             font=("Courier", 8, "bold"),
             fg=ACCENT, bg=CARD).grid(row=0, column=0, sticky="w")

    count_lbl = tk.Label(card_hdr, text="0 entries",
                         font=("Courier", 8),
                         fg=MUTED, bg=CARD)
    count_lbl.grid(row=0, column=1, sticky="e")

    # ttk style
    style = ttk.Style()
    style.theme_use("clam")

    style.configure("Custom.Treeview",
                    background=PANEL,
                    foreground=TEXT,
                    fieldbackground=PANEL,
                    borderwidth=0,
                    font=("Courier", 10),
                    rowheight=34)
    style.configure("Custom.Treeview.Heading",
                    background=CARD,
                    foreground=ACCENT,
                    font=("Courier", 9, "bold"),
                    borderwidth=0,
                    relief="flat")
    style.map("Custom.Treeview",
              background=[("selected", ACCENT)],
              foreground=[("selected", "white")])
    style.map("Custom.Treeview.Heading",
              background=[("active", PANEL)])

    # Scrollbar
    tree_scroll = tk.Scrollbar(tree_card, orient="vertical",
                               bg=BORDER, troughcolor=CARD,
                               width=6, relief="flat",
                               highlightthickness=0)
    tree_scroll.grid(row=1, column=1, sticky="ns", pady=(0, 10))

    tree = ttk.Treeview(tree_card,
                        columns=("ID", "Name"),
                        show="headings",
                        style="Custom.Treeview",
                        yscrollcommand=tree_scroll.set)
    tree.heading("ID",   text="ID")
    tree.heading("Name", text="Purok Name")
    tree.column("ID",   width=55,  anchor="center", stretch=False)
    tree.column("Name", width=300, anchor="w",      stretch=True)
    tree.grid(row=1, column=0, sticky="nsew", padx=(10, 0), pady=(0, 10))
    tree_scroll.config(command=tree.yview)

    # Alternating row tags
    tree.tag_configure("odd",  background=PANEL)
    tree.tag_configure("even", background="#161a26")

    # ── Add Purok card ────────────────────────────────────────────────────────
    add_card = tk.Frame(wrapper, bg=CARD,
                        highlightthickness=1, highlightbackground=BORDER)
    add_card.grid(row=3, column=0, sticky="ew", padx=26, pady=(0, 10))
    add_card.grid_columnconfigure(0, weight=1)

    tk.Label(add_card, text="▸ ADD NEW PUROK",
             font=("Courier", 8, "bold"),
             fg=ACCENT, bg=CARD).grid(
                 row=0, column=0, columnspan=2,
                 sticky="w", padx=16, pady=(12, 6))

    # Input + button row
    input_row = tk.Frame(add_card, bg=CARD)
    input_row.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 14))
    input_row.grid_columnconfigure(0, weight=1)

    entry_wrap = tk.Frame(input_row, bg=PANEL,
                          highlightthickness=1, highlightbackground=BORDER)
    entry_wrap.grid(row=0, column=0, sticky="ew", padx=(0, 8))

    purok_entry = tk.Entry(entry_wrap,
                           bg=PANEL, fg=TEXT,
                           font=("Courier", 10),
                           relief="flat",
                           insertbackground=ACCENT, bd=0)
    purok_entry.pack(fill="x", padx=10, pady=7)

    def _entry_focus_in(e):
        entry_wrap.config(highlightbackground=ACCENT)
    def _entry_focus_out(e):
        entry_wrap.config(highlightbackground=BORDER)
    purok_entry.bind("<FocusIn>",  _entry_focus_in)
    purok_entry.bind("<FocusOut>", _entry_focus_out)

    add_btn = tk.Button(input_row, text="+ Add",
                        font=("Courier", 9, "bold"),
                        bg=ACCENT, fg="white",
                        activebackground="#3a7ce8",
                        activeforeground="white",
                        relief="flat", bd=0, cursor="hand2")
    add_btn.grid(row=0, column=1, ipady=7, ipadx=14)

    # ── Open Residents button ─────────────────────────────────────────────────
    open_btn = tk.Button(wrapper,
                         text="OPEN RESIDENTS  →",
                         font=("Courier", 10, "bold"),
                         bg=SUCCESS, fg="#0d0f14",
                         activebackground="#3ab868",
                         activeforeground="#0d0f14",
                         relief="flat", bd=0, cursor="hand2")
    open_btn.grid(row=4, column=0, sticky="ew",
                  padx=26, pady=(0, 6), ipady=11)

    # Footer
    tk.Label(wrapper,
             text="© Barangay Management System  ·  v1.0",
             font=("Courier", 7),
             fg=BORDER, bg=BG).grid(row=5, column=0, pady=(2, 10))

    # ── Logic ─────────────────────────────────────────────────────────────────
    def refresh_puroks():
        for row in tree.get_children():
            tree.delete(row)
        puroks = database.get_puroks()
        for i, purok in enumerate(puroks):
            tag = "odd" if i % 2 == 0 else "even"
            tree.insert("", "end", values=purok, tags=(tag,))
        count_lbl.config(text=f"{len(puroks)} entr{'y' if len(puroks)==1 else 'ies'}")

    def add_purok(event=None):
        name = purok_entry.get().strip()
        if not name:
            messagebox.showwarning("Missing Name", "Please enter a Purok name.")
            return
        database.add_purok(name)
        purok_entry.delete(0, tk.END)
        refresh_puroks()

    def open_residents(event=None):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a Purok first.")
            return
        purok_id   = tree.item(selected[0])["values"][0]
        purok_name = tree.item(selected[0])["values"][1]
        root.destroy()
        ui.run_app(purok_id, purok_name)

    add_btn.config(command=add_purok)
    open_btn.config(command=open_residents)
    purok_entry.bind("<Return>", add_purok)
    tree.bind("<Return>", open_residents)
    tree.bind("<Double-1>", open_residents)   # double-click also opens

    refresh_puroks()
    root.mainloop()