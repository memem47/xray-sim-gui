"""
Minimul Tkinter GUI for the X-ray simulator.

Responsibilities:
- Provides two sliders: Tube current (mA) and Tube voltage (kVp)
- Call simulator.simulate(mA, kVp) and render the resulting image
- Save PNG, Reset controls
- Keep the physics isolated from the UI

Run:
    python -m src.app.gui
"""
from __future__ import annotations
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Optional
import numpy as np
from PIL import Image, ImageTk

from src.simulator import simulate

WINDOW_TITLE = "X-ray Simulator (Minimal)"
DEFAULT_MA = 200.0
DEFAULT_KVP = 70.0
IMG_SIZE = (256, 256)

class XRayApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(WINDOW_TITLE)
        
        # --- State (tk variables) ---
        self.var_mA = tk.DoubleVar(value=DEFAULT_MA)
        self.var_kVp = tk.DoubleVar(value=DEFAULT_KVP)

        # Debounce handle for slider drags
        self._after_id: Optional[str] = None

        # Last rendered PIL image / Tk image
        self._last_pil: Optional[Image.Image] = None
        self._last_tk: Optional[ImageTk.PhotoImage] = None

        # --- Layout ---
        root = ttk.Frame(self, padding=8)
        root.pack(fill="both", expand=True)

        left = ttk.Frame(root)
        left.pack(side="left", fill="y")

        right = ttk.Frame(root)
        right.pack(side="left", fill="both", expand=True, padx=(8, 0))

        # Controls (use tk.Scale to allow 'resolution' reliably on Windows)
        ttk.Label(left, text="Tube current (mA):").pack(anchor="w")
        tk.Scale(left, from_=10, to=500, resolution=1, orient=tk.HORIZONTAL,
                 length=220, variable=self.var_mA, command=self._on_slider).pack()
        
        ttk.Label(left, text="Tube voltage (kVp):").pack(anchor="w", pady=(8, 0))
        tk.Scale(left, from_=40, to=120, resolution=1, orient=tk.HORIZONTAL,
                 length=220, variable=self.var_kVp, command=self._on_slider).pack()
        
        # Buttons
        btns = ttk.Frame(left)
        btns.pack(anchor="w", pady=(12, 0))
        ttk.Button(btns, text="Reset", command=self.reset_params).grid(row=0, column=0, padx=(0, 6))
        ttk.Button(btns, text="Save PNG", command=self.save_png).grid(row=0, column=1)
        
        # Preview area
        self.preview = ttk.Label(right) # will hold a PhotoImage
        self.preview.pack(fill="both", expand=True)

        # Status bar
        self.status = ttk.Label(self, anchor="w", relief="sunken")
        self.status.pack(fill="x", side="bottom")

        # Initial render
        self.render()
    
    # --- Event handlers ---
    def _on_slider(self, _evt=None) -> None:
        """Debounce heavy re-rendering while the user is dragging."""
        if self._after_id:
            self.after_cancel(self._after_id)
        self._after_id = self.after(80, self.render) # ~80ms debounce
        
    def reset_params(self) -> None:
        """Reset sliders to default values and re-render."""
        self.var_mA.set(DEFAULT_MA)
        self.var_kVp.set(DEFAULT_KVP)
        self.render()

    def save_png(self) -> None:
        """Save the last rendered image to a PNG file."""
        if not self._last_pil:
            messagebox.showwarning("Nothing to save", "Please render an image first.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png")],
            initialfile="xray_sim.png",
            title="Save current image",
        )
        if path:
            self._last_pil.save(path)
            messagebox.showinfo("Saved", f"Saved: {path}")
    
    # --- Render pipeline ---
    def render(self) -> None:
        """Call simulator and update the preview."""
        self._after_id = None

        mA = float(self.var_mA.get())
        kVp = float(self.var_kVp.get())

        arr = simulate(mA=mA, kVp=kVp, size=IMG_SIZE)
        arr = np.clip(arr, 0.0, 1.0)

        # Convert to 8-bit grayscale PIL image
        img = Image.fromarray((arr * 255).astype(np.uint8), mode="L")
        self._last_pil = img

        # Keep a reference to avoid garbage collection
        self._last_tk = ImageTk.PhotoImage(img)
        self.preview.configure(image=self._last_tk)

        # Update status bar
        h, w = IMG_SIZE
        self.status.configure(text=f"mA: {mA:.0f} kVp:{kVp:.0f} Size: {w}x{h}")

def main() -> None:
    XRayApp().mainloop()

if __name__ == "__main__":
    main()        