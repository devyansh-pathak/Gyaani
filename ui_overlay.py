import math
import random
import queue
import threading
import time
import tkinter as tk
import ctypes

# Enable High-DPI awareness on Windows for crisp rendering
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass


class MiniVoicePillOverlay:
    """
    Ultra-compact, floating dynamic voice pill anchored at the bottom of the screen,
    inspired by modern bottom media controls. Contains only the dynamic voice input
    visualizer and status cues—no text.
    """

    WIDTH = 200
    HEIGHT = 40
    RADIUS = 20
    CHROMA_KEY = "#000001"  # Pure black key for 100% transparent window edges

    # Themes
    THEMES = {
        "IDLE": {
            "bg": "#12131A",
            "border": "#282A3A",
            "icon_bg": "#1C1E2A",
            "icon_fg": "#94A3B8",
            "wave": "#64748B",
            "dot": "#475569",
            "icon": "✦",
        },
        "DICTATION": {
            "bg": "#0D1814",
            "border": "#10B981",
            "icon_bg": "#064E3B",
            "icon_fg": "#34D399",
            "wave": "#10B981",
            "dot": "#34D399",
            "icon": "🎙️",
        },
        "AI_PROCESSING": {
            "bg": "#171226",
            "border": "#8B5CF6",
            "icon_bg": "#4C1D95",
            "icon_fg": "#C084FC",
            "wave": "#A855F7",
            "dot": "#C084FC",
            "icon": "⚡",
        },
        "DONE": {
            "bg": "#0D1814",
            "border": "#10B981",
            "icon_bg": "#064E3B",
            "icon_fg": "#6EE7B7",
            "wave": "#10B981",
            "dot": "#10B981",
            "icon": "✓",
        },
    }

    def __init__(self):
        self.root = None
        self.canvas = None
        self.msg_queue = queue.Queue()
        self.is_running = False

        self.mode = "IDLE"
        self.theme = self.THEMES["IDLE"]

        # 9 audio equalizer bars
        self.num_bars = 8
        self.bar_values = [0.15] * self.num_bars
        self.target_values = [0.15] * self.num_bars

        # Animation states
        self.phase = 0.0
        self.current_volume = 0.0

        # Dragging state
        self.drag_x = 0
        self.drag_y = 0

    def start(self):
        self.root = tk.Tk()
        self.root.title("Gyaani Mini Pill")
        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", True)

        # Transparent edges: only the rounded pill is visible!
        self.root.configure(bg=self.CHROMA_KEY)
        self.root.wm_attributes("-transparentcolor", self.CHROMA_KEY)

        # Position bottom-center
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        x = (screen_w - self.WIDTH) // 2
        y = screen_h - self.HEIGHT - 35
        self.root.geometry(f"{self.WIDTH}x{self.HEIGHT}+{x}+{y}")

        self.canvas = tk.Canvas(
            self.root,
            width=self.WIDTH,
            height=self.HEIGHT,
            bg=self.CHROMA_KEY,
            highlightthickness=0,
            cursor="hand2",
        )
        self.canvas.pack(fill="both", expand=True)

        # Draggable
        self.canvas.bind("<Button-1>", self._on_drag_start)
        self.canvas.bind("<B1-Motion>", self._on_drag_motion)
        self.canvas.bind("<Double-Button-1>", lambda e: self._reset_position())

        self.is_running = True
        self._animate_loop()
        self._process_queue()
        self.root.mainloop()

    def _reset_position(self):
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        x = (screen_w - self.WIDTH) // 2
        y = screen_h - self.HEIGHT - 35
        self.root.geometry(f"{self.WIDTH}x{self.HEIGHT}+{x}+{y}")

    def _on_drag_start(self, event):
        self.drag_x = event.x
        self.drag_y = event.y

    def _on_drag_motion(self, event):
        dx = event.x - self.drag_x
        dy = event.y - self.drag_y
        new_x = self.root.winfo_x() + dx
        new_y = self.root.winfo_y() + dy
        self.root.geometry(f"+{new_x}+{new_y}")

    # --- Public Thread-Safe API ---

    def feed_volume(self, volume: float):
        """Pass microphone audio volume/amplitude (0.0 to 1.0)."""
        self.msg_queue.put(("VOLUME", max(0.0, min(1.0, volume))))

    def push_lyric(self, text: str):
        """No-op: Text is omitted in ultra-mini visualizer mode."""
        pass

    def update_current(self, text: str):
        """No-op: Text is omitted in ultra-mini visualizer mode."""
        pass

    def set_mode(self, mode: str, label: str = None):
        """Sets the mode: 'IDLE', 'DICTATION', 'AI_PROCESSING', 'DONE'."""
        self.msg_queue.put(("MODE", mode))

    def close(self):
        self.msg_queue.put(("CLOSE", None))

    # --- Internal Event Loop ---

    def _process_queue(self):
        if not self.root:
            return

        try:
            while not self.msg_queue.empty():
                cmd, data = self.msg_queue.get_nowait()
                if cmd == "VOLUME":
                    self.current_volume = data
                elif cmd == "MODE":
                    if data in self.THEMES:
                        self.mode = data
                        self.theme = self.THEMES[data]
                elif cmd == "CLOSE":
                    self.is_running = False
                    self.root.destroy()
                    return
        except Exception:
            pass

        self.root.after(16, self._process_queue)

    def _animate_loop(self):
        if not self.is_running or not self.canvas:
            return

        self.canvas.delete("all")
        self.phase += 0.12

        # 1. Draw sleek capsule / stadium shape
        self._draw_pill_container()

        # 2. Draw Left Icon Badge
        self._draw_icon_badge()

        # 3. Draw Dynamic Voice Equalizer Wave
        self._draw_voice_wave()

        # 4. Draw Right Status Indicator Orb
        self._draw_status_orb()

        # 60 FPS update loop
        self.root.after(16, self._animate_loop)

    def _draw_pill_container(self):
        """Draws rounded pill background with smooth glowing outline."""
        w = self.WIDTH
        h = self.HEIGHT
        r = self.RADIUS

        # Rounded stadium container points
        points = [
            r, 1,
            w - r, 1,
            w - 1, 1,
            w - 1, r,
            w - 1, h - r,
            w - 1, h - 1,
            w - r, h - 1,
            r, h - 1,
            1, h - 1,
            1, h - r,
            1, r,
            1, 1,
        ]

        self.canvas.create_polygon(
            points,
            smooth=True,
            fill=self.theme["bg"],
            outline=self.theme["border"],
            width=1.5,
        )

    def _draw_icon_badge(self):
        """Small rounded icon box on the left (like media artwork)."""
        box_x1 = 7
        box_y1 = 7
        box_x2 = 33
        box_y2 = 33
        br = 6

        # Draw rounded badge
        points = [
            box_x1 + br, box_y1,
            box_x2 - br, box_y1,
            box_x2, box_y1,
            box_x2, box_y1 + br,
            box_x2, box_y2 - br,
            box_x2, box_y2,
            box_x2 - br, box_y2,
            box_x1 + br, box_y2,
            box_x1, box_y2,
            box_x1, box_y2 - br,
            box_x1, box_y1 + br,
            box_x1, box_y1,
        ]
        self.canvas.create_polygon(points, smooth=True, fill=self.theme["icon_bg"], outline="")

        # Icon symbol
        self.canvas.create_text(
            20, 20,
            text=self.theme["icon"],
            fill=self.theme["icon_fg"],
            font=("Segoe UI Emoji", 10, "bold"),
        )

    def _draw_voice_wave(self):
        """
        Draws dynamic voice input wave bars that bounce and dance
        in real-time according to voice volume and frequency.
        """
        center_y = self.HEIGHT // 2
        start_x = 46
        bar_spacing = 14
        bar_width = 3.5
        max_h = 22  # Maximum bar height in px

        # Decay current volume smoothly
        vol = self.current_volume
        self.current_volume = max(0.0, self.current_volume * 0.88)

        is_active = self.mode in ["DICTATION", "AI_PROCESSING"] or vol > 0.05

        for i in range(self.num_bars):
            if is_active:
                # Combine real voice volume with phase oscillation
                modulation = math.sin(self.phase + i * 0.75) * 0.5 + 0.5
                target_h = 4 + (vol * max_h * 1.5 * modulation) + random.uniform(0, 3)
                target_h = max(3.5, min(max_h, target_h))
            else:
                # Gentle resting pulse
                target_h = 3.0 + math.sin(self.phase * 0.5 + i * 0.4) * 1.5

            # Smooth interpolation
            self.bar_values[i] += (target_h - self.bar_values[i]) * 0.35
            h = self.bar_values[i]

            x = start_x + i * bar_spacing
            y1 = center_y - (h / 2)
            y2 = center_y + (h / 2)

            self.canvas.create_line(
                x, y1, x, y2,
                fill=self.theme["wave"],
                width=bar_width,
                capstyle="round",
            )

    def _draw_status_orb(self):
        """Small pulsing glowing dot / status indicator on the right edge."""
        cx = self.WIDTH - 18
        cy = self.HEIGHT // 2

        if self.mode in ["DICTATION", "AI_PROCESSING"]:
            # Pulsing size
            pulse_r = 3.5 + math.sin(self.phase * 2) * 1.2
        else:
            pulse_r = 3.0

        self.canvas.create_oval(
            cx - pulse_r, cy - pulse_r,
            cx + pulse_r, cy + pulse_r,
            fill=self.theme["dot"],
            outline="",
        )


_global_mini_overlay = None


def launch_overlay():
    """Starts the mini pill overlay in a background daemon thread."""
    global _global_mini_overlay
    _global_mini_overlay = MiniVoicePillOverlay()
    thread = threading.Thread(target=_global_mini_overlay.start, daemon=True)
    thread.start()
    time.sleep(0.3)
    return _global_mini_overlay


def get_overlay() -> MiniVoicePillOverlay:
    global _global_mini_overlay
    if _global_mini_overlay is None:
        return launch_overlay()
    return _global_mini_overlay


if __name__ == "__main__":
    print("=" * 60)
    print("Launching Ultra-Mini Voice Pill (No text, pure voice dynamics)...")
    print("Check the bottom center of your screen!")
    print("=" * 60)

    pill = launch_overlay()

    try:
        time.sleep(1)
        # Simulate voice dictation with dynamic volume
        pill.set_mode("DICTATION")
        for _ in range(60):
            # Simulate speech loudness variation
            simulated_vol = random.uniform(0.1, 0.95) if random.random() > 0.2 else 0.02
            pill.feed_volume(simulated_vol)
            time.sleep(0.06)

        pill.set_mode("AI_PROCESSING")
        time.sleep(2.5)

        pill.set_mode("IDLE")
        print("Pill active. Press Ctrl+C in terminal to stop.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pill.close()
