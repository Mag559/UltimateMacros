import tkinter as tk


# Claude generated
class StatusOverlay:
    def __init__(
        self,
        name="StatusOverlay",
        state="initializing",
        details="",
        width=280,
        height=140,
        corner="bottom-left",   # "top-left", "bottom-right", "bottom-left"
        margin=5,
        bg="#1e1e1e",
        fg="#e6e6e6",
        accent="#5fb0ff",
    ):
        self.root = tk.Tk()
        self.root.title(name)

        # No title bar / borders, stays on top of other windows.
        # -topmost doesn't need admin rights on Windows, macOS, or Linux/X11.
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        try:
            # Cosmetic slight transparency; not supported everywhere, so ignore failures.
            self.root.attributes("-alpha", 0.95)
        except tk.TclError:
            pass

        self.root.configure(bg=bg)
        self._position(width, height, corner, margin)

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
            widget.bind("<Button-3>", lambda e: self.root.destroy())  # right-click closes

        self.root.bind("<Escape>", lambda e: self.root.destroy())

        self._drag_data = {"x": 0, "y": 0}

    def _position(self, width, height, corner, margin):
        self.root.update_idletasks()
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()

        if corner == "top-left":
            x, y = margin, margin
        elif corner == "bottom-right":
            x, y = screen_w - width - margin, screen_h - height - margin
        elif corner == "bottom-left":
            x, y = margin, screen_h - height - margin
        else:  # "top-right" default
            x, y = screen_w - width - margin, margin

        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def _start_move(self, event):
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def _on_move(self, event):
        x = self.root.winfo_x() + (event.x - self._drag_data["x"])
        y = self.root.winfo_y() + (event.y - self._drag_data["y"])
        self.root.geometry(f"+{x}+{y}")

    # --- public API for updating live from your own code ---
    def set_name(self, text):
        self.name_var.set(text)

    def set_state(self, text):
        self.state_var.set(text)

    def set_details(self, text):
        self.details_var.set(text)

    def start(self):
        self.root.mainloop()

    def stop(self):
        try:
            self.root.destroy()
        except tk.TclError:
            pass


if __name__ == "__main__":
    overlay = StatusOverlay(name="Backup Job", state="running", details="Copying files (124/900)...")

    # Demo: cycle through a few states using tkinter's own event loop (after()),
    # so you can see how set_state()/set_details() work without threads.
    demo_steps = [
        ("running", "Copying files (124/900)..."),
        ("running", "Copying files (612/900)..."),
        ("paused", "Waiting for network..."),
        ("running", "Copying files (900/900)..."),
        ("done", "Backup complete."),
    ]

    def advance(i=0):
        if i < len(demo_steps):
            state, details = demo_steps[i]
            overlay.set_state(state)
            overlay.set_details(details)
            overlay.root.after(2000, advance, i + 1)

    overlay.root.after(2000, advance)
    overlay.start()
