"""
Spieler-Modul (PacmanPlayer).
Implementiert die Steuerung für den Spieler, Tastaturabfragen (Pfeiltasten & WASD),
Kollisionsabfragen für Pellets und Geister sowie die Todessequenz.
"""
import pygame
from pygame.locals import K_UP, K_DOWN, K_LEFT, K_RIGHT, K_w, K_s, K_a, K_d
from actor import Actor
from game_config import (
    PACMAN, YELLOW, LEFT, RIGHT, UP, DOWN, STOP, PORTAL
)
from graphics_engine import PacmanVisuals

class PacmanPlayer(Actor):
    """
    Repräsentiert die vom Spieler gesteuerte Pacman-Figur.
    """
    def __init__(self, start_node):
        super(PacmanPlayer, self).__init__(start_node)
        self.name = PACMAN
        # Fallback-Farbe wenn keine Grafik geladen ist
        self.color = YELLOW
        # Start-Blickrichtung
        self.direction = LEFT
        self.setBetweenNodes(LEFT)
        self.alive = True
        # Zuweisung des Sprite-Managers für Animationen
        self.sprites = PacmanVisuals(self)

    def reset(self):
        """Setzt Pacman nach Lebensverlust oder bei einem neuen Level zurück."""
        super(PacmanPlayer, self).reset()
        self.direction = LEFT
        self.setBetweenNodes(LEFT)
        self.alive = True
        self.image = self.sprites.getStartImage()
        self.sprites.reset()

    def die(self):
        """Leitet den Todeszustand von Pacman ein."""
        self.alive = False
        self.direction = STOP

    def update(self, dt):
        """
        Aktualisiert Animation, Bewegung und prüft Richtungswechsel anhand der gepufferten Tasteneingabe.
        """
        self.sprites.update(dt)
        self.position += self.directions[self.direction] * (self.speed * dt)

        # Tasteneingabe des Spielers ermitteln
        buffered_dir = self.getValidKey()

        if self.overshotTarget():
            self.node = self.target
            if self.node.neighbors.get(PORTAL) is not None:
                self.node = self.node.neighbors[PORTAL]

            new_target = self.getNewTarget(buffered_dir)
            if new_target is not self.node:
                self.direction = buffered_dir
                self.target = new_target
            else:
                self.target = self.getNewTarget(self.direction)

            if self.target is self.node:
                self.direction = STOP

            self.setPosition()
        else:
            # Sofortige Richtungsumkehr erlauben, wenn in die Gegenrichtung gedrückt wird
            if self.oppositeDirection(buffered_dir):
                self.reverseDirection()

    def getValidKey(self):
        """
        Anpassbar: Tastaturabfrage für die Steuerung.
        Unterstützt standardmäßig Pfeiltasten und W/A/S/D.
        """
        keys = pygame.key.get_pressed()
        if keys[K_UP] or keys[K_w]:
            return UP
        if keys[K_DOWN] or keys[K_s]:
            return DOWN
        if keys[K_LEFT] or keys[K_a]:
            return LEFT
        if keys[K_RIGHT] or keys[K_d]:
            return RIGHT
        return STOP

    def eatPellets(self, pellet_list):
        """Prüft, ob Pacman ein Pellet berührt und gibt dieses zurück."""
        for pellet in pellet_list:
            if self.collideCheck(pellet):
                return pellet
        return None

    def collideGhost(self, ghost):
        """Kollisionsprüfung zwischen Pacman und einem Geist."""
        return self.collideCheck(ghost)

    def collideCheck(self, other):
        """
        Allgemeine kreisförmige Kollisionsprüfung basierend auf den Kollisionsradien.
        """
        if other is None:
            return False
        delta = self.position - other.position
        dist_sq = delta.magnitude_squared()
        reach = self.collideRadius + other.collideRadius
        return dist_sq <= (reach * reach)


# Kompatibilitäts-Alias
Pacman = PacmanPlayer
