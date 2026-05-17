import tkinter as tk


# ─────────────────────────────────────────────────────────────────
#  draw_logo(parent, x, y, scale=1.0)
#
#  Draws the RIMS logo onto any tkinter Canvas at position (x, y).
#  Returns the Canvas widget so you can pack/grid it yourself.
#
#  Standalone usage:
#      canvas = make_logo_canvas(parent)
#      canvas.pack()
#
#  Inline usage inside an existing canvas:
#      draw_logo(existing_canvas, x=20, y=20, scale=0.8)
# ─────────────────────────────────────────────────────────────────

ACCENT  = "#4f8ef7"
ACCENT2 = "#7c5cfc"
SUCCESS = "#4fc97e"
BG      = "#0d0f14"
CARD    = "#13161e"
BORDER  = "#2a2f42"
TEXT    = "#e8ecf4"
MUTED   = "#6b7490"
PANEL   = "#1a1e2b"


def draw_logo(canvas, x=0, y=0, scale=1.0):
    """Draw the RIMS logo onto an existing canvas at offset (x, y)."""

    def s(v):
        return v * scale

    ox, oy = x, y  # origin offset

    def p(px, py):
        return ox + s(px), oy + s(py)

    # ── Outer hexagon ──────────────────────────────────────────────
    hex_pts_outer = [
        ox + s(42),  oy + s(0),
        ox + s(84),  oy + s(24),
        ox + s(84),  oy + s(72),
        ox + s(42),  oy + s(96),
        ox + s(0),   oy + s(72),
        ox + s(0),   oy + s(24),
    ]
    canvas.create_polygon(hex_pts_outer, fill="", outline=BORDER, width=max(1, int(1.5*scale)))

    # ── Inner hexagon ──────────────────────────────────────────────
    hex_pts_inner = [
        ox + s(42),  oy + s(12),
        ox + s(76),  oy + s(30),
        ox + s(76),  oy + s(66),
        ox + s(42),  oy + s(84),
        ox + s(8),   oy + s(66),
        ox + s(8),   oy + s(30),
    ]
    canvas.create_polygon(hex_pts_inner, fill=CARD, outline=BORDER, width=max(1, int(scale)))

    # ── Grid lines inside hex ──────────────────────────────────────
    grid_color = BORDER
    for ly in [s(42), s(54), s(66)]:
        canvas.create_line(ox + s(15), oy + ly,
                           ox + s(69), oy + ly,
                           fill=grid_color, width=1)

    # ── Connector lines between nodes ─────────────────────────────
    node_coords = {
        "top":    p(42, 30),
        "ml":     p(27, 24),
        "mr":     p(57, 24),
        "cl":     p(27, 54),
        "cr":     p(57, 54),
        "bot":    p(42, 66),
    }
    connections = [
        ("ml", "top"), ("top", "mr"),
        ("ml", "cl"),  ("mr", "cr"),
        ("cl", "bot"), ("cr", "bot"),
        ("top", "bot"),
        ("cl",  "cr"),
    ]
    for a, b in connections:
        canvas.create_line(*node_coords[a], *node_coords[b],
                           fill=BORDER, width=max(1, int(scale)))

    # ── Node dots ──────────────────────────────────────────────────
    def dot(coord_key, color, r=5):
        cx, cy = node_coords[coord_key]
        r = s(r)
        canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill=color, outline="")

    dot("top", ACCENT,  5)
    dot("ml",  ACCENT,  3.5)
    dot("mr",  ACCENT,  3.5)
    dot("cl",  ACCENT2, 3.5)
    dot("cr",  ACCENT2, 3.5)
    dot("bot", SUCCESS, 5)

    # Corner pips
    for px, py, col in [(84, 24, ACCENT), (0, 72, SUCCESS)]:
        cx, cy = ox + s(px), oy + s(py)
        r = s(4)
        canvas.create_oval(cx-r, cy-r, cx+r, cy+r,
                           fill=col, outline="", stipple="gray50")

    # ── Vertical divider ──────────────────────────────────────────
    divx = ox + s(100)
    canvas.create_line(divx, oy + s(4), divx, oy + s(92),
                       fill=BORDER, width=1)

    # ── "RIMS" wordmark ───────────────────────────────────────────
    wx = ox + s(112)
    wy = oy + s(60)
    fs = max(10, int(36 * scale))

    canvas.create_text(wx, wy,
                       text="R",
                       font=("Georgia", fs, "bold"),
                       fill=TEXT, anchor="w")

    r_width = int(fs * 0.68)
    canvas.create_text(wx + r_width, wy,
                       text="I",
                       font=("Georgia", fs, "bold italic"),
                       fill=ACCENT, anchor="w")

    i_width = int(fs * 0.38)
    canvas.create_text(wx + r_width + i_width, wy,
                       text="MS",
                       font=("Georgia", fs, "bold"),
                       fill=TEXT, anchor="w")

    # Accent underline
    canvas.create_line(wx, oy + s(68),
                       wx + s(160), oy + s(68),
                       fill=ACCENT, width=max(1, int(2*scale)))

    # ── Subtitle ──────────────────────────────────────────────────
    sub_fs = max(7, int(8 * scale))
    canvas.create_text(wx, oy + s(80),
                       text="RESIDENT INFORMATION MANAGEMENT SYSTEM",
                       font=("Courier", sub_fs),
                       fill=MUTED, anchor="w")

    # ── Bottom badge ──────────────────────────────────────────────
    badge_y = oy + s(108)
    badge_x = ox + s(0)

    # Separator line
    canvas.create_line(badge_x, badge_y - s(6),
                       badge_x + s(340), badge_y - s(6),
                       fill=PANEL, width=1)

    # Badge rect
    canvas.create_rectangle(badge_x, badge_y,
                             badge_x + s(158), badge_y + s(20),
                             fill=CARD, outline=BORDER, width=1)
    canvas.create_text(badge_x + s(79), badge_y + s(10),
                       text="BARANGAY EDITION  v1.0",
                       font=("Courier", max(6, int(7*scale))),
                       fill=ACCENT, anchor="center")

    # Palette dots
    for i, col in enumerate([ACCENT, ACCENT2, SUCCESS]):
        dx = badge_x + s(170 + i * 16)
        dy = badge_y + s(10)
        r  = s(5)
        canvas.create_oval(dx-r, dy-r, dx+r, dy+r, fill=col, outline="")

    # Tagline
    canvas.create_text(badge_x + s(230), badge_y + s(10),
                       text="CLEAN · EFFICIENT · CONNECTED",
                       font=("Courier", max(6, int(7*scale))),
                       fill=BORDER, anchor="w")


def make_logo_canvas(parent, scale=1.0, bg=BG):
    """
    Creates a self-contained Canvas with the logo drawn on it.
    Returns the canvas — caller is responsible for pack/grid/place.

    Example:
        logo = make_logo_canvas(root, scale=1.0)
        logo.pack(pady=10)
    """
    w = int(400 * scale)
    h = int(140 * scale)
    c = tk.Canvas(parent, width=w, height=h, bg=bg, highlightthickness=0)
    draw_logo(c, x=int(20*scale), y=int(16*scale), scale=scale)
    return c


# ── Demo / preview ────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Logo Preview")
    root.configure(bg=BG)
    root.geometry("480x520")

    tk.Label(root, text="scale = 1.0", font=("Courier", 9),
             fg=MUTED, bg=BG).pack(pady=(16, 2))
    make_logo_canvas(root, scale=1.0).pack(padx=20)

    tk.Frame(root, bg=BORDER, height=1).pack(fill="x", padx=20, pady=10)

    tk.Label(root, text="scale = 0.75", font=("Courier", 9),
             fg=MUTED, bg=BG).pack(pady=(4, 2))
    make_logo_canvas(root, scale=0.75).pack(padx=20)

    tk.Frame(root, bg=BORDER, height=1).pack(fill="x", padx=20, pady=10)

    tk.Label(root, text="scale = 0.55  (sidebar size)", font=("Courier", 9),
             fg=MUTED, bg=BG).pack(pady=(4, 2))
    make_logo_canvas(root, scale=0.55).pack(padx=20)

    root.mainloop()