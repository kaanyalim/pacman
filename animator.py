"""
Sprite-Frame-Animator.
Steuert das zeitbasierte Durchschalten von Animations-Frames
für wiederholende Zyklen (Loop) oder einmalige Sequenzen (Todesanimation).
"""

class SpriteAnimator(object):
    """
    Klasse zur Verwaltung und Zeitsteuerung von Frame-Sequenzen.
    """
    # Anpassbar: Standard-Framerate für Animationen (Standard: 20 FPS)
    def __init__(self, frames=None, fps=20, loop=True):
        self.frames = list(frames) if frames is not None else []
        self.current_frame = 0
        self.speed = fps
        self.loop = loop
        self.time_acc = 0.0
        self.finished = False

    def reset(self):
        """Setzt die Animation auf das erste Frame zurück."""
        self.current_frame = 0
        self.time_acc = 0.0
        self.finished = False

    def update(self, dt):
        """
        Schaltet das Frame basierend auf dem Zeitintervall weiter und gibt die Koordinaten des aktuellen Frames zurück.
        """
        if not self.finished:
            self._step_frame(dt)

        if self.current_frame >= len(self.frames):
            if self.loop and len(self.frames) > 0:
                self.current_frame = 0
            else:
                self.finished = True
                self.current_frame = max(0, len(self.frames) - 1)

        return self.frames[self.current_frame] if self.frames else None

    def _step_frame(self, dt):
        """Erhöht den Frame-Index nach Ablauf der berechneten Frame-Dauer."""
        self.time_acc += dt
        frame_interval = 1.0 / self.speed if self.speed > 0 else 1.0
        if self.time_acc >= frame_interval:
            self.current_frame += 1
            self.time_acc = 0.0

    def nextFrame(self, dt):
        self._step_frame(dt)


# Kompatibilitäts-Alias
Animator = SpriteAnimator
