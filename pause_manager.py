"""
Pausen- & Timer-Controller.
Verwaltet manuelle Spielpausen (z. B. Leertaste) sowie zeitgesteuerte Spielverzögerungen
mit automatischer Fortsetzungsfunktion und Callbacks (z. B. nach Levelgewinn oder Pacman-Tod).
"""

class PauseController(object):
    """
    Verwaltet Pausenzustände und Timer-basierte Ereignis-Verzögerungen.
    """
    def __init__(self, initial_state=False):
        self.paused = initial_state
        self.timer = 0.0
        self.pauseTime = None
        self.func = None

    def update(self, dt):
        """
        Zählt die Pausenzeit herunter und gibt nach Ablauf die hinterlegte Callback-Funktion zurück.
        """
        if self.pauseTime is not None:
            self.timer += dt
            if self.timer >= self.pauseTime:
                callback = self.func
                self.timer = 0.0
                self.paused = False
                self.pauseTime = None
                self.func = None
                return callback
        return None

    # Anpassbar: Setzen von Pausenzeit und Callback-Methode (z. B. 3s für Levelwechsel)
    def setPause(self, playerPaused=False, pauseTime=None, func=None):
        self.timer = 0.0
        self.func = func
        self.pauseTime = pauseTime
        self.toggle()

    def toggle(self):
        """Schaltet den Pausenzustand um."""
        self.paused = not self.paused

    def flip(self):
        self.toggle()


# Kompatibilitäts-Alias
Pause = PauseController
