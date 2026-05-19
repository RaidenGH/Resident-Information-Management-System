import tkinter as tk
from tkinter import messagebox
import os
import threading
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
                       bg="#11141f", accent="#4f8ef7",
                       panel="#181c2a", border="#252c42",
                       text="#e8ecf4", muted="#6b7490",
                       success="#4fc97e", danger="#f74f6a"):
    """
    Opens a popup camera window.
    on_photo_taken(filepath) is called with the saved image path.
    """
    ensure_photos_dir()

    if not CV2_OK or not PIL_OK:
        messagebox.showerror(
            "Missing Libraries",
            "opencv-python and Pillow are required.\n"
            "Run: pip install opencv-python pillow"
        )
        return

    win = tk.Toplevel(parent)
    win.title("📷  Capture Photo")
    win.configure(bg=bg)
    win.geometry("520x460")
    win.resizable(False, False)
    win.grab_set()

    win.update_idletasks()
    sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
    win.geometry(f"520x460+{(sw-520)//2}+{(sh-460)//2}")

    # ── Top stripe ────────────────────────────────────────────────
    tk.Frame(win, bg=accent, height=3).pack(fill="x")

    # ── Header ────────────────────────────────────────────────────
    tk.Label(win, text="📷  CAPTURE RESIDENT PHOTO",
             font=("Courier", 10, "bold"),
             fg=accent, bg=bg).pack(pady=(12, 4))
    tk.Label(win, text="Position the resident in the frame and press Capture",
             font=("Courier", 8),
             fg=muted, bg=bg).pack()

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
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            feed_lbl.config(
                text="⚠ No camera found.\nConnect a webcam and try again.",
                fg=danger, font=("Courier", 10), compound="center")
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
                            font=("Courier", 9, "bold"),
                            relief="flat", bd=0, cursor="hand2")
    capture_btn.pack(side="left", padx=6, ipady=8, ipadx=16)

    retake_btn = tk.Button(btn_row, text="↺  Retake",
                           command=retake,
                           bg=panel, fg=muted,
                           activebackground=border,
                           font=("Courier", 9, "bold"),
                           relief="flat", bd=0, cursor="hand2",
                           state="disabled")
    retake_btn.pack(side="left", padx=6, ipady=8, ipadx=16)

    confirm_btn = tk.Button(btn_row, text="✓  Use This Photo",
                            command=confirm,
                            bg=panel, fg=muted,
                            activebackground=border,
                            font=("Courier", 9, "bold"),
                            relief="flat", bd=0, cursor="hand2",
                            state="disabled")
    confirm_btn.pack(side="left", padx=6, ipady=8, ipadx=16)

    tk.Button(btn_row, text="✕  Cancel",
              command=on_close,
              bg=panel, fg=danger,
              activebackground=border,
              font=("Courier", 9, "bold"),
              relief="flat", bd=0, cursor="hand2").pack(
                  side="left", padx=6, ipady=8, ipadx=16)

    status_lbl = tk.Label(win, text="", font=("Courier", 8),
                          fg=success, bg=bg)
    status_lbl.pack()

    # Start camera after window is ready
    win.after(200, start_camera)