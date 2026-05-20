import tkinter as tk
from tkinter import messagebox, filedialog
import os
import shutil
from datetime import datetime

try:
    import cv2
    CV2_OK = True
except ImportError:
    CV2_OK = False

try:
    from PIL import Image, ImageTk
    PIL_OK = True
except ImportError:
    PIL_OK = False

# Photos saved here (next to the app)
PHOTOS_DIR = "resident_photos"


def ensure_photos_dir():
    os.makedirs(PHOTOS_DIR, exist_ok=True)


def open_camera_window(parent, on_photo_taken,
                       bg=None, accent=None,
                       panel=None, border=None,
                       text=None, muted=None,
                       success=None, danger=None):
    """
    Opens a popup camera window.
    on_photo_taken(filepath) is called with the saved image path.
    """
    import theme as _t
    if bg is None: bg = _t.CARD
    if accent is None: accent = _t.ACCENT
    if panel is None: panel = _t.PANEL
    if border is None: border = _t.BORDER
    if text is None: text = _t.TEXT
    if muted is None: muted = _t.MUTED
    if success is None: success = _t.SUCCESS
    if danger is None: danger = _t.DANGER
    ensure_photos_dir()

    if not PIL_OK:
        messagebox.showerror(
            "Missing Libraries",
            "Pillow is required.\n"
            "Run: pip install pillow"
        )
        return

    win = tk.Toplevel(parent)
    win.title("📷  Capture Photo")
    win.configure(bg=bg)
    win.geometry("520x520")
    win.resizable(False, False)
    win.grab_set()

    win.update_idletasks()
    sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
    win.geometry(f"520x520+{(sw-520)//2}+{(sh-520)//2}")

    # ── Top stripe ────────────────────────────────────────────────
    tk.Frame(win, bg=accent, height=3).pack(fill="x")

    # ── Header row with Browse button on the right ───────────────
    header_row = tk.Frame(win, bg=bg)
    header_row.pack(fill="x", padx=20, pady=(12, 4))
    header_row.grid_columnconfigure(0, weight=1)

    # Title labels (left side)
    title_frame = tk.Frame(header_row, bg=bg)
    title_frame.grid(row=0, column=0, sticky="w")
    tk.Label(title_frame, text="📷  CAPTURE RESIDENT PHOTO",
             font=_t.font("Courier", 10, "bold"),
             fg=accent, bg=bg).pack(anchor="w")
    tk.Label(title_frame, text="Position the resident in the frame and press Capture",
             font=_t.font("Courier", 8),
             fg=muted, bg=bg).pack(anchor="w")

    # Browse button (upper right)
    def browse_photo():
        file_path = filedialog.askopenfilename(
            parent=win,
            title="Select Resident Photo",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.bmp *.gif *.webp"),
                ("JPEG", "*.jpg *.jpeg"),
                ("PNG", "*.png"),
                ("All files", "*.*")
            ]
        )
        if not file_path:
            return  # User cancelled

        # Stop camera if running
        stop_camera()

        # Copy to resident_photos folder with timestamp
        ext = os.path.splitext(file_path)[1].lower() or ".jpg"
        fname = f"resident_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
        dest_path = os.path.join(PHOTOS_DIR, fname)

        try:
            shutil.copy2(file_path, dest_path)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy file:\n{e}")
            return

        # Show preview in feed area
        try:
            img = Image.open(dest_path).resize((CAM_W, CAM_H))
            imgtk = ImageTk.PhotoImage(img)
            feed_lbl.config(image=imgtk, text="")
            feed_lbl._img = imgtk
        except Exception:
            feed_lbl.config(text="📁  Photo loaded", fg=accent,
                           font=_t.font("Courier", 14, "bold"), compound="center")

        _state["captured"] = True
        _state["capture_path"] = dest_path

        capture_btn.config(state="disabled", bg=muted)
        retake_btn.config(state="normal",  bg="#d9903a")
        confirm_btn.config(state="normal",  bg=success)

        status_lbl.config(text=f"✓ Photo loaded: {os.path.basename(file_path)}", fg=success)

    browse_btn = tk.Button(header_row, text="📁  Browse",
                           command=browse_photo,
                           bg=panel, fg=accent,
                           activebackground=border,
                           activeforeground="white",
                           font=_t.font("Courier", 8, "bold"),
                           relief="flat", bd=0, cursor="hand2",
                           highlightthickness=1, highlightbackground=border,
                           padx=10, pady=4)
    browse_btn.grid(row=0, column=1, sticky="e")

    # ── Camera feed ───────────────────────────────────────────────
    feed_frame = tk.Frame(win, bg=panel,
                          highlightthickness=1, highlightbackground=border)
    feed_frame.pack(padx=20, pady=12)

    CAM_W, CAM_H = 460, 320
    feed_lbl = tk.Label(feed_frame, bg=panel,
                        width=CAM_W, height=CAM_H)
    feed_lbl.pack()

    # State
    _state = {
        "cap":         None,
        "running":     False,
        "last_frame":  None,
        "captured":    False,
    }

    # ── Start camera ──────────────────────────────────────────────
    def start_camera():
        if not CV2_OK:
            feed_lbl.config(
                text="⚠ No camera found.\nConnect a webcam and try again.",
                fg=danger, font=_t.font("Courier", 10), compound="center")
            return
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            feed_lbl.config(
                text="⚠ No camera found.\nConnect a webcam and try again.",
                fg=danger, font=_t.font("Courier", 10), compound="center")
            return
        _state["cap"] = cap
        _state["running"] = True
        _update_feed()

    def _update_feed():
        if not _state["running"]:
            return
        cap = _state["cap"]
        if cap is None:
            return
        ret, frame = cap.read()
        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            _state["last_frame"] = frame
            img = Image.fromarray(frame_rgb).resize((CAM_W, CAM_H))
            imgtk = ImageTk.PhotoImage(img)
            feed_lbl.config(image=imgtk, text="")
            feed_lbl._img = imgtk
        win.after(30, _update_feed)

    def stop_camera():
        _state["running"] = False
        if _state["cap"]:
            _state["cap"].release()
            _state["cap"] = None

    # ── Capture ───────────────────────────────────────────────────
    def capture():
        frame = _state["last_frame"]
        if frame is None:
            messagebox.showwarning("No Frame", "Camera not ready yet.")
            return

        fname = f"resident_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        fpath = os.path.join(PHOTOS_DIR, fname)
        cv2.imwrite(fpath, frame)

        # Show frozen captured frame
        _state["running"] = False
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb).resize((CAM_W, CAM_H))
        imgtk = ImageTk.PhotoImage(img)
        feed_lbl.config(image=imgtk)
        feed_lbl._img = imgtk

        _state["captured"] = True
        _state["capture_path"] = fpath

        capture_btn.config(state="disabled", bg=muted)
        retake_btn.config(state="normal",  bg="#d9903a")
        confirm_btn.config(state="normal",  bg=success)

        status_lbl.config(text=f"✓ Photo saved: {fname}", fg=success)

    def retake():
        _state["captured"] = False
        _state["capture_path"] = None
        capture_btn.config(state="normal", bg=accent)
        retake_btn.config(state="disabled", bg=panel)
        confirm_btn.config(state="disabled", bg=panel)
        status_lbl.config(text="", fg=muted)
        _state["running"] = True
        _update_feed()

    def confirm():
        path = _state.get("capture_path", "")
        stop_camera()
        win.destroy()
        if path:
            on_photo_taken(path)

    def on_close():
        stop_camera()
        win.destroy()

    win.protocol("WM_DELETE_WINDOW", on_close)

    # ── Buttons ───────────────────────────────────────────────────
    btn_row = tk.Frame(win, bg=bg)
    btn_row.pack(pady=4)

    capture_btn = tk.Button(btn_row, text="📷  Capture",
                            command=capture,
                            bg=accent, fg="white",
                            activebackground="#3a7ce8",
                            font=_t.font("Courier", 9, "bold"),
                            relief="flat", bd=0, cursor="hand2")
    capture_btn.pack(side="left", padx=6, ipady=8, ipadx=16)

    retake_btn = tk.Button(btn_row, text="↺  Retake",
                           command=retake,
                           bg=panel, fg=muted,
                           activebackground=border,
                           font=_t.font("Courier", 9, "bold"),
                           relief="flat", bd=0, cursor="hand2",
                           state="disabled")
    retake_btn.pack(side="left", padx=6, ipady=8, ipadx=16)

    confirm_btn = tk.Button(btn_row, text="✓  Use This Photo",
                            command=confirm,
                            bg=panel, fg=muted,
                            activebackground=border,
                            font=_t.font("Courier", 9, "bold"),
                            relief="flat", bd=0, cursor="hand2",
                            state="disabled")
    confirm_btn.pack(side="left", padx=6, ipady=8, ipadx=16)

    tk.Button(btn_row, text="✕  Cancel",
              command=on_close,
              bg=panel, fg=danger,
              activebackground=border,
              font=_t.font("Courier", 9, "bold"),
              relief="flat", bd=0, cursor="hand2").pack(
                  side="left", padx=6, ipady=8, ipadx=16)

    status_lbl = tk.Label(win, text="", font=_t.font("Courier", 8),
                          fg=success, bg=bg)
    status_lbl.pack(pady=(4, 0))

    # Start camera after window is ready
    win.after(200, start_camera)