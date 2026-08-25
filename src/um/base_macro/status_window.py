"""
Small always-on-top status overlay window using tkinter.

Thread safety
-------------
Tkinter itself is NOT thread-safe: widgets and StringVars must only be
touched from the thread running mainloop(). set_name()/set_state()/
set_details() are safe to call from ANY thread -- they just push the
update onto a queue.Queue(). The Tk main loop drains that queue on a
timer (via after()) and applies the changes on the correct thread.
"""

import queue
import tkinter as tk

from um.profiles import ProfileReader


# Claude generated
class StatusOverlay:
    def __init__(
        self,
        name="StatusOverlay",
        state="initializing",
        details="",
        width=ProfileReader.profile().macro_status_window_width,
        height=ProfileReader.profile().macro_status_window_height,
        corner=ProfileReader.profile().macro_status_window_corner,   # "top-left", "bottom-right", "bottom-left"
        margin_x=ProfileReader.profile().macro_status_window_margin_x,
        margin_y=ProfileReader.profile().macro_status_window_margin_y,
        bg=ProfileReader.profile().macro_status_window_bg,
        fg=ProfileReader.profile().macro_status_window_fg,
        accent=ProfileReader.profile().macro_status_window_accent,
        poll_ms=ProfileReader.profile().macro_status_window_refresh_ms,
    ):
        self.root = tk.Tk()
        self.root.title(name)

        # No title bar / borders, stays on top of other windows.
        # -topmost doesn't need admin rights on Windows, macOS, or Linux/X11.
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        try:
            # Cosmetic slight transparency; not supported everywhere, so ignore failures.
            self.root.attributes("-alpha", ProfileReader.profile().macro_status_window_alpha)
        except tk.TclError:
            pass

        self.root.configure(bg=bg)
        self._position(width, height, corner, margin_x, margin_y)

        # --- top row: name (left) + state (right) ---
        top = tk.Frame(self.root, bg=bg)
        top.pack(fill="x", padx=10, pady=(8, 4))

        self.name_var = tk.StringVar(value=name)
        self.state_var = tk.StringVar(value=state)

        self.name_label = tk.Label(
            top, textvariable=self.name_var, bg=bg, fg=fg,
            font=("Segoe UI", 11, "bold"), anchor="w",
        )
        self.name_label.pack(side="left")

        self.state_label = tk.Label(
            top, textvariable=self.state_var, bg=bg, fg=accent,
            font=("Segoe UI", 10, "bold"), anchor="e",
        )
        self.state_label.pack(side="right")

        sep = tk.Frame(self.root, bg="#3a3a3a", height=1)
        sep.pack(fill="x", padx=10, pady=(0, 4))

        # --- bottom: details, smaller font, multi-line, wraps ---
        self.details_var = tk.StringVar(value=details)
        self.details_label = tk.Label(
            self.root, textvariable=self.details_var, bg=bg, fg="#b5b5b5",
            font=("Segoe UI", 9), anchor="nw", justify="left",
            wraplength=width - 20,
        )
        self.details_label.pack(fill="both", expand=True, padx=10, pady=(0, 8))

        # No window manager decorations, so we implement dragging ourselves.
        draggable = (self.root, top, self.name_label, self.state_label, sep, self.details_label)
        for widget in draggable:
            widget.bind("<Button-1>", self._start_move)
            widget.bind("<B1-Motion>", self._on_move)
            widget.bind("<Button-3>", lambda e: self._close())  # right-click closes

        self.root.bind("<Escape>", lambda e: self._close())

        self._drag_data = {"x": 0, "y": 0}

        # --- thread-safe update queue ---
        self._updates = queue.Queue()
        self._poll_ms = poll_ms
        self.root.after(self._poll_ms, self._drain_queue)

    def _position(self, width, height, corner, margin_x, margin_y):
        self.root.update_idletasks()
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()

        if corner == "top-left":
            x, y = margin_x, margin_y
        elif corner == "bottom-right":
            x, y = screen_w - width - margin_x, screen_h - height - margin_y
        elif corner == "bottom-left":
            x, y = margin_x, screen_h - height - margin_y
        else:  # "top-right" default
            x, y = screen_w - width - margin_x, margin_y

        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def _start_move(self, event):
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def _on_move(self, event):
        x = self.root.winfo_x() + (event.x - self._drag_data["x"])
        y = self.root.winfo_y() + (event.y - self._drag_data["y"])
        self.root.geometry(f"+{x}+{y}")

    # --- queue draining, runs on the Tk main thread via after() ---
    def _drain_queue(self):
        try:
            while True:
                kind, value = self._updates.get_nowait()
                if kind == "name":
                    self.name_var.set(value)
                elif kind == "state":
                    self.state_var.set(value)
                elif kind == "details":
                    self.details_var.set(value)
                elif kind == "close":
                    self._close()
                    return  # don't reschedule, window is gone
        except queue.Empty:
            pass
        self.root.after(self._poll_ms, self._drain_queue)

    def _close(self):
        try:
            self.root.destroy()
        except tk.TclError:
            pass

    # --- public API: safe to call from any thread ---
    def set_name(self, text):
        self._updates.put(("name", text))

    def set_state(self, text):
        self._updates.put(("state", text))

    def set_details(self, text):
        self._updates.put(("details", text))

    def start(self):
        self.root.mainloop()

    def stop(self):
        self._updates.put(("close", None))


if __name__ == "__main__":
    import threading
    import time

    overlay = StatusOverlay(name="Backup Job", state="idle", details="Waiting to start...")

    def worker():
        # This runs on a background thread. It only ever calls set_state /
        # set_details / set_name, never touches Tk widgets directly.
        time.sleep(1)
        overlay.set_state("running")
        steps = [
            "Copying files (124/900)...",
            "Copying files (612/900)...",
            "Copying files (900/900)...",
        ]
        for step in steps:
            overlay.set_details(step)
            time.sleep(1.5)
        overlay.set_state("done")
        overlay.set_details("Backup complete.")

    threading.Thread(target=worker, daemon=True).start()
    overlay.start()  # mainloop() stays on the main thread, as it must
