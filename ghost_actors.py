"""
Geister-KI & Gegner-Modul.
Definiert die Basisklasse Ghost sowie die individuellen Wegfindungs- und Ziel-Algorithmen
der vier Geister:
- Blinky (Rot): Direkter Verfolger
- Pinky (Pink): Hinterhältiger Abfangjäger (zielt 4 Kacheln voraus)
- Inky (Türkis): Komplexer Flankierer (Vektorspiegelung über Blinky)
- Clyde (Orange): Feiger Angreifer (flieht ab < 8 Kacheln Distanz)
"""
from actor import Actor
from math_vec import Vec2
from game_config import (
    GHOST, BLINKY, PINKY, INKY, CLYDE,
    RED, PINK, TEAL, ORANGE, DOWN,
    TILEWIDTH, TILEHEIGHT, NCOLS, NROWS,
    SCATTER, CHASE, FREIGHT, SPAWN
)
from ghost_state_machine import GhostStateManager
from graphics_engine import GhostVisuals

class Ghost(Actor):
    """
    Basisklasse für Geistergegner inklusive Zustandsverwaltung und Modus-Umschaltung.
    """
    def __init__(self, node, pacman=None, blinky=None):
        super(Ghost, self).__init__(node)
        self.name = GHOST
        # Anpassbar: Basispunkte beim Fressen des ersten Geistes im Angst-Modus
        self.points = 200
        self.goal = Vec2()
        self.directionMethod = self.goalDirection
        self.pacman = pacman
        self.mode = GhostStateManager(self)
        self.blinky = blinky
        self.homeNode = node
        self.spawnNode = None

    def reset(self):
        super(Ghost, self).reset()
        self.points = 200
        self.directionMethod = self.goalDirection

    def update(self, dt):
        """Aktualisiert Sprites, Zustandsautomat und Zielpunkt basierend auf dem aktuellen Modus."""
        self.sprites.update(dt)
        self.mode.update(dt)

        if self.mode.current == SCATTER:
            self.scatter()
        elif self.mode.current == CHASE:
            self.chase()

        super(Ghost, self).update(dt)

    def scatter(self):
        """Standard-Rückzugsziel (wird in abgeleiteten Klassen überschrieben)."""
        self.goal = Vec2(0, 0)

    def chase(self):
        """Standard-Verfolgungsziel: Direkte Pacman-Position."""
        if self.pacman is not None:
            self.goal = self.pacman.position

    def spawn(self):
        """Ziel während des Respawn-Vorgangs: Zurück ins Geisterhaus."""
        if self.spawnNode is not None:
            self.goal = self.spawnNode.position

    def setSpawnNode(self, node):
        self.spawnNode = node

    def startSpawn(self):
        """Aktiviert den Respawn-Modus (Augen fliegen mit erhöhter Geschwindigkeit zur Basis)."""
        self.mode.setSpawnMode()
        if self.mode.current == SPAWN:
            # Anpassbar: Geschwindigkeit der Augen beim Zurückfliegen
            self.setSpeed(150)
            self.directionMethod = self.goalDirection
            self.spawn()

    def startFreight(self):
        """Aktiviert den Angst-/Fluchtmodus (Geister werden blau und verlangsamt)."""
        self.mode.setFreightMode()
        if self.mode.current == FREIGHT:
            # Anpassbar: Reduzierte Geschwindigkeit im Angstmodus
            self.setSpeed(50)
            self.directionMethod = self.randomDirection

    def normalMode(self):
        """Setzt den Geist auf die reguläre Geschwindigkeit und Zielmethode zurück."""
        self.setSpeed(100)
        self.directionMethod = self.goalDirection
        if self.homeNode is not None:
            self.homeNode.denyAccess(DOWN, self)


# ==========================================
# Individuelle Geister-Implementierungen
# ==========================================

class Blinky(Ghost):
    """Blinky (Rot): Aggressiver Jäger, zielt direkt auf Pacmans aktuelle Position."""
    def __init__(self, node, pacman=None, blinky=None):
        super(Blinky, self).__init__(node, pacman, blinky)
        self.name = BLINKY
        self.color = RED
        self.sprites = GhostVisuals(self)


class Pinky(Ghost):
    """Pinky (Pink): Hinterhalt-Strategie, zielt 4 Kacheln in Pacmans Bewegungsrichtung voraus."""
    def __init__(self, node, pacman=None, blinky=None):
        super(Pinky, self).__init__(node, pacman, blinky)
        self.name = PINKY
        self.color = PINK
        self.sprites = GhostVisuals(self)

    def scatter(self):
        # Obere rechte Ecke
        self.goal = Vec2(TILEWIDTH * NCOLS, 0)

    def chase(self):
        # 4 Kacheln vor Pacman zielen
        if self.pacman is not None:
            lead_vec = self.pacman.directions[self.pacman.direction] * (TILEWIDTH * 4)
            self.goal = self.pacman.position + lead_vec


class Inky(Ghost):
    """Inky (Türkis): Taktischer Flankierer, spiegelt den Vektor von Blinky über einen Punkt vor Pacman."""
    def __init__(self, node, pacman=None, blinky=None):
        super(Inky, self).__init__(node, pacman, blinky)
        self.name = INKY
        self.color = TEAL
        self.sprites = GhostVisuals(self)

    def scatter(self):
        # Untere rechte Ecke
        self.goal = Vec2(TILEWIDTH * NCOLS, TILEHEIGHT * NROWS)

    def chase(self):
        # Vektor-Konstruktion über Blinky und 2 Kacheln vor Pacman
        if self.pacman is not None and self.blinky is not None:
            lead_vec = self.pacman.position + (self.pacman.directions[self.pacman.direction] * (TILEWIDTH * 2))
            offset_from_blinky = (lead_vec - self.blinky.position) * 2.0
            self.goal = self.blinky.position + offset_from_blinky


class Clyde(Ghost):
    """Clyde (Orange): Greift an wenn weit entfernt (> 8 Kacheln), flieht in die Ecke bei Nähe."""
    def __init__(self, node, pacman=None, blinky=None):
        super(Clyde, self).__init__(node, pacman, blinky)
        self.name = CLYDE
        self.color = ORANGE
        self.sprites = GhostVisuals(self)

    def scatter(self):
        # Untere linke Ecke
        self.goal = Vec2(0, TILEHEIGHT * NROWS)

    def chase(self):
        # Anpassbar: Distanzschwelle (8 Kacheln) für Clydes Fluchtverhalten
        if self.pacman is not None:
            delta = self.pacman.position - self.position
            if delta.magnitude_squared() <= ((TILEWIDTH * 8) ** 2):
                self.scatter()
            else:
                lead_vec = self.pacman.directions[self.pacman.direction] * (TILEWIDTH * 4)
                self.goal = self.pacman.position + lead_vec


# ==========================================
# Geister-Gruppen-Manager
# ==========================================

class GhostSquad(object):
    """Verwaltet alle vier Geister als Gruppe und steuert Gruppenaktionen (z.B. Angst-Modus)."""
    def __init__(self, spawn_node, pacman):
        self.blinky = Blinky(spawn_node, pacman)
        self.pinky = Pinky(spawn_node, pacman)
        self.inky = Inky(spawn_node, pacman, self.blinky)
        self.clyde = Clyde(spawn_node, pacman)
        self.ghosts = [self.blinky, self.pinky, self.inky, self.clyde]

    def __iter__(self):
        return iter(self.ghosts)

    def update(self, dt):
        for ghost in self.ghosts:
            ghost.update(dt)

    def startFreight(self):
        """Aktiviert den Angstmodus für alle Geister und setzt den Punkte-Multiplikator zurück."""
        for ghost in self.ghosts:
            ghost.startFreight()
        self.resetPoints()

    def setSpawnNode(self, node):
        for ghost in self.ghosts:
            ghost.setSpawnNode(node)

    def updatePoints(self):
        """Verdoppelt die Punktzahl für jeden weiteren im gleichen Angstmodus gefressenen Geist (200, 400, 800, 1600)."""
        for ghost in self.ghosts:
            ghost.points *= 2

    def resetPoints(self):
        for ghost in self.ghosts:
            ghost.points = 200

    def hide(self):
        for ghost in self.ghosts:
            ghost.visible = False

    def show(self):
        for ghost in self.ghosts:
            ghost.visible = True

    def reset(self):
        for ghost in self.ghosts:
            ghost.reset()

    def render(self, screen):
        for ghost in self.ghosts:
            ghost.render(screen)


# Kompatibilitäts-Alias
GhostGroup = GhostSquad
