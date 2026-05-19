import tkinter as tk
from tkinter import ttk, messagebox
import database
import ui
from logo import make_logo_canvas


# ── Philippine Location Data (Davao Region focus + major regions) ─────────────
PH_LOCATIONS = {
    "Davao Region (XI)": {
        "Davao City": [
            "Agdao", "Alambre", "Alejandra Navarro", "Alfonso Angliongto Sr.",
            "Angalan", "Atan-Awe", "Baganihan", "Bago Aplaya", "Bago Gallera",
            "Bago Oshiro", "Baguio", "Balengaeng", "Baliok", "Bangkas Heights",
            "Bantol", "Baracatan", "Barangay 1-A", "Barangay 2-A", "Barangay 3-A",
            "Barangay 4-A", "Barangay 5-A", "Barangay 6-A", "Barangay 7-A",
            "Barangay 8-A", "Barangay 9-A", "Barangay 10-A", "Barangay 11-B",
            "Barangay 12-B", "Barangay 13-B", "Barangay 14-B", "Barangay 15-B",
            "Barangay 16-B", "Barangay 17-B", "Barangay 18-B", "Barangay 19-B",
            "Barangay 20-B", "Barangay 21-C", "Barangay 22-C", "Barangay 23-C",
            "Barangay 24-C", "Barangay 25-C", "Barangay 26-C", "Barangay 27-C",
            "Barangay 28-C", "Barangay 29-C", "Barangay 30-C", "Barangay 31-D",
            "Barangay 32-D", "Barangay 33-D", "Barangay 34-D", "Barangay 35-D",
            "Barangay 36-D", "Barangay 37-D", "Barangay 38-D", "Barangay 39-D",
            "Barangay 40-D", "Buhangin", "Bunawan", "Cabantian", "Calinan",
            "Callawa", "Catalunan Grande", "Catalunan Pequeño", "Communal",
            "Crossing Bayabas", "Dacudao", "Dalag", "Daliaon Plantation",
            "Damascus", "Dumoy", "Eden", "Fatima", "Gatungan", "Gov. Paciano Bangoy",
            "Gov. Vicente Duterte", "Gumalang", "Indangan", "Kilate", "Lacson",
            "Lamanan", "Langub", "Lapu-lapu", "Leon Garcia Sr.", "Lizada",
            "Los Amigos", "Lubogan", "Lumiad", "Ma-a", "Mabuhay", "Malagos",
            "Malamba", "Manambulan", "Mandug", "Manuel Guianga", "Mapula",
            "Marapangi", "Marilog", "Matina Aplaya", "Matina Crossing",
            "Matina Pangi", "Megkawayan", "Mintal", "Mudiang", "Mulig",
            "New Carmen", "New Valencia", "Pampanga", "Panacan", "Pañabo",
            "Paradise Embak", "Riverside", "Salapawan", "Saliducon", "Samo-Samo",
            "San Antonio", "Santo Niño", "Sasa", "Sirib", "Sirawan", "Sirib",
            "Tacunan", "Tagakpan", "Tagluno", "Tagurano", "Talomo",
            "Talomonan", "Tamayong", "Tamugan", "Tapak", "Tawan-tawan",
            "Tibuloy", "Tibungco", "Tigatto", "Toril", "Tugbok", "Tungkalan",
            "Ubalde", "Ula", "Waan", "Wilfredo Aquino", "Wines",
        ],
        "Tagum City": [
            "Apokon", "Bincungan", "Busaon", "Canocotan", "Cuambogan",
            "La Filipina", "Liboganon", "Madaum", "Magdum", "Magugpo East",
            "Magugpo North", "Magugpo Poblacion", "Magugpo South", "Magugpo West",
            "Mankilam", "New Balamban", "Nueva Fuerza", "Pagsabangan",
            "Pandapan", "San Agustin", "San Isidro", "San Miguel", "Visayan Village",
        ],
        "Panabo City": [
            "A.O. Floirendo", "Buenavista", "Cacao", "Cagangohan", "Consolacion",
            "Dapco", "Gredu", "J.P. Laurel", "Katipunan", "Kasilak",
            "Langkilaan", "Lasang", "Mabunao", "Maduao", "Malativas",
            "Manay", "Nanyo", "New Malaga", "New Panaon", "New Santiago",
            "Quezon", "Salvacion", "San Francisco", "San Nicolas", "San Pedro",
            "San Roque", "San Vicente", "Santo Niño", "Sindaton", "Southern Davao",
            "Tibungol", "Upper Licanan", "Waterfall",
        ],
        "Digos City": [
            "Aplaya", "Balabag", "Binaton", "Cogon", "Colorado", "Dawis",
            "Dulangan", "Goma", "Igpit", "Kapatagan", "Kiagot", "Lungag",
            "Mahayahay", "Matti", "Ruparan", "San Agustin", "San Jose",
            "San Miguel", "San Roque", "Sinawilan", "Soong", "Tiguman",
            "Tres de Mayo", "Zone 1", "Zone 2", "Zone 3",
        ],
        "Mati City": [
            "Badas", "Bobon", "Buso", "Cabuaya", "Central", "Don Enrique Lopez",
            "Don Martin Marundan", "Don Salvador Lopez Sr.", "Dawan", "Macambol",
            "Magsaysay", "Matiao", "Mayo", "Sainz", "Sanghay", "Tagabakid",
            "Tagbinonga", "Taguibo", "Tamisan",
        ],
    },
    "Metro Manila (NCR)": {
        "Manila": ["Binondo", "Ermita", "Intramuros", "Malate", "Paco",
                   "Pandacan", "Port Area", "Quiapo", "Sampaloc", "San Andres",
                   "San Miguel", "San Nicolas", "Santa Ana", "Santa Cruz",
                   "Santa Mesa", "Tondo"],
        "Quezon City": ["Alicia", "Bagong Buhay", "Bagong Pag-asa", "Bagong Silangan",
                        "Batasan Hills", "Commonwealth", "Cubao", "Diliman",
                        "Fairview", "Novaliches", "Payatas", "Project 4", "Project 6"],
        "Makati": ["Bel-Air", "Cembo", "Comembo", "Dasmarinas Village", "Forbes Park",
                   "Guadalupe Nuevo", "Guadalupe Viejo", "Legazpi Village",
                   "Olympia", "Palanan", "Pembo", "Pinagkaisahan", "Poblacion",
                   "Rockwell", "Salcedo Village", "San Lorenzo", "San Antonio"],
        "Pasig": ["Bagong Ilog", "Bagong Katipunan", "Bambang", "Buting",
                  "Caniogan", "Dela Paz", "Kapitolyo", "Malinao", "Manggahan",
                  "Maybunga", "Ortigas Center", "Pineda", "Rosario", "Sagad",
                  "San Antonio", "San Joaquin", "San Nicolas", "Santa Cruz",
                  "Santa Rosa", "Santo Tomas", "Ugong"],
    },
    "Central Visayas (VII)": {
        "Cebu City": ["Adlaon", "Agsungot", "Apas", "Babag", "Bacayan",
                      "Banilad", "Basak Pardo", "Basak San Nicolas", "Binaliw",
                      "Bonbon", "Budlaan", "Buhisan", "Bulacao", "Buot-Taup",
                      "Busay", "Calamba", "Cambinocot", "Capitol Site", "Carreta",
                      "Central", "Cogon Pardo", "Cogon Ramos", "Day-as", "Duljo",
                      "Ermita", "Guadalupe", "Guba", "Hippodromo", "Inayawan",
                      "Kalubihan", "Kamundanan", "Kasambagan", "Kinasang-an",
                      "Labangon", "Lahug", "Lorega", "Lusaran", "Luz", "Mabini",
                      "Mabolo", "Malubog", "Mambaling", "Pahina Central",
                      "Pahina San Nicolas", "Pamutan", "Pardo", "Pari-an",
                      "Paril", "Pasil", "Pit-os", "Poblacion Pardo", "Pulangbato",
                      "Pung-ol-Sibugay", "Punta Princesa", "Quiot Pardo",
                      "Sambag I", "Sambag II", "San Antonio", "San Jose",
                      "San Nicolas Central", "San Roque", "Santa Cruz",
                      "Santo Niño", "Sapangdaku", "Sawang Calero", "Sinsin",
                      "Sirao", "Sudlon I", "Sudlon II", "T. Padilla", "Tabunan",
                      "Tagba-o", "Talamban", "Taptap", "Tejero", "Tinago",
                      "Tisa", "To-ong Pardo", "Toong", "Zapatera"],
        "Lapu-Lapu City": ["Agus", "Babag", "Bankal", "Baring", "Basak",
                           "Buaya", "Calawisan", "Canjulao", "Caubian", "Caw-oy",
                           "Cawhagan", "Gun-ob", "Ibo", "Looc", "Mactan", "Maribago",
                           "Marigondon", "Pajo", "Pajod", "Pilipog", "Poblacion",
                           "Punta Engaño", "Pusok", "Subabasbas", "Talima",
                           "Tingo", "Tungasan"],
    },
    "Northern Mindanao (X)": {
        "Cagayan de Oro": ["Agusan", "Balubal", "Barangay 1", "Barangay 2",
                           "Barangay 3", "Barangay 4", "Barangay 5", "Barangay 6",
                           "Barangay 7", "Barangay 8", "Barangay 9", "Barangay 10",
                           "Barangay 11", "Barangay 12", "Barangay 13", "Barangay 14",
                           "Barangay 15", "Barangay 16", "Barangay 17", "Barangay 18",
                           "Barangay 19", "Barangay 20", "Barangay 21", "Barangay 22",
                           "Barangay 23", "Barangay 24", "Barangay 25", "Bayabas",
                           "Bonbon", "Bulua", "Camaman-an", "Canitoan", "Carmen",
                           "Consolacion", "Cugman", "Dansolihon", "F.S. Catanico",
                           "Gusa", "Indahag", "Iponan", "Kauswagan", "Lapasan",
                           "Lumbia", "Macabalan", "Macasandig", "Mambuaya",
                           "Nazareth", "Pagalungan", "Pagatpat", "Patrocinio",
                           "Pigsag-an", "Puerto", "Puntod", "San Simon", "Tablon",
                           "Taglimao", "Tagpangi", "Tignapoloan", "Tuburan", "Tumpagon"],
        "Iligan City": ["Abuno", "Acmac", "Bagong Silang", "Bonbonon", "Bunawan",
                        "Buru-un", "Dalipuga", "Del Carmen", "Digkilaan", "Dulag",
                        "Hinaplanon", "Hindang", "Kabacsanan", "Kalilangan",
                        "Kiwalan", "Lanipao", "Luinab", "Mahayahay", "Mainit",
                        "Mandulog", "Maria Cristina", "Pala-o", "Panoroganan",
                        "Poblacion", "Puga-an", "Rogongon", "San Miguel",
                        "San Roque", "Santa Elena", "Santa Filomena", "Santiago",
                        "Santo Rosario", "Saray", "Suarez", "Tambacan",
                        "Tibanga", "Tipanoy", "Tominobo Proper", "Tominobo Upper",
                        "Tubod", "Ubaldo Laya", "Upper Hinaplanon", "Villa Verde"],
    },
}


def run_purok_window():
    database.create_purok_table()

    # ── Palette ───────────────────────────────────────────────────────────────
    BG      = "#0d0f14"
    CARD    = "#13161e"
    PANEL   = "#1a1e2b"
    BORDER  = "#2a2f42"
    ACCENT  = "#4f8ef7"
    ACCENT2 = "#7c5cfc"
    SUCCESS = "#4fc97e"
    WARNING = "#f7c948"
    DANGER  = "#ff5f5f"
    TEXT    = "#e8ecf4"
    MUTED   = "#6b7490"

    # ── Root window ───────────────────────────────────────────────────────────
    root = tk.Tk()
    root.title("Purok Management")
    root.configure(bg=BG)
    root.geometry("660x860")
    root.minsize(560, 700)
    root.resizable(True, True)

    root.update_idletasks()
    x = (root.winfo_screenwidth()  - 660) // 2
    y = (root.winfo_screenheight() - 860) // 2
    root.geometry(f"660x860+{x}+{y}")

    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    # ── Outer wrapper ─────────────────────────────────────────────────────────
    wrapper = tk.Frame(root, bg=BG)
    wrapper.grid(row=0, column=0, sticky="nsew")
    wrapper.grid_rowconfigure(4, weight=1)   # treeview row expands
    wrapper.grid_columnconfigure(0, weight=1)

    # Top accent stripe
    tk.Frame(wrapper, bg=ACCENT, height=3).grid(row=0, column=0, sticky="ew")

    # Logo
    logo_canvas = make_logo_canvas(wrapper, scale=0.75, bg=BG)
    logo_canvas.grid(row=1, column=0, sticky="w", padx=26, pady=(16, 0))

    # Separator
    tk.Frame(wrapper, bg=BORDER, height=1).grid(
        row=2, column=0, sticky="ew", padx=26, pady=(12, 0))

    # ── Header ────────────────────────────────────────────────────────────────
    header = tk.Frame(wrapper, bg=BG)
    header.grid(row=3, column=0, sticky="ew", padx=26, pady=(16, 10))
    header.grid_columnconfigure(1, weight=1)

    dot_c = tk.Canvas(header, width=28, height=28, bg=BG, highlightthickness=0)
    dot_c.grid(row=0, column=0, rowspan=2, padx=(0, 12))
    dot_c.create_oval(0,  0, 12, 12, fill=ACCENT,  outline="")
    dot_c.create_oval(15, 0, 27, 12, fill=ACCENT2, outline="")
    dot_c.create_oval(7, 15, 19, 27, fill=SUCCESS,  outline="")

    title_f = tk.Frame(header, bg=BG)
    title_f.grid(row=0, column=1, sticky="w")
    tk.Label(title_f, text="Purok",
             font=("Georgia", 22, "bold"), fg=TEXT, bg=BG).pack(side="left")
    tk.Label(title_f, text=" Management",
             font=("Georgia", 22, "italic"), fg=ACCENT, bg=BG).pack(side="left")
    tk.Label(header,
             text="Select a purok to view its residents",
             font=("Courier", 8), fg=MUTED, bg=BG).grid(row=1, column=1, sticky="w")

    # ── Treeview card ─────────────────────────────────────────────────────────
    tree_card = tk.Frame(wrapper, bg=CARD,
                         highlightthickness=1, highlightbackground=BORDER)
    tree_card.grid(row=4, column=0, sticky="nsew", padx=26, pady=(0, 10))
    tree_card.grid_rowconfigure(1, weight=1)
    tree_card.grid_columnconfigure(0, weight=1)

    card_hdr = tk.Frame(tree_card, bg=CARD)
    card_hdr.grid(row=0, column=0, columnspan=2, sticky="ew", padx=16, pady=(12, 6))
    card_hdr.grid_columnconfigure(1, weight=1)

    tk.Label(card_hdr, text="▸ PUROK LIST",
             font=("Courier", 8, "bold"), fg=ACCENT, bg=CARD).grid(
                 row=0, column=0, sticky="w")
    count_lbl = tk.Label(card_hdr, text="0 entries",
                         font=("Courier", 8), fg=MUTED, bg=CARD)
    count_lbl.grid(row=0, column=1, sticky="e")

    # ttk style
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Custom.Treeview",
                    background=PANEL, foreground=TEXT, fieldbackground=PANEL,
                    borderwidth=0, font=("Courier", 10), rowheight=34)
    style.configure("Custom.Treeview.Heading",
                    background=CARD, foreground=ACCENT,
                    font=("Courier", 9, "bold"), borderwidth=0, relief="flat")
    style.map("Custom.Treeview",
              background=[("selected", ACCENT)], foreground=[("selected", "white")])
    style.map("Custom.Treeview.Heading", background=[("active", PANEL)])

    style.configure("Loc.TCombobox",
                    fieldbackground=PANEL, background=PANEL,
                    foreground=TEXT, selectbackground=ACCENT,
                    selectforeground="white", bordercolor=BORDER,
                    arrowcolor=ACCENT, relief="flat")
    style.map("Loc.TCombobox",
              fieldbackground=[("readonly", PANEL)],
              foreground=[("readonly", TEXT)],
              bordercolor=[("focus", ACCENT)])

    # Scrollbar + Treeview
    tree_scroll = tk.Scrollbar(tree_card, orient="vertical",
                               bg=BORDER, troughcolor=CARD,
                               width=6, relief="flat", highlightthickness=0)
    tree_scroll.grid(row=1, column=1, sticky="ns", pady=(0, 10))

    tree = ttk.Treeview(tree_card,
                        columns=("ID", "Name", "Region", "City", "Barangay"),
                        show="headings",
                        style="Custom.Treeview",
                        yscrollcommand=tree_scroll.set)
    tree.heading("ID",        text="ID")
    tree.heading("Name",      text="Purok Name")
    tree.heading("Region",    text="Region")
    tree.heading("City",      text="City / Municipality")
    tree.heading("Barangay",  text="Barangay")
    tree.column("ID",        width=40,  anchor="center", stretch=False)
    tree.column("Name",      width=120, anchor="w",      stretch=True)
    tree.column("Region",    width=130, anchor="w",      stretch=True)
    tree.column("City",      width=120, anchor="w",      stretch=True)
    tree.column("Barangay",  width=130, anchor="w",      stretch=True)
    tree.grid(row=1, column=0, sticky="nsew", padx=(10, 0), pady=(0, 10))
    tree_scroll.config(command=tree.yview)
    tree.tag_configure("odd",  background=PANEL)
    tree.tag_configure("even", background="#161a26")

    # ── Add Purok card ────────────────────────────────────────────────────────
    add_card = tk.Frame(wrapper, bg=CARD,
                        highlightthickness=1, highlightbackground=BORDER)
    add_card.grid(row=5, column=0, sticky="ew", padx=26, pady=(0, 10))
    add_card.grid_columnconfigure(0, weight=1)

    # Card title + collapse toggle
    add_hdr = tk.Frame(add_card, bg=CARD)
    add_hdr.grid(row=0, column=0, sticky="ew", padx=16, pady=(12, 0))
    add_hdr.grid_columnconfigure(0, weight=1)
    tk.Label(add_hdr, text="▸ ADD NEW PUROK",
             font=("Courier", 8, "bold"), fg=ACCENT, bg=CARD).grid(
                 row=0, column=0, sticky="w")

    # ── Location selection area ───────────────────────────────────────────────
    loc_frame = tk.Frame(add_card, bg=CARD)
    loc_frame.grid(row=1, column=0, sticky="ew", padx=16, pady=(10, 0))
    loc_frame.grid_columnconfigure((0, 1, 2), weight=1)

    def make_label(parent, text, col):
        tk.Label(parent, text=text,
                 font=("Courier", 7, "bold"),
                 fg=MUTED, bg=CARD).grid(row=0, column=col, sticky="w", padx=(0, 6))

    make_label(loc_frame, "REGION / PROVINCE",  0)
    make_label(loc_frame, "CITY / MUNICIPALITY", 1)
    make_label(loc_frame, "BARANGAY",            2)

    region_var   = tk.StringVar(value="— select region —")
    city_var     = tk.StringVar(value="— select city —")
    barangay_var = tk.StringVar(value="— select barangay —")

    def styled_combo(parent, textvariable, col):
        wrap = tk.Frame(parent, bg=PANEL,
                        highlightthickness=1, highlightbackground=BORDER)
        wrap.grid(row=1, column=col, sticky="ew", padx=(0, 6), pady=(4, 0))
        cb = ttk.Combobox(wrap, textvariable=textvariable,
                          state="readonly", style="Loc.TCombobox",
                          font=("Courier", 9))
        cb.pack(fill="x", padx=6, pady=5)
        cb.bind("<FocusIn>",  lambda e: wrap.config(highlightbackground=ACCENT))
        cb.bind("<FocusOut>", lambda e: wrap.config(highlightbackground=BORDER))
        return cb, wrap

    region_cb,   region_wrap   = styled_combo(loc_frame, region_var,   0)
    city_cb,     city_wrap     = styled_combo(loc_frame, city_var,     1)
    barangay_cb, barangay_wrap = styled_combo(loc_frame, barangay_var, 2)

    region_cb["values"]   = list(PH_LOCATIONS.keys())
    city_cb["values"]     = []
    barangay_cb["values"] = []

    # Location badge (shows chosen summary)
    badge_var = tk.StringVar(value="")
    badge_lbl = tk.Label(loc_frame, textvariable=badge_var,
                         font=("Courier", 8), fg=SUCCESS, bg=CARD,
                         anchor="w")
    badge_lbl.grid(row=2, column=0, columnspan=3, sticky="w", pady=(5, 0))

    def update_badge():
        r = region_var.get()
        c = city_var.get()
        b = barangay_var.get()
        parts = []
        if r and not r.startswith("—"): parts.append(r)
        if c and not c.startswith("—"): parts.append(c)
        if b and not b.startswith("—"): parts.append(b)
        badge_var.set("📍 " + " › ".join(parts) if parts else "")

    def on_region_change(event=None):
        region = region_var.get()
        cities = list(PH_LOCATIONS.get(region, {}).keys())
        city_var.set("— select city —")
        barangay_var.set("— select barangay —")
        city_cb["values"]     = cities
        barangay_cb["values"] = []
        update_badge()

    def on_city_change(event=None):
        region = region_var.get()
        city   = city_var.get()
        brgys  = PH_LOCATIONS.get(region, {}).get(city, [])
        barangay_var.set("— select barangay —")
        barangay_cb["values"] = brgys
        update_badge()

    def on_barangay_change(event=None):
        update_badge()

    region_cb.bind("<<ComboboxSelected>>",   on_region_change)
    city_cb.bind("<<ComboboxSelected>>",     on_city_change)
    barangay_cb.bind("<<ComboboxSelected>>", on_barangay_change)

    # Separator
    tk.Frame(add_card, bg=BORDER, height=1).grid(
        row=2, column=0, sticky="ew", padx=16, pady=(12, 0))

    # ── Purok name + Add button ───────────────────────────────────────────────
    input_row = tk.Frame(add_card, bg=CARD)
    input_row.grid(row=3, column=0, sticky="ew", padx=16, pady=(10, 14))
    input_row.grid_columnconfigure(0, weight=1)

    tk.Label(input_row, text="PUROK NAME",
             font=("Courier", 7, "bold"), fg=MUTED, bg=CARD).grid(
                 row=0, column=0, sticky="w", pady=(0, 4))

    name_input_row = tk.Frame(input_row, bg=CARD)
    name_input_row.grid(row=1, column=0, sticky="ew")
    name_input_row.grid_columnconfigure(0, weight=1)

    entry_wrap = tk.Frame(name_input_row, bg=PANEL,
                          highlightthickness=1, highlightbackground=BORDER)
    entry_wrap.grid(row=0, column=0, sticky="ew", padx=(0, 8))

    purok_entry = tk.Entry(entry_wrap, bg=PANEL, fg=TEXT,
                           font=("Courier", 10), relief="flat",
                           insertbackground=ACCENT, bd=0)
    purok_entry.pack(fill="x", padx=10, pady=7)

    def _entry_fi(e): entry_wrap.config(highlightbackground=ACCENT)
    def _entry_fo(e): entry_wrap.config(highlightbackground=BORDER)
    purok_entry.bind("<FocusIn>",  _entry_fi)
    purok_entry.bind("<FocusOut>", _entry_fo)

    add_btn = tk.Button(name_input_row, text="+ Add",
                        font=("Courier", 9, "bold"),
                        bg=ACCENT, fg="white",
                        activebackground="#3a7ce8", activeforeground="white",
                        relief="flat", bd=0, cursor="hand2")
    add_btn.grid(row=0, column=1, ipady=7, ipadx=14)

    # ── Open Residents button ─────────────────────────────────────────────────
    open_btn = tk.Button(wrapper,
                         text="OPEN RESIDENTS  →",
                         font=("Courier", 10, "bold"),
                         bg=SUCCESS, fg="#0d0f14",
                         activebackground="#3ab868", activeforeground="#0d0f14",
                         relief="flat", bd=0, cursor="hand2")
    open_btn.grid(row=6, column=0, sticky="ew", padx=26, pady=(0, 6), ipady=11)

    # ── Archived Puroks collapsible panel ─────────────────────────────────────
    archive_panel_visible = tk.BooleanVar(value=False)

    archive_toggle_btn = tk.Button(
        wrapper,
        text="📦  Show Archived Puroks  ▾",
        font=("Courier", 8, "bold"),
        bg=PANEL, fg=WARNING,
        activebackground=BORDER, activeforeground=WARNING,
        relief="flat", bd=0, cursor="hand2",
        anchor="w"
    )
    archive_toggle_btn.grid(row=7, column=0, sticky="ew", padx=26, pady=(0, 4), ipady=5)

    # The collapsible card — hidden by default
    arch_card = tk.Frame(wrapper, bg=CARD,
                         highlightthickness=1, highlightbackground=BORDER)
    arch_card.grid_columnconfigure(0, weight=1)

    arch_hdr = tk.Frame(arch_card, bg=CARD)
    arch_hdr.grid(row=0, column=0, columnspan=2, sticky="ew", padx=16, pady=(10, 6))
    arch_hdr.grid_columnconfigure(1, weight=1)
    tk.Label(arch_hdr, text="📦  ARCHIVED PUROKS",
             font=("Courier", 8, "bold"), fg=WARNING, bg=CARD).grid(
                 row=0, column=0, sticky="w")
    arch_count_lbl = tk.Label(arch_hdr, text="0 archived",
                               font=("Courier", 8), fg=MUTED, bg=CARD)
    arch_count_lbl.grid(row=0, column=1, sticky="e")

    arch_scroll = tk.Scrollbar(arch_card, orient="vertical",
                                bg=BORDER, troughcolor=CARD,
                                width=6, relief="flat", highlightthickness=0)
    arch_scroll.grid(row=1, column=1, sticky="ns", pady=(0, 8))

    arch_tree = ttk.Treeview(arch_card,
                              columns=("ID", "Name", "Region", "City", "Barangay"),
                              show="headings",
                              style="Custom.Treeview",
                              height=4,
                              yscrollcommand=arch_scroll.set)
    arch_tree.heading("ID",       text="ID")
    arch_tree.heading("Name",     text="Purok Name")
    arch_tree.heading("Region",   text="Region")
    arch_tree.heading("City",     text="City / Municipality")
    arch_tree.heading("Barangay", text="Barangay")
    arch_tree.column("ID",       width=40,  anchor="center", stretch=False)
    arch_tree.column("Name",     width=120, anchor="w",      stretch=True)
    arch_tree.column("Region",   width=120, anchor="w",      stretch=True)
    arch_tree.column("City",     width=110, anchor="w",      stretch=True)
    arch_tree.column("Barangay", width=120, anchor="w",      stretch=True)
    arch_tree.grid(row=1, column=0, sticky="nsew", padx=(10, 0), pady=(0, 8))
    arch_scroll.config(command=arch_tree.yview)
    arch_tree.tag_configure("arch_odd",  background="#1a1408")
    arch_tree.tag_configure("arch_even", background="#141008")

    tk.Label(arch_card,
             text="Right-click a row to Restore or Delete permanently",
             font=("Courier", 7), fg=MUTED, bg=CARD).grid(
                 row=2, column=0, columnspan=2, pady=(0, 10))

    # Footer
    tk.Label(wrapper,
             text="© Barangay Management System  ·  v1.0",
             font=("Courier", 7), fg=BORDER, bg=BG).grid(row=9, column=0, pady=(2, 10))

    # ── Logic ─────────────────────────────────────────────────────────────────
    def refresh_archived():
        for row in arch_tree.get_children():
            arch_tree.delete(row)
        archived = database.get_archived_puroks()
        for i, p in enumerate(archived):
            tag = "arch_odd" if i % 2 == 0 else "arch_even"
            if len(p) >= 5:
                arch_tree.insert("", "end", values=p[:5], tags=(tag,))
            else:
                arch_tree.insert("", "end",
                                 values=(p[0], p[1], "—", "—", "—"), tags=(tag,))
        n = len(archived)
        arch_count_lbl.config(
            text=f"{n} archived entr{'y' if n == 1 else 'ies'}")

    def toggle_archive_panel():
        if archive_panel_visible.get():
            arch_card.grid_forget()
            archive_panel_visible.set(False)
            archive_toggle_btn.config(text="📦  Show Archived Puroks  ▾")
        else:
            arch_card.grid(row=8, column=0, sticky="ew", padx=26, pady=(0, 8))
            archive_panel_visible.set(True)
            archive_toggle_btn.config(text="📦  Hide Archived Puroks  ▴")
            refresh_archived()

    archive_toggle_btn.config(command=toggle_archive_panel)

    # Right-click menu for the archived tree
    arch_ctx = tk.Menu(root, tearoff=0,
                       bg=CARD, fg=TEXT,
                       activebackground=ACCENT, activeforeground="white",
                       font=("Courier", 9), relief="flat", bd=0)
    arch_ctx.add_command(label="♻  Restore Purok", foreground=SUCCESS,
                         activebackground="#0d3320", activeforeground=SUCCESS,
                         command=lambda: _arch_restore())
    arch_ctx.add_separator()
    arch_ctx.add_command(label="⚠  Delete Permanently", foreground="#ff5f5f",
                         activebackground="#7a1e1e", activeforeground="#ff5f5f",
                         command=lambda: _arch_delete())

    _arch_target = {"iid": None}

    def _show_arch_menu(event):
        iid = arch_tree.identify_row(event.y)
        if not iid:
            return
        arch_tree.selection_set(iid)
        _arch_target["iid"] = iid
        try:
            arch_ctx.tk_popup(event.x_root, event.y_root)
        finally:
            arch_ctx.grab_release()

    def _get_arch_values():
        iid = _arch_target["iid"]
        if not iid:
            return None, None
        vals = arch_tree.item(iid)["values"]
        return vals[0], vals[1]

    def _arch_restore():
        purok_id, purok_name = _get_arch_values()
        if purok_id is None:
            return
        confirm = messagebox.askyesno(
            "Restore Purok",
            f"Restore  '{purok_name}'?\n\n"
            "It will reappear in the active Purok list.")
        if confirm:
            database.restore_purok(purok_id)
            refresh_puroks()
            refresh_archived()

    def _arch_delete():
        purok_id, purok_name = _get_arch_values()
        if purok_id is None:
            return
        confirm = messagebox.askyesno(
            "Delete Permanently",
            f"Permanently delete  '{purok_name}'?\n\n"
            "This cannot be undone and will unlink\n"
            "all associated residents.")
        if confirm:
            database.delete_purok(purok_id)
            refresh_archived()

    arch_tree.bind("<Button-3>", _show_arch_menu)
    arch_tree.bind("<Button-2>", _show_arch_menu)

    def refresh_puroks():
        for row in tree.get_children():
            tree.delete(row)
        puroks = database.get_puroks()
        for i, p in enumerate(puroks):
            tag = "odd" if i % 2 == 0 else "even"
            # p may be (id, name) or (id, name, region, city, barangay)
            if len(p) >= 5:
                tree.insert("", "end", values=p[:5], tags=(tag,))
            else:
                tree.insert("", "end",
                            values=(p[0], p[1], "—", "—", "—"), tags=(tag,))
        count_lbl.config(
            text=f"{len(puroks)} entr{'y' if len(puroks)==1 else 'ies'}")

    def add_purok(event=None):
        name     = purok_entry.get().strip()
        region   = region_var.get()
        city     = city_var.get()
        barangay = barangay_var.get()

        if not name:
            messagebox.showwarning("Missing Name", "Please enter a Purok name.")
            return

        # Warn but don't block if location is incomplete
        if region.startswith("—") or city.startswith("—") or barangay.startswith("—"):
            proceed = messagebox.askyesno(
                "Incomplete Location",
                "Location is not fully set.\nSave purok without full location?")
            if not proceed:
                return

        # Sanitise placeholder strings to empty
        reg_val = "" if region.startswith("—")   else region
        cit_val = "" if city.startswith("—")     else city
        brg_val = "" if barangay.startswith("—") else barangay

        # database.add_purok supports (name) or (name, region, city, barangay)
        try:
            database.add_purok(name, reg_val, cit_val, brg_val)
        except TypeError:
            # Fallback if the DB function only accepts name
            database.add_purok(name)

        purok_entry.delete(0, tk.END)
        region_var.set("— select region —")
        city_var.set("— select city —")
        barangay_var.set("— select barangay —")
        city_cb["values"]     = []
        barangay_cb["values"] = []
        badge_var.set("")
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

    # ── Right-click context menu ───────────────────────────────────────────────
    ctx_menu = tk.Menu(root, tearoff=0,
                       bg=CARD, fg=TEXT,
                       activebackground=ACCENT, activeforeground="white",
                       font=("Courier", 9),
                       relief="flat", bd=0)

    # Separator style
    ctx_menu.add_command(label="⚠  Delete Purok",  foreground="#ff5f5f",
                         activebackground="#7a1e1e", activeforeground="#ff5f5f",
                         command=lambda: _ctx_delete())
    ctx_menu.add_separator()
    ctx_menu.add_command(label="📦  Archive Purok", foreground=WARNING,
                         activebackground="#4a3a00", activeforeground=WARNING,
                         command=lambda: _ctx_archive())

    _ctx_target = {"iid": None}   # holds the row that was right-clicked

    def _show_context_menu(event):
        """Select the row under cursor then show the menu."""
        iid = tree.identify_row(event.y)
        if not iid:
            return
        tree.selection_set(iid)
        _ctx_target["iid"] = iid
        try:
            ctx_menu.tk_popup(event.x_root, event.y_root)
        finally:
            ctx_menu.grab_release()

    def _get_ctx_values():
        iid = _ctx_target["iid"]
        if not iid:
            return None, None
        vals = tree.item(iid)["values"]
        return vals[0], vals[1]   # purok_id, purok_name

    def _ctx_delete():
        purok_id, purok_name = _get_ctx_values()
        if purok_id is None:
            return
        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Permanently delete  '{purok_name}'?\n\n"
            "This cannot be undone and will remove all\n"
            "associated residents from this purok.")
        if confirm:
            database.delete_purok(purok_id)
            refresh_puroks()

    def _ctx_archive():
        purok_id, purok_name = _get_ctx_values()
        if purok_id is None:
            return
        confirm = messagebox.askyesno(
            "Archive Purok",
            f"Archive  '{purok_name}'?\n\n"
            "The purok will be hidden from the list\n"
            "but can be restored later.")
        if confirm:
            database.archive_purok(purok_id)
            refresh_puroks()

    tree.bind("<Button-3>", _show_context_menu)   # right-click (Windows/Linux)
    tree.bind("<Button-2>", _show_context_menu)   # right-click (macOS)

    add_btn.config(command=add_purok)
    open_btn.config(command=open_residents)
    purok_entry.bind("<Return>", add_purok)
    tree.bind("<Return>", open_residents)
    tree.bind("<Double-1>", open_residents)

    refresh_puroks()
    root.mainloop()