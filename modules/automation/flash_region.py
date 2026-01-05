import tkinter as tk
import threading
import time


def flash_region(x1, y1, x2, y2, duration_ms=800, thickness=3):
    width = x2 - x1
    height = y2 - y1

    def _show():
        root = tk.Tk()
        root.overrideredirect(True)      # no window chrome
        root.attributes("-topmost", True)
        root.attributes("-transparentcolor", "white")

        root.geometry(f"{width}x{height}+{x1}+{y1}")

        canvas = tk.Canvas(
            root,
            width=width,
            height=height,
            bg="white",
            highlightthickness=0,
        )
        canvas.pack()

        canvas.create_rectangle(
            thickness,
            thickness,
            width - thickness,
            height - thickness,
            outline="red",
            width=thickness,
        )

        root.after(duration_ms, root.destroy)
        root.mainloop()

    threading.Thread(target=_show, daemon=True).start()
