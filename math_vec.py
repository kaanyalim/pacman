"""
2D-Vektormathematik für Raster- und Positionsberechnungen.
Stellt grundlegende Vektoroperationen (Addition, Subtraktion, Skalierung, Distanz) bereit.
"""
import math

class Vec2(object):
    """
    2D-Vektorklasse mit Operatorenüberladung für Positions- und Bewegungsberechnungen.
    """
    __slots__ = ('x', 'y', 'thresh')

    def __init__(self, x=0.0, y=0.0):
        self.x = float(x)
        self.y = float(y)
        # Fehlertoleranz für Float-Vergleiche bei Richtungs- und Positionsprüfungen
        self.thresh = 1e-6

    # Vektoraddition (z. B. Position + Bewegungsvektor)
    def __add__(self, other):
        return Vec2(self.x + other.x, self.y + other.y)

    # Vektorsubtraktion (z. B. Distanz zwischen zwei Akteuren)
    def __sub__(self, other):
        return Vec2(self.x - other.x, self.y - other.y)

    # Richtungsumkehr
    def __neg__(self):
        return Vec2(-self.x, -self.y)

    # Skalare Multiplikation (z. B. Geschwindigkeit * Delta-Time)
    def __mul__(self, scalar):
        return Vec2(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar):
        return Vec2(self.x * scalar, self.y * scalar)

    # Skalare Division
    def __truediv__(self, scalar):
        if scalar == 0:
            return None
        inv = 1.0 / float(scalar)
        return Vec2(self.x * inv, self.y * inv)

    def __div__(self, scalar):
        return self.__truediv__(scalar)

    # Prüft Gleichheit unter Berücksichtigung einer kleinen Epsilon-Toleranz
    def __eq__(self, other):
        if not isinstance(other, Vec2):
            return False
        return (abs(self.x - other.x) < self.thresh) and (abs(self.y - other.y) < self.thresh)

    # Quadratische Länge: Optimiert für Distanzvergleiche, da keine teure Quadratwurzel nötig ist
    def magnitude_squared(self):
        return self.x * self.x + self.y * self.y

    def magnitudeSquared(self):
        return self.magnitude_squared()

    # Euklidische Norm / tatsächliche Vektorlänge
    def magnitude(self):
        return math.hypot(self.x, self.y)

    # Erzeugt eine eigenständige Kopie des Vektors
    def copy(self):
        return Vec2(self.x, self.y)

    # Konvertierungsmethoden für Pygame-Zeichenfunktionen
    def as_tuple(self):
        return self.x, self.y

    def asTuple(self):
        return self.as_tuple()

    def as_int(self):
        return int(self.x), int(self.y)

    def asInt(self):
        return self.as_int()

    def __str__(self):
        return f"Vec2({self.x:.2f}, {self.y:.2f})"

    def __repr__(self):
        return f"Vec2({self.x}, {self.y})"


# Kompatibilitäts-Alias für bestehende Referenzen
Vector2 = Vec2
