"""
Sammelobjekte & Pellets-Modul.
Verwaltet reguläre Punkte-Pellets, blinkende Power-Pellets (Energizer)
sowie das Einlesen der Kachel-Symbole aus den Map-Textdateien.
"""
import pygame
import numpy as np
from math_vec import Vec2
from game_config import (
    TILEWIDTH, TILEHEIGHT, WHITE, PELLET, POWERPELLET
)

class PelletDot(object):
    """
    Standard-Punktepellet, das im Labyrinth verteilt ist.
    """
    def __init__(self, row, col):
        self.name = PELLET
        self.position = Vec2(col * TILEWIDTH, row * TILEHEIGHT)
        # Anpassbar: Farbe, Punktwert und Radius für Standard-Pellets
        self.color = WHITE
        self.radius = int(2.0 * TILEWIDTH / 16.0)
        self.collideRadius = 2.0 * TILEWIDTH / 16.0
        self.points = 10
        self.visible = True

    def render(self, screen):
        """Zeichnet das Pellet zentriert auf seiner Kachelposition."""
        if self.visible:
            center_offset = Vec2(TILEWIDTH, TILEHEIGHT) / 2.0
            draw_pos = self.position + center_offset
            pygame.draw.circle(screen, self.color, draw_pos.as_int(), self.radius)


class EnergizerDot(PelletDot):
    """
    Großes Power-Pellet, das blinkt und Geister in den Angst-Modus versetzt.
    """
    def __init__(self, row, col):
        super(EnergizerDot, self).__init__(row, col)
        self.name = POWERPELLET
        # Anpassbar: Größe, Punktwert und Blink-Intervall für Power-Pellets
        self.radius = int(8.0 * TILEWIDTH / 16.0)
        self.points = 50
        self.flashTime = 0.2
        self.timer = 0.0

    def update(self, dt):
        """Aktualisiert das Blink-Intervall des Power-Pellets."""
        self.timer += dt
        if self.timer >= self.flashTime:
            self.visible = not self.visible
            self.timer = 0.0


class CollectibleManager(object):
    """
    Verwaltet alle aktiven Pellets auf dem Spielfeld und liest diese aus der Map-Textdatei ein.
    """
    def __init__(self, map_file):
        self.pelletList = []
        self.powerpellets = []
        self.numEaten = 0
        self.loadFromMap(map_file)

    def loadFromMap(self, map_file):
        """
        Liest die Map-Textdatei ein:
        - '.' und '+' repräsentieren Standard-Pellets
        - 'P' und 'p' repräsentieren Power-Pellets
        """
        grid_data = np.loadtxt(map_file, dtype='<U1')
        rows, cols = grid_data.shape
        for r in range(rows):
            for c in range(cols):
                symbol = grid_data[r][c]
                if symbol in ('.', '+'):
                    dot = PelletDot(r, c)
                    self.pelletList.append(dot)
                elif symbol in ('P', 'p'):
                    energizer = EnergizerDot(r, c)
                    self.pelletList.append(energizer)
                    self.powerpellets.append(energizer)

    def createPelletList(self, pelletfile):
        self.pelletList = []
        self.powerpellets = []
        self.loadFromMap(pelletfile)

    def update(self, dt):
        for energizer in self.powerpellets:
            energizer.update(dt)

    def isEmpty(self):
        """Prüft, ob alle Pellets im Level aufgefressen wurden (Siegbedingung)."""
        return len(self.pelletList) == 0

    def render(self, screen):
        for item in self.pelletList:
            item.render(screen)


# Kompatibilitäts-Aliase
Pellet = PelletDot
PowerPellet = EnergizerDot
PelletGroup = CollectibleManager
