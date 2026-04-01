import tkinter as tk
from collections.abc import Callable
from tkinter import ttk


from PIL import Image, ImageTk


# ChatGPT generated
# not feeling like even touching this
class PreviewWindow(tk.Tk):
    def __init__(self, image: Image.Image, on_text_submitted: Callable[[str], None]):
        super().__init__()

        self.title("Image Viewer")

        # --- Window geometry ---
        self.window_width = 300
        self.window_height = 200
        self.geometry(f"{self.window_width}x{self.window_height}+{1920 - self.window_width}+{980 - self.window_height}")

        # --- Store original image ---
        self._original_image = image
        self._photo = None

        # --- Top: number inputs ---
        top_frame = ttk.Frame(self)
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        self.number_vars: list[tk.IntVar] = []
        for i in range(4):
            var = tk.IntVar(value=100)
            entry = ttk.Entry(top_frame, textvariable=var, width=6)
            entry.pack(side=tk.LEFT, padx=2)
            self.number_vars.append(var)

        # --- Middle: image ---
        self.image_label = ttk.Label(self)
        self.image_label.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)

        # --- Bottom: string input ---
        bottom_frame = ttk.Frame(self)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)

        self.text_var = tk.StringVar()
        self.text_entry = ttk.Entry(bottom_frame, textvariable=self.text_var)
        self.text_entry.pack(fill=tk.X)

        # --- Initial render ---
        self._update_image()

        # --- Resize handling ---
        self.bind("<Configure>", self._on_resize)
        # qol moving via keys
        self.bind("<Up>", lambda _: self.number_vars[1].set(self.get_number(1) - 10))
        self.bind("<Down>", lambda _: self.number_vars[1].set(self.get_number(1) + 10))
        self.bind("<Left>", lambda _: self.number_vars[0].set(self.get_number(0) - 10))
        self.bind("<Right>", lambda _: self.number_vars[0].set(self.get_number(0) + 10))

        self.text_entry.bind("<Return>", lambda _: on_text_submitted(self.text_var.get()))
    # ---------- Internal helpers ----------

    def _on_resize(self, event):
        if event.widget is self:
            self._update_image()

    def _update_image(self):
        if not self._original_image:
            return

        label_width = self.image_label.winfo_width()
        label_height = self.image_label.winfo_height()

        if label_width <= 1 or label_height <= 1:
            return

        img = self._original_image.copy()
        img.thumbnail((label_width, label_height), Image.LANCZOS)

        self._photo = ImageTk.PhotoImage(img)
        self.image_label.configure(image=self._photo)

    # ---------- Public API ----------

    def set_image(self, image: Image.Image):
        """Replace the displayed image."""
        self._original_image = image
        self._update_image()

    def get_number(self, index: int) -> int:
        """Return a single numeric input as float or None."""
        try:
            return int(self.number_vars[index].get())
        except Exception:
            return 1

    def get_all_numbers(self) -> list[int]:
        """Return all 4 numeric inputs."""
        values:list[int] = [self.get_number(q) for q in range(4)]
        return values

    def get_text(self):
        """Return the bottom string input."""
        return self.text_var.get()
