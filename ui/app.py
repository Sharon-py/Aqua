import tkinter as tk
from tkinter import font
from tkinter import ttk

import config
from core.timer import CountdownTimer


class AquaApp(tk.Tk):
    def __init__(self):
        super().__init__()

        print("[DEBUG] AquaApp.__init__")

        # -------- Police Pixel NES (installée dans Windows) --------
        self.pixel_font = font.Font(family="Pixel NES", size=12)
        self.pixel_font_small = font.Font(family="Pixel NES", size=9)

        # ---------------- Fenêtre principale ----------------
        self.title(config.WINDOW_TITLE)
        self.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
        self.configure(bg="#fbe9f7")
        self.resizable(False, False)

        # -------- Logique hydratation --------
        self.timer = None
        self.total_cl = 0
        self.hour_cl = 0
        self.hourly_goal_cl = config.HOURLY_GOAL_CL
        self.daily_goal_cl = config.DAILY_GOAL_CL

        # XP
        self.level = 1
        self.xp = 0
        self.xp_needed = 3

        # Humeur + scintillement
        self.drop_mood = "neutral"   # "neutral" | "happy" | "sad"
        self.sparkle_on = False

        # Nom de la goutte
        self.drop_name_var = tk.StringVar(value="Aqua")

        # Animation de saut
        self.drop_jump_state = False

        # ---------------- Styles ttk ----------------
        style = ttk.Style(self)
        style.theme_use("clam")

        base_layout = style.layout("Horizontal.TProgressbar")
        style.layout("Hour.TProgressbar", base_layout)
        style.layout("Day.TProgressbar", base_layout)
        style.layout("XP.TProgressbar", base_layout)

        style.configure("Hour.TProgressbar",
                        troughcolor="#ffe4f3",
                        background="#ff9ecb")
        style.configure("Day.TProgressbar",
                        troughcolor="#e3f2fd",
                        background="#90caf9")
        style.configure("XP.TProgressbar",
                        troughcolor="#e8f5e9",
                        background="#66bb6a")

        # ---------------- Carte principale ----------------
        self.card_outer = tk.Frame(self, bg="#fbe9f7")
        self.card_outer.pack(expand=True, fill="both", padx=10, pady=10)

        card_bg = "#ffeaf5"
        self.card = tk.Frame(self.card_outer, bg=card_bg, bd=3, relief="ridge")
        self.card.pack(expand=True, fill="both", padx=5, pady=5)

        # Titre
        tk.Label(
            self.card,
            text="Aqua – Rappel hydratation",
            font=self.pixel_font,
            bg=card_bg,
            fg="#3e2723"
        ).pack(pady=(4, 0))

        # Nom + niveau + XP
        self.status_label = tk.Label(
            self.card,
            text="",
            font=self.pixel_font_small,
            bg=card_bg,
            fg="#3e2723"
        )
        self.status_label.pack(pady=(2, 4))

        # ---------------- Zone du personnage ----------------
        drop_area = tk.Frame(self.card, bg=card_bg, bd=4, relief="ridge")
        drop_area.pack(pady=(0, 6))

        # Barre XP au-dessus de la scène
        self.xp_progress = ttk.Progressbar(
            drop_area,
            length=120,
            mode="determinate",
            maximum=self.xp_needed,
            style="XP.TProgressbar"
        )
        self.xp_progress.pack(pady=(2, 4))

        # Canvas de la scène
        self.drop_canvas = tk.Canvas(
            drop_area,
            width=144,
            height=112,
            bg="#f7f2e8",
            highlightthickness=0
        )
        self.drop_canvas.pack(padx=4, pady=(0, 4))

        self.draw_kawaii_drop(jump=self.drop_jump_state)
        self.animate_drop()

        # ---------------- Countdown ----------------
        self.countdown_label = tk.Label(
            self.card,
            text="Prochain bilan dans --:--",
            font=self.pixel_font_small,
            bg=card_bg,
            fg="#4e342e"
        )
        self.countdown_label.pack(pady=(2, 4))

        # ---------------- Stats ----------------
        stats_frame = tk.Frame(self.card, bg=card_bg)
        stats_frame.pack(pady=(0, 4))

        self.hour_label = tk.Label(
            stats_frame,
            text=f"Sur cette heure : 0 / {self.hourly_goal_cl} cl",
            font=self.pixel_font_small,
            bg=card_bg
        )
        self.hour_label.pack()

        self.hour_progress = ttk.Progressbar(
            stats_frame,
            length=260,
            maximum=self.hourly_goal_cl,
            style="Hour.TProgressbar"
        )
        self.hour_progress.pack(pady=(0, 4))

        self.total_label = tk.Label(
            stats_frame,
            text=f"Aujourd'hui : 0 / {self.daily_goal_cl} cl 💧",
            font=self.pixel_font_small,
            bg=card_bg
        )
        self.total_label.pack()

        self.daily_progress = ttk.Progressbar(
            stats_frame,
            length=260,
            maximum=self.daily_goal_cl,
            style="Day.TProgressbar"
        )
        self.daily_progress.pack(pady=(0, 4))

        # ---------------- Boutons CL ----------------
        controls = tk.Frame(self.card, bg="#ffd1e8")
        controls.pack(fill="x", pady=(4, 0))

        tk.Label(
            controls,
            text="Je viens de boire :",
            bg="#ffd1e8",
            font=self.pixel_font_small
        ).grid(row=0, column=0, columnspan=4, pady=4)

        self._make_drink_button(controls, "5 cl", 5, 0, "#ff80ab")
        self._make_drink_button(controls, "10 cl", 10, 1, "#ffb74d")
        self._make_drink_button(controls, "15 cl", 15, 2, "#4db6ac")
        self._make_drink_button(controls, "20 cl", 20, 3, "#64b5f6")

        tk.Label(
            controls,
            text="Laisse Aqua ouverte pendant que tu bosses 💻",
            bg="#ffd1e8",
            font=self.pixel_font_small
        ).grid(row=2, column=0, columnspan=4, pady=6)

        # ---------------- Timer ----------------
        self.start_hour_timer()
        self.update_xp_ui()

        # ---------------- Popup de nom ----------------
        # on l'ouvre après un tout petit délai
        self.after(50, self.ask_drop_name)

    # ==========================================================
    #                   UI : nom de la goutte
    # ==========================================================
    def ask_drop_name(self):
        print("[DEBUG] ask_drop_name")

        popup = tk.Toplevel(self)
        popup.title("Nom de ta goutte 💧")
        popup.configure(bg="#ffeaf5")
        popup.resizable(False, False)

        popup.transient(self)
        popup.grab_set()
        popup.lift()
        popup.attributes("-topmost", True)

        popup.update_idletasks()
        w, h = 330, 200
        sw = popup.winfo_screenwidth()
        sh = popup.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        popup.geometry(f"{w}x{h}+{x}+{y}")

        frame = tk.Frame(popup, bg="#ffccde", bd=6, relief="ridge")
        frame.pack(expand=True, fill="both", padx=10, pady=10)

        tk.Label(
            frame,
            text="Nom de ta goutte",
            font=self.pixel_font,
            bg="#ffccde",
            fg="#3e2723"
        ).pack(pady=(10, 4))

        name_var = tk.StringVar()
        entry = tk.Entry(
            frame,
            textvariable=name_var,
            font=self.pixel_font_small,
            justify="center",
            bd=4,
            relief="ridge",
            bg="#fff8fd"
        )
        entry.pack(pady=8)
        entry.focus()

        def validate():
            name = name_var.get().strip() or "Aqua"
            self.drop_name_var.set(name)
            self.update_xp_ui()
            popup.destroy()

        tk.Button(
            frame,
            text="VALIDER",
            command=validate,
            font=self.pixel_font_small,
            bg="#f48fb1",
            bd=4,
            relief="ridge"
        ).pack(pady=8)

        # on peut laisser Tk gérer, pas besoin de wait_window ici

    # ==========================================================
    #                   Boutons CL
    # ==========================================================
    def _make_drink_button(self, parent, text, cl_value, col, bg):
        tk.Button(
            parent,
            text=text,
            command=lambda: self.log_drink(cl_value),
            bg=bg,
            bd=3,
            relief="ridge",
            font=self.pixel_font_small
        ).grid(row=1, column=col, padx=5, pady=4)

    # ==========================================================
    #                   Dessin de la goutte + chambre
    # ==========================================================
    def draw_kawaii_drop(self, jump: bool = False):
        c = self.drop_canvas
        c.delete("all")
        px = 4

        def p(x, y, col):
            c.create_rectangle(
                x * px, y * px,
                (x + 1) * px, (y + 1) * px,
                fill=col, outline=col
            )

        oy = -1 if jump else 0

        # --- décor ---
        wall = "#f7f2e8"
        floor = "#d4b79c"
        floor_dark = "#b18b69"
        rug = "#b3e5fc"
        rug_dark = "#90caf9"

        for x in range(36):
            for y in range(0, 14):
                p(x, y, wall)

        for x in range(36):
            for y in range(14, 28):
                p(x, y, floor)
            p(x, 14, floor_dark)

        for x in range(9, 27):
            p(x, 14, rug)
            p(x, 15, rug_dark)

        frame_col = "#e3c7d8"
        sky = "#c4e8ff"
        cloud = "#ffffff"

        for x in range(23, 33):
            p(x, 2, frame_col)
            p(x, 7, frame_col)
        for y in range(3, 7):
            p(23, y, frame_col)
            p(32, y, frame_col)

        for x in range(24, 32):
            for y in range(3, 7):
                p(x, y, sky)

        for (x, y) in [(26, 4), (27, 4), (28, 4), (27, 5)]:
            p(x, y, cloud)

        pot = "#b8734c"
        pot_dark = "#8b5a33"
        leaf = "#76c37a"
        leaf_dark = "#4e8f52"

        for x in range(5, 8):
            p(x, 13, pot)
        for x in range(5, 8):
            p(x, 14, pot_dark)

        for (x, y) in [(5, 11), (6, 10), (7, 11)]:
            p(x, y, leaf)
        p(6, 11, leaf_dark)

        # --- goutte ---
        body = "#7ed7ff"
        body_dark = "#5ec3ea"
        highlight = "#ffffff"
        blush = "#ffb7c5"
        eye = "#3a2a29"
        shadow = "#a78363"

        for x in range(13, 23):
            p(x, 16, shadow)

        body_pixels = [
            (18, 9),
            (17, 10), (18, 10), (19, 10),
            (16, 11), (17, 11), (18, 11), (19, 11), (20, 11),
            (16, 12), (17, 12), (18, 12), (19, 12), (20, 12),
            (17, 13), (18, 13), (19, 13),
        ]

        highlight_pixels = [
            (17, 10),
            (16, 11),
        ]

        blush_pixels = [
            (17, 13),
            (19, 13),
        ]

        eyes = [
            (17, 12),
            (19, 12),
        ]

        mood = getattr(self, "drop_mood", "neutral")
        if mood == "happy":
            mouth_pixels = [(17, 13), (18, 13), (19, 13)]
        elif mood == "sad":
            mouth_pixels = [(17, 12), (18, 11), (19, 12)]
        else:
            mouth_pixels = [(18, 13)]

        dark_border = [
            (17, 13), (18, 13), (19, 13),
        ]

        for (x, y) in body_pixels:
            p(x, y + oy, body)
        for (x, y) in dark_border:
            p(x, y + oy, body_dark)
        for (x, y) in highlight_pixels:
            p(x, y + oy, highlight)
        for (x, y) in blush_pixels:
            p(x, y + oy, blush)
        for (x, y) in eyes:
            p(x, y + oy, eye)
        for (x, y) in mouth_pixels:
            p(x, y + oy, eye)

        if getattr(self, "sparkle_on", False) and mood == "happy":
            sparkle_color1 = "#ffffff"
            sparkle_color2 = "#fff7b0"
            for i, (sx, sy) in enumerate([(13, 8), (23, 9), (15, 7), (21, 7)]):
                p(sx, sy, sparkle_color1 if i % 2 == 0 else sparkle_color2)

    def draw_popup_drop(self, canvas: tk.Canvas, happy: bool = True):
        canvas.delete("all")
        px = 4

        def p(x, y, col):
            canvas.create_rectangle(
                x * px, y * px,
                (x + 1) * px, (y + 1) * px,
                fill=col, outline=col
            )

        body = "#7ed7ff"
        body_dark = "#5ec3ea"
        highlight = "#ffffff"
        blush = "#ffb7c5"
        eye = "#3a2a29"

        body_pixels = [
            (4, 2),
            (3, 3), (4, 3), (5, 3),
            (3, 4), (4, 4), (5, 4),
            (4, 5),
        ]

        for (x, y) in body_pixels:
            p(x, y, body)

        for (x, y) in [(3, 4), (4, 5), (5, 4)]:
            p(x, y, body_dark)

        p(3, 3, highlight)

        for (x, y) in [(3, 5), (5, 5)]:
            p(x, y, blush)

        for (x, y) in [(3, 4), (5, 4)]:
            p(x, y, eye)

        if happy:
            mouth = [(4, 5)]
        else:
            mouth = [(3, 6), (4, 5), (5, 6)]

        for (x, y) in mouth:
            p(x, y, eye)

    # ==========================================================
    #                   Animation goutte
    # ==========================================================
    def animate_drop(self):
        self.drop_jump_state = not self.drop_jump_state

        if self.drop_mood == "happy":
            self.sparkle_on = not self.sparkle_on
        else:
            self.sparkle_on = False

        self.draw_kawaii_drop(jump=self.drop_jump_state)

        delay = 180 if self.drop_jump_state else 900
        self.after(delay, self.animate_drop)

    # ==========================================================
    #                   XP UI
    # ==========================================================
    def update_xp_ui(self):
        self.xp_progress["value"] = self.xp
        name = self.drop_name_var.get()
        self.status_label.config(
            text=f"{name} – Niveau {self.level} – XP {self.xp}/{self.xp_needed}"
        )

    # ==========================================================
    #                   Timer
    # ==========================================================
    def start_hour_timer(self):
        interval = config.DEFAULT_INTERVAL_MIN * 60
        self.timer = CountdownTimer(
            interval,
            on_tick=self.update_countdown,
            on_finish=self.hour_check
        )
        self.timer.start()
        self.update_countdown(interval)
        self.schedule_tick()

    def schedule_tick(self):
        if self.timer and self.timer.running:
            self.timer.tick()
            self.after(1000, self.schedule_tick)

    def update_countdown(self, sec):
        m, s = divmod(sec, 60)
        self.countdown_label.config(
            text=f"Prochain bilan dans {m:02}:{s:02}"
        )

    # ==========================================================
    #                   Fin d'heure
    # ==========================================================
    def hour_check(self):
        missing = self.hourly_goal_cl - self.hour_cl

        if missing > 0:
            if self.level > 1:
                self.level -= 1
            self.xp = 0
            self.drop_mood = "sad"
            self.update_xp_ui()
            self.show_hour_popup(False, missing)
        else:
            self.xp += 1
            if self.xp >= self.xp_needed and self.level < 3:
                self.level += 1
                self.xp = 0
            self.drop_mood = "happy"
            self.update_xp_ui()
            self.show_hour_popup(True, 0)

        self.draw_kawaii_drop(jump=self.drop_jump_state)

        self.hour_cl = 0
        self.hour_label.config(
            text=f"Sur cette heure : 0 / {self.hourly_goal_cl} cl"
        )
        self.hour_progress["value"] = 0

    # ==========================================================
    #                   Popup fin d'heure
    # ==========================================================
    def show_hour_popup(self, success, remaining):
        popup = tk.Toplevel(self)
        popup.attributes("-topmost", True)
        popup.transient(self)
        popup.grab_set()
        popup.lift()

        popup.configure(bg="#ffeaf5")
        popup.title("Aqua 💧")

        w, h = 280, 230
        self.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - w) // 2
        y = self.winfo_y() + (self.winfo_height() - h) // 2
        popup.geometry(f"{w}x{h}+{x}+{y}")
        popup.resizable(False, False)

        name = self.drop_name_var.get()

        if success:
            title = "Bravo ! 🎉"
            msg = (
                f"Tu as atteint ton objectif.\n"
                f"{name} est fier·e de toi 💙\n"
                f"XP : {self.xp}/{self.xp_needed}"
            )
        else:
            title = "Oups… 💧"
            msg = (
                f"Il te manque {remaining} cl\n"
                f"pour atteindre ton objectif.\n\n"
                f"{name} est un peu triste…"
            )

        tk.Label(
            popup,
            text=title,
            font=self.pixel_font,
            bg="#ffeaf5",
            fg="#3e2723"
        ).pack(pady=(6, 2))

        mini_canvas = tk.Canvas(
            popup,
            width=80,
            height=80,
            bg="#ffeaf5",
            highlightthickness=0
        )
        mini_canvas.pack(pady=(2, 4))
        self.draw_popup_drop(mini_canvas, happy=success)

        tk.Label(
            popup,
            text=msg,
            font=self.pixel_font_small,
            bg="#ffeaf5",
            fg="#4e342e",
            justify="center"
        ).pack(pady=(2, 6))

        tk.Button(
            popup,
            text="OK 💧",
            command=popup.destroy,
            font=self.pixel_font_small,
            bg="#ffccde",
            bd=3,
            relief="ridge"
        ).pack(pady=(0, 8))

    # ==========================================================
    #                   Log de boisson
    # ==========================================================
    def log_drink(self, cl):
        self.total_cl += cl
        self.hour_cl += cl

        self.hour_label.config(
            text=f"Sur cette heure : {self.hour_cl} / {self.hourly_goal_cl} cl"
        )
        self.total_label.config(
            text=f"Aujourd'hui : {self.total_cl} / {self.daily_goal_cl} cl 💧"
        )

        self.hour_progress["value"] = self.hour_cl
        self.daily_progress["value"] = self.total_cl

    # ==========================================================
    #                   Lancement
    # ==========================================================
    def run(self):
        print("[DEBUG] mainloop start")
        self.mainloop()
