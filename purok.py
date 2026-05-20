import tkinter as tk
from tkinter import ttk, messagebox
import database
import ui
import users_database
from logo import make_logo_canvas


# ── Philippine Location Data (Davao Region focus + major regions) ─────────────
PH_LOCATIONS = {
    "Davao Region (XI)": {
        "Davao del Sur": {
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
                "San Antonio", "Santo Niño", "Sasa", "Sirib", "Sirawan",
                "Tacunan", "Tagakpan", "Tagluno", "Tagurano", "Talomo",
                "Talomonan", "Tamayong", "Tamugan", "Tapak", "Tawan-tawan",
                "Tibuloy", "Tibungco", "Tigatto", "Toril", "Tugbok", "Tungkalan",
                "Ubalde", "Ula", "Waan", "Wilfredo Aquino", "Wines",
            ],
            "Digos City": [
                "Aplaya", "Balabag", "Binaton", "Cogon", "Colorado", "Dawis",
                "Dulangan", "Goma", "Igpit", "Kapatagan", "Kiagot", "Lungag",
                "Mahayahay", "Matti", "Ruparan", "San Agustin", "San Jose",
                "San Miguel", "San Roque", "Sinawilan", "Soong", "Tiguman",
                "Tres de Mayo", "Zone 1", "Zone 2", "Zone 3",
            ],
        },
        "Davao del Norte": {
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
        },
        "Davao de Oro": {
            "Compostela": [
                "Aurora", "Bagongon", "Cabiloyan", "Gaboc", "Gabi",
                "Jose Rizal", "Mabuhay", "Magading", "Mamangan",
                "Mangga", "Mozon", "New Leyte", "Osmeña",
                "Poblacion", "San Jose", "San Miguel", "San Roque",
                "Tagnocon", "Upper Sua",
            ],
            "Laak": [
                "Aguinaldo", "Banbanon", "Binasbas", "Cebulida", "Concepcion",
                "Datu Balong", "Datu Davao", "Datu Salumay", "Elibrado",
                "Kapatagan", "Lam-it", "Langub", "Lianga", "Maharlika",
                "Malinawon", "Mambayaan", "Melgar", "Napnapan", "Poblacion",
                "San Antonio", "San Marcos", "San Vicente", "Santo Niño",
            ],
            "Mabini (Doña Alicia)": [
                "Anitapan", "Cabasagan", "Gatpan", "Kadapa", "Langatian",
                "Libasan", "Little Tanay", "Longganapan", "Maduao",
                "Nabunwa", "New San Lazaro", "Panalisayan", "Poblacion",
                "San Antonio", "Sampao", "San Jose", "San Pablo",
            ],
            "Maco": [
                "Anibongan", "Anislagan", "Binuangan", "Dawak", "Don Panaca",
                "Dumlan", "Guiwanon", "Kinuban", "Lawa", "Liban",
                "Malamodao", "Mapanapan", "New Barili", "New Leyte",
                "Panibasan", "Panoraon", "Poblacion", "San Miguel",
                "San Roque", "Sangab", "Tagbaros", "Tinanogan", "Upper Ilao",
            ],
            "Maragusan (San Mariano)": [
                "Bagong Silang", "Bat-og", "Binagong", "Camp 2", "Camp 3",
                "Cebulida", "Kapatagan", "Lahi", "Lam-ag", "Linibunan",
                "Mahaba", "Maharlika", "Mapawa", "Mauswagon", "New Albay",
                "Poblacion", "San Roque","Talian","Tupaz","Victory",
            ],
            "Mawab": [
                "Andili", "Bawani", "Bawing", "B. Melgar", "Cadayunan",
                "Calamba", "Cone-sa", "Dawhan", "Divisoria", "Igabon",
                "Linao", "Mabantao", "Malinawon", "Malita", "Nuevo Iloco",
                "Poblacion", "Salvacion", "Saosao", "Sawangan", "Sawom",
                "Sogo-sogo", "Sucod", "Tagbaros", "Tagmamarkay", "Tuburan",
            ],
            "Monkayo": [
                "Awao", "Babag", "Banlag", "Baylo", "Basa", "Casoon",
                "E. Manikop", "Tandang Sora", "Leveriza", "Macopa",
                "Mamonga", "Mount Diwata (Diwalwal)", "Najos-Labid", "Olo",
                "Oligopolistic Village", "Poblacion", "Rizal", "Salvacion",
                "San Jose", "Tubo-tubo", "Upper Ulip", "Union",
            ],
            "Montevista": [
                "Banagbanag", "Banglas", "Canidkid", "Sibucao", "Camansi",
                "Casib-ang", "Cawayan", "Cutcutan", "Dauman", "Danag",
                "Kamanlangan", "Liban", "Ligao", "Limboc", "Lub-a",
                "Nalisan", "Poblacion", "Santa Cruz", "Tambobong", "Tapayan",
            ],
            "Nabunturan": [
                "Anislagan", "Basak", "Bayabas", "Bukal", "Cameron",
                "Candalapan", "Casig-ang", "Concepcion", "Inuas", "Katipunan",
                "Loreto", "Luna", "Magangit", "Magugpo", "Mainit",
                "Magsaysay", "New Cebu", "New Dauis", "New Davao", "New Leyte",
                "New Pandan", "New Purok", "New Visayas", "Palencia",
                "Pangi", "Poblacion", "San Miguel", "San Roque", "Sibulan",
                "Tagnocon",
            ],
            "New Bataan": [
                "Bantacan", "Bantawan", "Batang", "Bathan", "Binalgan",
                "Cabinuangan", "Camanlangan", "Cabay’an", "Casahan", "Chiong-O",
                "Dalangpan", "Inayagan", "Kahayag", "Kinuban", "Mabini",
                "Magsaysay", "Magangit", "Manurigao", "Poblacion", "Salamanca",
                "Sampao", "San Isidro", "San Jose", "San Roque", "Tandawan",
            ],
            "Pantukan": [
                "Araibo", "Bongabong", "Camp 4", "Cabuacan", "Danawan",
                "Dapnan", "Igangon", "Kingking", "Lahi", "Langaylangay",
                "Magnaga", "Maibo", "P. Gomez", "Pandasan", "Poblacion",
                "Sibahay", "Sibulan", "Tagdangua", "Tanglaw", "Tibal-og",
            ],
        },
        "Davao Oriental": {
            "Mati City": [
                "Badas", "Bobon", "Buso", "Cabuaya", "Central", "Don Enrique Lopez",
                "Don Martin Marundan", "Don Salvador Lopez Sr.", "Dawan", "Macambol",
                "Magsaysay", "Matiao", "Mayo", "Sainz", "Sanghay", "Tagabakid",
                "Tagbinonga", "Taguibo", "Tamisan",
            ],
        },
    },
    "Metro Manila (NCR)": {
        "Metro Manila": {
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
    },
    "Central Visayas (VII)": {
        "Cebu": {
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
    },
    "Northern Mindanao (X)": {
        "Misamis Oriental": {
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
        },
        "Lanao del Norte": {
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
    },
}


def run_purok_window(admin_username=None):
    database.create_purok_table()

    import theme as _font
    BG = _font.BG; CARD = _font.CARD; PANEL = _font.PANEL
    BORDER = _font.BORDER; ACCENT = _font.ACCENT; ACCENT2 = _font.ACCENT2
    SUCCESS = _font.SUCCESS; WARN = _font.WARN; DANGER = _font.DANGER
    TEXT = _font.TEXT; MUTED = _font.MUTED

    # ── Root window ───────────────────────────────────────────────────────────
    root = tk.Tk()
    root.title("Purok Management")
    root.configure(bg=BG)
    root.attributes("-fullscreen", True)
    root.resizable(True, True)
    # Press Escape to exit fullscreen
    root.bind("<Escape>", lambda e: root.attributes("-fullscreen", False))

    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    # ── Outer wrapper ─────────────────────────────────────────────────────────
    wrapper = tk.Frame(root, bg=BG)
    wrapper.grid(row=0, column=0, sticky="nsew")
    wrapper.grid_rowconfigure(5, weight=1)   # treeview row expands
    wrapper.grid_columnconfigure(0, weight=1)
    wrapper.grid_rowconfigure(2, weight=0)
    wrapper.grid_rowconfigure(4, weight=0)
    wrapper.grid_rowconfigure(6, weight=0)
    wrapper.grid_rowconfigure(7, weight=0)
    wrapper.grid_rowconfigure(8, weight=0)
    wrapper.grid_rowconfigure(10, weight=0)

    # ── Titlebar ────────────────────────────────────────────────
    titlebar = tk.Frame(wrapper, bg=CARD, height=34)
    titlebar.grid(row=0, column=0, sticky="ew")
    titlebar.pack_propagate(False)

    tk.Label(titlebar, text="Purok Management  ·  v1.0",
             font=_font.font("Courier", 9, "bold"), fg=MUTED, bg=CARD).pack(side="left", padx=14)

    # Drag to move
    def _tb_drag_start(e): root._dx, root._dy = e.x_root, e.y_root
    def _tb_drag_move(e):
        root.attributes("-fullscreen", False)
        root.geometry(f"+{root.winfo_x()+e.x_root-root._dx}+{root.winfo_y()+e.y_root-root._dy}")
        root._dx, root._dy = e.x_root, e.y_root
    titlebar.bind("<ButtonPress-1>", _tb_drag_start)
    titlebar.bind("<B1-Motion>",     _tb_drag_move)

    # Window controls on the right
    ctrl_frame = tk.Frame(titlebar, bg=CARD)
    ctrl_frame.pack(side="right", padx=(0, 6), pady=4)

    def _minimize():
        root.attributes("-fullscreen", False)
        root.state("iconic")

    # ── Fullscreen toggle helper (defined before use) ────────
    _fs_saved = {"geo": None}
    def _toggle_fullscreen():
        is_fs = root.attributes("-fullscreen")
        if is_fs:
            root.attributes("-fullscreen", False)
            if _fs_saved["geo"]:
                root.geometry(_fs_saved["geo"])
            else:
                root.geometry("960x800")
                x = (root.winfo_screenwidth() - 960) // 2
                y = (root.winfo_screenheight() - 800) // 2
                root.geometry(f"960x800+{x}+{y}")
        else:
            _fs_saved["geo"] = root.geometry()
            root.attributes("-fullscreen", True)

    for sym, cmd, hov in [("🗖", _toggle_fullscreen, BORDER),
                           ("─", _minimize, BORDER),
                           ("✕", lambda: root.destroy(), DANGER)]:
        b = tk.Button(ctrl_frame, text=sym, command=cmd,
                      bg=CARD, fg=MUTED,
                      activebackground=hov, activeforeground=TEXT,
                      font=_font.font("Courier", 10), relief="flat", bd=0,
                      cursor="hand2", width=3)
        b.pack(side="left", ipady=1)

    # Top accent stripe
    tk.Frame(wrapper, bg=ACCENT, height=3).grid(row=1, column=0, sticky="ew")

    # Logo
    logo_canvas = make_logo_canvas(wrapper, scale=0.75, bg=BG)
    logo_canvas.grid(row=2, column=0, sticky="w", padx=36, pady=(20, 0))

    # Separator
    tk.Frame(wrapper, bg=BORDER, height=1).grid(
        row=3, column=0, sticky="ew", padx=36, pady=(14, 0))

    # ── Header ────────────────────────────────────────────────────────────────
    header = tk.Frame(wrapper, bg=BG)
    header.grid(row=4, column=0, sticky="ew", padx=36, pady=(16, 10))
    header.grid_columnconfigure(1, weight=1)

    dot_c = tk.Canvas(header, width=28, height=28, bg=BG, highlightthickness=0)
    dot_c.grid(row=0, column=0, rowspan=2, padx=(0, 12))
    dot_c.create_oval(0,  0, 12, 12, fill=ACCENT,  outline="")
    dot_c.create_oval(15, 0, 27, 12, fill=ACCENT2, outline="")
    dot_c.create_oval(7, 15, 19, 27, fill=SUCCESS,  outline="")

    title_f = tk.Frame(header, bg=BG)
    title_f.grid(row=0, column=1, sticky="w")
    tk.Label(title_f, text="Purok",
             font=_font.font("Georgia", 22, "bold"), fg=TEXT, bg=BG).pack(side="left")
    tk.Label(title_f, text=" Management",
             font=_font.font("Georgia", 22, "italic"), fg=ACCENT, bg=BG).pack(side="left")
    tk.Label(header,
             text="Select a purok to view its residents",
             font=_font.font("Courier", 8), fg=MUTED, bg=BG).grid(row=1, column=1, sticky="w")

    # ── Admin Panel button (top right) — only for admins ─────────
    if admin_username and users_database.can_access_admin_panel(admin_username):
        def _open_admin_from_purok():
            # Verify password via popup
            pw_win = tk.Toplevel(root)
            pw_win.title("Confirm Access")
            pw_win.configure(bg=CARD)
            pw_win.geometry("320x180")
            pw_win.resizable(False, False)
            pw_win.grab_set()
            pw_win.transient(root)
            sw, sh = pw_win.winfo_screenwidth(), pw_win.winfo_screenheight()
            pw_win.geometry(f"320x180+{(sw-320)//2}+{(sh-180)//2}")

            tk.Label(pw_win, text="Enter your password to continue:",
                     font=_font.font("Courier", 9, "bold"),
                     fg=TEXT, bg=CARD).pack(pady=(16, 8))

            pw_entry_wrap = tk.Frame(pw_win, bg=PANEL,
                                      highlightthickness=1, highlightbackground=BORDER)
            pw_entry_wrap.pack(padx=20, fill="x")
            pw_entry = tk.Entry(pw_entry_wrap, bg=PANEL, fg=TEXT,
                                font=_font.font("Courier", 11), show="●",
                                relief="flat", insertbackground=ACCENT, bd=0)
            pw_entry.pack(fill="x", padx=8, pady=6)
            pw_entry.focus_set()

            def _confirm_pw():
                p = pw_entry.get().strip()
                if not users_database.validate_login(admin_username, p):
                    messagebox.showerror("Access Denied", "Incorrect password.")
                    return
                pw_win.destroy()
                import admin_panel
                admin_panel.run_admin_panel(admin_username, lambda: None)

            pw_entry.bind("<Return>", lambda e: _confirm_pw())
            btn_row = tk.Frame(pw_win, bg=CARD)
            btn_row.pack(fill="x", padx=20, pady=(12, 0))
            tk.Button(btn_row, text="✓  Confirm", command=_confirm_pw,
                      bg=ACCENT, fg="white",
                      font=_font.font("Courier", 9, "bold"),
                      relief="flat", bd=0, cursor="hand2",
                      padx=14, pady=5).pack(side="left", padx=(0, 6))
            tk.Button(btn_row, text="✕  Cancel", command=pw_win.destroy,
                      bg=DANGER, fg="white",
                      font=_font.font("Courier", 9, "bold"),
                      relief="flat", bd=0, cursor="hand2",
                      padx=14, pady=5).pack(side="left")

        # Admin Panel tab button — top right of header
        admin_tab_outer = tk.Frame(header, bg="#1a1030",
                                    highlightthickness=1, highlightbackground=ACCENT2)
        admin_tab_outer.grid(row=0, column=2, rowspan=2, sticky="ne", padx=(12, 0))
        admin_tab_btn = tk.Button(admin_tab_outer, text="⚙  ADMIN",
                                   command=_open_admin_from_purok,
                                   bg="#140b24", fg=ACCENT2,
                                   activebackground="#2a1a4a", activeforeground="#b090ff",
                                   font=_font.font("Courier", 8, "bold"),
                                   relief="flat", bd=0, cursor="hand2",
                                   padx=10, pady=4)
        admin_tab_btn.pack()
        def _ad_in(e):
            admin_tab_outer.config(highlightbackground="#b090ff")
            admin_tab_btn.config(fg="#c8aaff")
        def _ad_out(e):
            admin_tab_outer.config(highlightbackground=ACCENT2)
            admin_tab_btn.config(fg=ACCENT2)
        admin_tab_btn.bind("<Enter>", _ad_in)
        admin_tab_btn.bind("<Leave>", _ad_out)

    # ── Treeview card ─────────────────────────────────────────────────────────
    tree_card = tk.Frame(wrapper, bg=CARD,
                         highlightthickness=1, highlightbackground=BORDER)
    tree_card.grid(row=5, column=0, sticky="nsew", padx=36, pady=(0, 10))
    tree_card.grid_rowconfigure(3, weight=1)
    tree_card.grid_columnconfigure(0, weight=1)
    tree_card.grid_columnconfigure(1, weight=0)

    card_hdr = tk.Frame(tree_card, bg=CARD)
    card_hdr.grid(row=0, column=0, columnspan=2, sticky="ew", padx=16, pady=(12, 6))
    card_hdr.grid_columnconfigure(1, weight=1)

    tk.Label(card_hdr, text="▸ PUROK LIST",
             font=_font.font("Courier", 8, "bold"), fg=ACCENT, bg=CARD).grid(
                 row=0, column=0, sticky="w")
    count_lbl = tk.Label(card_hdr, text="0 entries",
                         font=_font.font("Courier", 8), fg=MUTED, bg=CARD)
    count_lbl.grid(row=0, column=1, sticky="e")

    # ── Search / Filter bar ───────────────────────────────────────────────────
    search_frame = tk.Frame(tree_card, bg=CARD)
    search_frame.grid(row=1, column=0, columnspan=2, sticky="ew",
                      padx=20, pady=(0, 8))
    search_frame.grid_columnconfigure(0, weight=1)

    # Magnifying-glass icon label
    search_icon = tk.Label(search_frame, text="🔍",
                           font=_font.font("Segoe UI", 11), fg=MUTED, bg=CARD)
    search_icon.grid(row=0, column=0, sticky="w", padx=(0, 6))

    search_entry_wrap = tk.Frame(search_frame, bg=PANEL,
                                  highlightthickness=1, highlightbackground=BORDER)
    search_entry_wrap.grid(row=0, column=1, sticky="ew", padx=(0, 6))

    search_var = tk.StringVar(value="")
    search_entry = tk.Entry(search_entry_wrap,
                            textvariable=search_var,
                            bg=PANEL, fg=TEXT,
                            font=_font.font("Courier", 10), relief="flat",
                            insertbackground=ACCENT, bd=0)
    search_entry.pack(fill="x", padx=10, pady=6)
    search_entry.bind("<FocusIn>",
                      lambda e: search_entry_wrap.config(highlightbackground=ACCENT))
    search_entry.bind("<FocusOut>",
                      lambda e: search_entry_wrap.config(highlightbackground=BORDER))

    def clear_search():
        search_var.set("")
        search_entry.focus_set()
        filter_puroks()

    clear_btn = tk.Button(search_frame, text="✕",
                          font=_font.font("Courier", 9, "bold"),
                          bg=PANEL, fg=MUTED,
                          activebackground=BORDER, activeforeground=TEXT,
                          relief="flat", bd=0, cursor="hand2",
                          command=clear_search, width=2)
    clear_btn.grid(row=0, column=2, sticky="e", ipady=1)

    # Hint label below search
    hint_lbl = tk.Label(tree_card,
                        text="Type to filter by name, province, city, or barangay",
                        font=_font.font("Courier", 7), fg=MUTED, bg=CARD)
    hint_lbl.grid(row=2, column=0, columnspan=2, sticky="w", padx=16, pady=(0, 6))

    # ttk style
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Custom.Treeview",
                    background=PANEL, foreground=TEXT, fieldbackground=PANEL,
                    borderwidth=0, font=_font.font("Courier", 10), rowheight=38)
    style.configure("Custom.Treeview.Heading",
                    background=CARD, foreground=ACCENT,
                    font=_font.font("Courier", 9, "bold"), borderwidth=0, relief="flat")
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
    tree_scroll.grid(row=3, column=1, sticky="ns", pady=(0, 10))

    tree = ttk.Treeview(tree_card,
                        columns=("ID", "Name", "Province", "City", "Barangay"),
                        show="headings",
                        style="Custom.Treeview",
                        yscrollcommand=tree_scroll.set)
    tree.heading("ID",       text="ID")
    tree.heading("Name",     text="Purok Name")
    tree.heading("Province", text="Province")
    tree.heading("City",     text="City / Municipality")
    tree.heading("Barangay", text="Barangay")
    tree.column("ID",       width=60,  minwidth=40,  anchor="center", stretch=False)
    tree.column("Name",     width=200, minwidth=120, anchor="w",      stretch=True)
    tree.column("Province", width=220, minwidth=120, anchor="w",      stretch=True)
    tree.column("City",     width=200, minwidth=120, anchor="w",      stretch=True)
    tree.column("Barangay", width=240, minwidth=130, anchor="w",      stretch=True)
    tree.grid(row=3, column=0, sticky="nsew", padx=(10, 0), pady=(0, 10))
    tree_scroll.config(command=tree.yview)
    # Compute theme-aware alternating row colors
    cur_theme = _font.get_current_theme()
    if cur_theme == "light":
        even_bg = "#e0e3ec"
    elif cur_theme == "forest":
        even_bg = "#182818"
    else:
        even_bg = "#161a26"
    tree.tag_configure("odd",  background=PANEL)
    tree.tag_configure("even", background=even_bg)

    # ── Add Purok card ────────────────────────────────────────────────────────
    add_card = tk.Frame(wrapper, bg=CARD,
                        highlightthickness=1, highlightbackground=BORDER)
    add_card.grid(row=6, column=0, sticky="ew", padx=36, pady=(0, 10))
    add_card.grid_columnconfigure(0, weight=1)

    # Card title + collapse toggle
    add_hdr = tk.Frame(add_card, bg=CARD)
    add_hdr.grid(row=0, column=0, sticky="ew", padx=16, pady=(12, 0))
    add_hdr.grid_columnconfigure(0, weight=1)
    tk.Label(add_hdr, text="▸ ADD NEW PUROK",
             font=_font.font("Courier", 8, "bold"), fg=ACCENT, bg=CARD).grid(
                 row=0, column=0, sticky="w")

    # ── Location selection area ───────────────────────────────────────────────
    loc_frame = tk.Frame(add_card, bg=CARD)
    loc_frame.grid(row=1, column=0, sticky="ew", padx=16, pady=(10, 0))
    loc_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

    def make_label(parent, text, col):
        tk.Label(parent, text=text,
                 font=_font.font("Courier", 7, "bold"),
                 fg=MUTED, bg=CARD).grid(row=0, column=col, sticky="w", padx=(0, 6))

    make_label(loc_frame, "REGION",  0)
    make_label(loc_frame, "PROVINCE", 1)
    make_label(loc_frame, "CITY / MUNICIPALITY", 2)
    make_label(loc_frame, "BARANGAY",            3)

    region_var   = tk.StringVar(value="— select region —")
    province_var = tk.StringVar(value="— select province —")
    city_var     = tk.StringVar(value="— select city —")
    barangay_var = tk.StringVar(value="— select barangay —")

    def styled_combo(parent, textvariable, col):
        wrap = tk.Frame(parent, bg=PANEL,
                        highlightthickness=1, highlightbackground=BORDER)
        wrap.grid(row=1, column=col, sticky="ew", padx=(0, 6), pady=(4, 0))
        cb = ttk.Combobox(wrap, textvariable=textvariable,
                          state="readonly", style="Loc.TCombobox",
                          font=_font.font("Courier", 9))
        cb.pack(fill="x", padx=6, pady=5)
        cb.bind("<FocusIn>",  lambda e: wrap.config(highlightbackground=ACCENT))
        cb.bind("<FocusOut>", lambda e: wrap.config(highlightbackground=BORDER))
        return cb, wrap

    region_cb,   region_wrap   = styled_combo(loc_frame, region_var,   0)
    province_cb, province_wrap = styled_combo(loc_frame, province_var, 1)
    city_cb,     city_wrap     = styled_combo(loc_frame, city_var,     2)
    barangay_cb, barangay_wrap = styled_combo(loc_frame, barangay_var, 3)

    region_cb["values"]   = list(PH_LOCATIONS.keys())
    province_cb["values"] = []
    city_cb["values"]     = []
    barangay_cb["values"] = []

    # Location badge (shows chosen summary)
    badge_var = tk.StringVar(value="")
    badge_lbl = tk.Label(loc_frame, textvariable=badge_var,
                         font=_font.font("Courier", 8), fg=SUCCESS, bg=CARD,
                         anchor="w")
    badge_lbl.grid(row=2, column=0, columnspan=4, sticky="w", pady=(5, 0))

    def update_badge():
        r = region_var.get()
        p = province_var.get()
        c = city_var.get()
        b = barangay_var.get()
        parts = []
        if r and not r.startswith("—"): parts.append(r)
        if p and not p.startswith("—"): parts.append(p)
        if c and not c.startswith("—"): parts.append(c)
        if b and not b.startswith("—"): parts.append(b)
        badge_var.set("📍 " + " › ".join(parts) if parts else "")

    def on_region_change(event=None):
        region = region_var.get()
        provinces = list(PH_LOCATIONS.get(region, {}).keys())
        province_var.set("— select province —")
        city_var.set("— select city —")
        barangay_var.set("— select barangay —")
        province_cb["values"] = provinces
        city_cb["values"]     = []
        barangay_cb["values"] = []
        update_badge()

    def on_province_change(event=None):
        region   = region_var.get()
        province = province_var.get()
        cities   = list(PH_LOCATIONS.get(region, {}).get(province, {}).keys())
        city_var.set("— select city —")
        barangay_var.set("— select barangay —")
        city_cb["values"]     = cities
        barangay_cb["values"] = []
        update_badge()

    def on_city_change(event=None):
        region   = region_var.get()
        province = province_var.get()
        city     = city_var.get()
        brgys    = PH_LOCATIONS.get(region, {}).get(province, {}).get(city, [])
        barangay_var.set("— select barangay —")
        barangay_cb["values"] = brgys
        update_badge()

    def on_barangay_change(event=None):
        update_badge()

    region_cb.bind("<<ComboboxSelected>>",   on_region_change)
    province_cb.bind("<<ComboboxSelected>>", on_province_change)
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
             font=_font.font("Courier", 7, "bold"), fg=MUTED, bg=CARD).grid(
                 row=0, column=0, sticky="w", pady=(0, 4))

    name_input_row = tk.Frame(input_row, bg=CARD)
    name_input_row.grid(row=1, column=0, sticky="ew")
    name_input_row.grid_columnconfigure(0, weight=1)

    entry_wrap = tk.Frame(name_input_row, bg=PANEL,
                          highlightthickness=1, highlightbackground=BORDER)
    entry_wrap.grid(row=0, column=0, sticky="ew", padx=(0, 8))

    purok_entry = tk.Entry(entry_wrap, bg=PANEL, fg=TEXT,
                           font=_font.font("Courier", 10), relief="flat",
                           insertbackground=ACCENT, bd=0)
    purok_entry.pack(fill="x", padx=10, pady=7)

    def _entry_fi(e): entry_wrap.config(highlightbackground=ACCENT)
    def _entry_fo(e): entry_wrap.config(highlightbackground=BORDER)
    purok_entry.bind("<FocusIn>",  _entry_fi)
    purok_entry.bind("<FocusOut>", _entry_fo)

    add_btn = tk.Button(name_input_row, text="+ Add",
                        font=_font.font("Courier", 9, "bold"),
                        bg=ACCENT, fg="white",
                        activebackground="#3a7ce8", activeforeground="white",
                        relief="flat", bd=0, cursor="hand2")
    add_btn.grid(row=0, column=1, ipady=7, ipadx=14)

    # ── Open Residents button ─────────────────────────────────────────────────
    open_btn = tk.Button(wrapper,
                         text="OPEN RESIDENTS  →",
                         font=_font.font("Courier", 12, "bold"),
                         bg=SUCCESS, fg="#0d0f14",
                         activebackground="#3ab868", activeforeground="#0d0f14",
                         relief="flat", bd=0, cursor="hand2")
    open_btn.grid(row=7, column=0, sticky="ew", padx=36, pady=(0, 8), ipady=14)

    # ── Archived Puroks collapsible panel ─────────────────────────────────────
    archive_panel_visible = tk.BooleanVar(value=False)

    archive_toggle_btn = tk.Button(
        wrapper,
        text="📦  Show Archived Puroks  ▾",
        font=_font.font("Courier", 8, "bold"),
        bg=PANEL, fg=WARN,
        activebackground=BORDER, activeforeground=WARN,
        relief="flat", bd=0, cursor="hand2",
        anchor="w"
    )
    archive_toggle_btn.grid(row=8, column=0, sticky="ew", padx=36, pady=(0, 4), ipady=5)

    # The collapsible card — hidden by default
    arch_card = tk.Frame(wrapper, bg=CARD,
                         highlightthickness=1, highlightbackground=BORDER)
    arch_card.grid_columnconfigure(0, weight=1)

    arch_hdr = tk.Frame(arch_card, bg=CARD)
    arch_hdr.grid(row=0, column=0, columnspan=2, sticky="ew", padx=16, pady=(10, 6))
    arch_hdr.grid_columnconfigure(1, weight=1)
    tk.Label(arch_hdr, text="📦  ARCHIVED PUROKS",
             font=_font.font("Courier", 8, "bold"), fg=WARN, bg=CARD).grid(
                 row=0, column=0, sticky="w")
    arch_count_lbl = tk.Label(arch_hdr, text="0 archived",
                               font=_font.font("Courier", 8), fg=MUTED, bg=CARD)
    arch_count_lbl.grid(row=0, column=1, sticky="e")

    arch_scroll = tk.Scrollbar(arch_card, orient="vertical",
                                bg=BORDER, troughcolor=CARD,
                                width=6, relief="flat", highlightthickness=0)
    arch_scroll.grid(row=1, column=1, sticky="ns", pady=(0, 8))

    arch_tree = ttk.Treeview(arch_card,
                              columns=("ID", "Name", "Province", "City", "Barangay"),
                              show="headings",
                              style="Custom.Treeview",
                              height=4,
                              yscrollcommand=arch_scroll.set)
    arch_tree.heading("ID",       text="ID")
    arch_tree.heading("Name",     text="Purok Name")
    arch_tree.heading("Province", text="Province")
    arch_tree.heading("City",     text="City / Municipality")
    arch_tree.heading("Barangay", text="Barangay")
    arch_tree.column("ID",       width=40,  anchor="center", stretch=False)
    arch_tree.column("Name",     width=120, anchor="w",      stretch=True)
    arch_tree.column("Province", width=120, anchor="w",      stretch=True)
    arch_tree.column("City",     width=110, anchor="w",      stretch=True)
    arch_tree.column("Barangay", width=120, anchor="w",      stretch=True)
    arch_tree.grid(row=1, column=0, sticky="nsew", padx=(10, 0), pady=(0, 8))
    arch_scroll.config(command=arch_tree.yview)
    # Archive row colors (theme-aware)
    if cur_theme == "light":
        arch_odd  = "#f0e8d0"
        arch_even = "#e8e0c0"
    elif cur_theme == "forest":
        arch_odd  = "#1a2c1a"
        arch_even = "#152415"
    else:
        arch_odd  = "#1a1408"
        arch_even = "#141008"
    arch_tree.tag_configure("arch_odd",  background=arch_odd)
    arch_tree.tag_configure("arch_even", background=arch_even)

    tk.Label(arch_card,
             text="Right-click a row to Restore or Delete permanently",
             font=_font.font("Courier", 7), fg=MUTED, bg=CARD).grid(
                 row=2, column=0, columnspan=2, pady=(0, 10))

    # Footer
    tk.Label(wrapper,
             text="© Barangay Management System  ·  v1.0",
             font=_font.font("Courier", 8), fg=BORDER, bg=BG).grid(row=10, column=0, pady=(6, 14))

    # ── Logic ─────────────────────────────────────────────────────────────────
    _all_puroks_cache = []

    def filter_puroks(event=None):
        """Re-filter the treeview based on search text."""
        q = search_var.get().strip().lower()
        if not q:
            refresh_puroks()
            return
        for row in tree.get_children():
            tree.delete(row)
        matched = []
        for p in _all_puroks_cache:
            vals = [str(v).lower() for v in p[:5]]
            if any(q in v for v in vals):
                matched.append(p)
        for i, p in enumerate(matched):
            tag = "odd" if i % 2 == 0 else "even"
            if len(p) >= 5:
                tree.insert("", "end", values=p[:5], tags=(tag,))
            else:
                tree.insert("", "end",
                            values=(p[0], p[1], "—", "—", "—"), tags=(tag,))
        count_lbl.config(text=f"{len(matched)} of {len(_all_puroks_cache)} entr{'y' if len(matched)==1 else 'ies'}")

    search_entry.bind("<KeyRelease>", filter_puroks)

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
            arch_card.grid(row=9, column=0, sticky="ew", padx=36, pady=(0, 8))
            archive_panel_visible.set(True)
            archive_toggle_btn.config(text="📦  Hide Archived Puroks  ▴")
            refresh_archived()

    archive_toggle_btn.config(command=toggle_archive_panel)

    # Right-click menu for the archived tree
    arch_ctx = tk.Menu(root, tearoff=0,
                       bg=CARD, fg=TEXT,
                       activebackground=ACCENT, activeforeground="white",
                       font=_font.font("Courier", 9), relief="flat", bd=0)
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
        nonlocal _all_puroks_cache
        for row in tree.get_children():
            tree.delete(row)
        puroks = database.get_puroks()
        _all_puroks_cache = puroks[:]
        for i, p in enumerate(puroks):
            tag = "odd" if i % 2 == 0 else "even"
            # p may be (id, name) or (id, name, province, city, barangay)
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
        province = province_var.get()
        city     = city_var.get()
        barangay = barangay_var.get()

        if not name:
            messagebox.showwarning("Missing Name", "Please enter a Purok name.")
            return

        # Warn but don't block if location is incomplete
        if region.startswith("—") or province.startswith("—") or city.startswith("—") or barangay.startswith("—"):
            proceed = messagebox.askyesno(
                "Incomplete Location",
                "Location is not fully set.\nSave purok without full location?")
            if not proceed:
                return

        # Sanitise placeholder strings to empty
        reg_val = "" if region.startswith("—")      else region
        prv_val = "" if province.startswith("—")    else province
        cit_val = "" if city.startswith("—")        else city
        brg_val = "" if barangay.startswith("—")    else barangay

        database.add_purok(name, reg_val, prv_val, cit_val, brg_val)

        purok_entry.delete(0, tk.END)
        region_var.set("— select region —")
        province_var.set("— select province —")
        city_var.set("— select city —")
        barangay_var.set("— select barangay —")
        province_cb["values"] = []
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
        ui.run_app(purok_id, purok_name, admin_username=admin_username)

    # ── Right-click context menu ───────────────────────────────────────────────
    ctx_menu = tk.Menu(root, tearoff=0,
                       bg=CARD, fg=TEXT,
                       activebackground=ACCENT, activeforeground="white",
                       font=_font.font("Courier", 9),
                       relief="flat", bd=0)

    # Separator style
    ctx_menu.add_command(label="⚠  Delete Purok",  foreground="#ff5f5f",
                         activebackground="#7a1e1e", activeforeground="#ff5f5f",
                         command=lambda: _ctx_delete())
    ctx_menu.add_separator()
    ctx_menu.add_command(label="📦  Archive Purok", foreground=WARN,
                         activebackground="#4a3a00", activeforeground=WARN,
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