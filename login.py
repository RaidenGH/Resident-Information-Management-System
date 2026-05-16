import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import users_database
import database
from purok import run_purok_window
import register
from datetime import datetime
import platform

# Windows-specific imports for taskbar fix
if platform.system() == "Windows":
    import ctypes
    from ctypes import wintypes

def _set_app_user_model_id(app_id: str):
    """
    Set an explicit AppUserModelID for the current process (Windows).
    This helps Windows show the taskbar icon and group windows correctly.
    Safe no-op on non-Windows platforms.
    """
    if platform.system() != "Windows":
        return
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
    except Exception:
        pass

def _ensure_taskbar_entry(win):
    """
    On Windows, a window created with overrideredirect(True) may not show in the taskbar.
    This function adjusts the extended window style to include WS_EX_APPWINDOW and
    remove WS_EX_TOOLWINDOW so the window appears in the taskbar.
    Safe no-op on non-Windows platforms.
    """
    if platform.system() != "Windows":
        return

    try:
        GWL_EXSTYLE = -20
        WS_EX_APPWINDOW = 0x00040000
        WS_EX_TOOLWINDOW = 0x00000080
        SWP_NOSIZE = 0x0001
        SWP_NOMOVE = 0x0002
        SWP_NOZORDER = 0x0004
        SWP_FRAMECHANGED = 0x0020

        hwnd = win.winfo_id()
        # Get current extended style
        ex_style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        # Add APPWINDOW, remove TOOLWINDOW
        new_ex_style = (ex_style | WS_EX_APPWINDOW) & (~WS_EX_TOOLWINDOW)
        ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, new_ex_style)
        # Apply the style change so taskbar updates
        ctypes.windll.user32.SetWindowPos(hwnd, 0, 0, 0, 0, 0,
                                          SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER | SWP_FRAMECHANGED)
    except Exception:
        # Silently ignore errors so behavior remains unchanged on other systems
        pass

def run_login():
    # Initialize both sets of tables
    users_database.create_users_table()   # login accounts
    database.create_tables()              # residents & puroks

    # On Windows, set an explicit AppUserModelID for proper taskbar behavior
    if platform.system() == "Windows":
        _set_app_user_model_id("com.yourcompany.residentinfo")  # change string if you want a custom id

    root = tk.Tk()
    root.title("Resident Information Management System")
    root.configure(bg="#1b1b1b")
    root.resizable(False, False)

    # --- Remove default window border (Steam style) ---
    root.overrideredirect(True)

    # --- Center the window on screen ---
    window_width, window_height = 700, 440
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    # Ensure geometry is applied before manipulating native window styles
    root.update_idletasks()

    # --- Force taskbar visibility (Windows) ---
    # Adjust native window styles so the borderless window still shows in the taskbar.
    _ensure_taskbar_entry(root)

    # --- Soft border frame (3D look) ---
    border_frame = tk.Frame(root, bg="#1b1b1b",
                            highlightbackground="#d9d9d9",
                            highlightthickness=3,
                            relief="ridge")
    border_frame.pack(fill="both", expand=True)

    # --- Make window draggable by the border frame ---
    def start_move(event):
        # store the offset of the pointer relative to the window top-left
        root._drag_start_x = event.x
        root._drag_start_y = event.y

    def do_move(event):
        # compute new top-left coordinates and move the window
        dx = event.x - root._drag_start_x
        dy = event.y - root._drag_start_y
        new_x = root.winfo_x() + dx
        new_y = root.winfo_y() + dy
        root.geometry(f"+{new_x}+{new_y}")

    border_frame.bind("<ButtonPress-1>", start_move)
    border_frame.bind("<B1-Motion>", do_move)

    # --- Custom close button (inside window) ---
    close_btn = tk.Button(border_frame, text="✕", command=root.destroy,
                          bg="#1b1b1b", fg="white", font=("Arial", 12, "bold"),
                          relief="flat", bd=0, activebackground="red", activeforeground="white",
                          cursor="hand2")
    close_btn.place(x=window_width - 30, y=5, width=25, height=25)

    # --- Header ---
    header_frame = tk.Frame(border_frame, bg="#1b1b1b")
    header_frame.place(x=30, y=20)

    try:
        icon_img = Image.open("images/hcdc_logo.png")
        icon_img = icon_img.resize((40, 40), Image.LANCZOS)
        icon = ImageTk.PhotoImage(icon_img)
        lbl_icon = tk.Label(header_frame, image=icon, bg="#1b1b1b")
        lbl_icon.image = icon
        lbl_icon.pack(side="left", padx=(0, 10))
    except Exception:
        tk.Label(header_frame, text="🏠", font=("Arial", 24), fg="white", bg="#1b1b1b").pack(side="left", padx=(0, 10))

    tk.Label(header_frame, text="Resident Information Management System",
             font=("Poppins", 16, "bold"), fg="white", bg="#1b1b1b").pack(side="left")

    # --- Left login section ---
    left_frame = tk.Frame(border_frame, bg="#1b1b1b")
    left_frame.place(x=40, y=100)

    tk.Label(left_frame, text="SIGN IN WITH ACCOUNT NAME",
             font=("Poppins", 9, "bold"), fg="#00aaff", bg="#1b1b1b").pack(anchor="w")

    username_entry = tk.Entry(left_frame, bg="#2b2b2b", fg="white",
                              font=("Poppins", 10), relief="flat", insertbackground="white")
    username_entry.pack(anchor="w", pady=(5, 15), ipady=5, ipadx=150)

    tk.Label(left_frame, text="PASSWORD",
             font=("Poppins", 9, "bold"), fg="#00aaff", bg="#1b1b1b").pack(anchor="w")

    password_entry = tk.Entry(left_frame, bg="#2b2b2b", fg="white",
                              font=("Poppins", 10), show="*", relief="flat", insertbackground="white")
    password_entry.pack(anchor="w", pady=(5, 10), ipady=5, ipadx=150)

    remember_var = tk.BooleanVar()
    tk.Checkbutton(left_frame, text="Remember me", variable=remember_var,
                   font=("Poppins", 9), fg="white", bg="#1b1b1b",
                   activebackground="#1b1b1b", activeforeground="white",
                   selectcolor="#1b1b1b").pack(anchor="w", pady=(5, 10))

    # --- Hover animation ---
    def on_hover(btn, color): btn.config(bg=color)
    def on_leave(btn, color): btn.config(bg=color)

    # Login button
    def login(event=None):
        username = username_entry.get().strip()
        password = password_entry.get().strip()
        if not username or not password:
            messagebox.showwarning("Error", "Please fill in both fields.")
            return
        if users_database.validate_login(username, password):
            messagebox.showinfo("Login Successful", f"Welcome, {username}!")
            root.destroy()
            run_purok_window()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    login_btn = tk.Button(left_frame, text="Sign in", command=login,
                          bg="#00aaff", fg="white", font=("Poppins", 10, "bold"),
                          activebackground="#33bbff", activeforeground="white",
                          relief="flat", bd=0, cursor="hand2")
    login_btn.pack(anchor="w", pady=(10, 10), ipadx=100, ipady=5)
    login_btn.bind("<Enter>", lambda e: on_hover(login_btn, "#33bbff"))
    login_btn.bind("<Leave>", lambda e: on_leave(login_btn, "#00aaff"))

    # --- Right section: System Overview (live data + last sync date only) ---
    right_frame = tk.Frame(border_frame, bg="#1b1b1b", highlightbackground="#2b2b2b", highlightthickness=1)
    right_frame.place(x=420, y=100, width=230, height=220)

    tk.Label(right_frame, text="SYSTEM OVERVIEW",
             font=("Poppins", 10, "bold"), fg="#00aaff", bg="#1b1b1b").pack(anchor="center", pady=(10, 5))

    total_residents = database.count_residents()
    total_puroks = database.count_puroks()
    pending_updates = 0  # placeholder until you add update tracking
    last_sync = datetime.now().strftime("%b %d, %Y")  # date only

    overview_items = [
        ("Total Residents", str(total_residents)),
        ("Registered Puroks", str(total_puroks)),
        ("Pending Updates", str(pending_updates)),
        ("Last Sync", last_sync)
    ]

    for label, value in overview_items:
        item_frame = tk.Frame(right_frame, bg="#1b1b1b")
        item_frame.pack(anchor="w", pady=3, padx=20)
        tk.Label(item_frame, text=f"{label}:", font=("Poppins", 9), fg="white", bg="#1b1b1b").pack(side="left")
        tk.Label(item_frame, text=value, font=("Poppins", 9, "bold"), fg="#00aaff", bg="#1b1b1b").pack(side="left", padx=(5, 0))

    # --- Footer ---
    footer_frame = tk.Frame(border_frame, bg="#1b1b1b")
    footer_frame.place(x=40, y=380)

    tk.Label(footer_frame, text="Don't have an account?",
             font=("Poppins", 9), fg="white", bg="#1b1b1b").pack(side="left")

    create_btn = tk.Button(footer_frame, text="Create Account",
                           command=lambda: [root.destroy(), register.run_register(run_login)],
                           bg="#1b1b1b", fg="#00aaff", font=("Poppins", 9, "bold"),
                           activebackground="#00aaff", activeforeground="white",
                           relief="flat", bd=0, cursor="hand2")
    create_btn.pack(side="left", padx=(5, 0))
    create_btn.bind("<Enter>", lambda e: on_hover(create_btn, "#00aaff"))
    create_btn.bind("<Leave>", lambda e: on_leave(create_btn, "#1b1b1b"))

    # --- Debug: print and briefly display the native window handle (winfo_id) ---
    try:
        hwnd = root.winfo_id()
        print(f"[DEBUG] Window handle (winfo_id): {hwnd}")
        # Briefly show a small non-intrusive label with the hwnd so you can confirm the native handle
        if platform.system() == "Windows":
            debug_lbl = tk.Label(border_frame, text=f"hwnd: {hwnd}", font=("Poppins", 8),
                                 fg="#bbbbbb", bg="#1b1b1b")
            # place near bottom-right inside the window without altering main UI layout
            debug_lbl.place(x=window_width - 180, y=window_height - 22)
            # remove after 4 seconds
            root.after(4000, debug_lbl.destroy)
    except Exception:
        pass

    password_entry.bind("<Return>", login)
    root.mainloop()
