class CountdownTimer:
    """Logique de compte à rebours, sans dépendance à Tkinter."""

    def __init__(self, interval_seconds, on_tick=None, on_finish=None):
        """
        interval_seconds : durée totale en secondes
        on_tick(remaining_seconds) : callback appelé à chaque seconde
        on_finish() : callback quand le temps est écoulé
        """
        self.interval_seconds = interval_seconds
        self.remaining_seconds = interval_seconds
        self.on_tick = on_tick
        self.on_finish = on_finish
        self.running = False

    def start(self):
        self.running = True

    def stop(self):
        self.running = False

    def reset(self, new_interval_seconds=None):
        if new_interval_seconds is not None:
            self.interval_seconds = new_interval_seconds
        self.remaining_seconds = self.interval_seconds

    def tick(self):
        """À appeler régulièrement (par exemple toutes les secondes)."""
        if not self.running:
            return

        if self.remaining_seconds > 0:
            self.remaining_seconds -= 1
            if self.on_tick:
                self.on_tick(self.remaining_seconds)
        else:
            if self.on_finish:
                self.on_finish()
            # on repart pour un cycle
            self.reset()
