"""
Navigationsgraph & Wegpunkt-Modul.
Erstellt aus den Map-Textdateien ein diskretes Wegenetzwerk aus Knotenpunkten (Intersections)
und Nachbarschaftsverbindungen, verwaltet Portale und Zugriffsrechte (z. B. Geisterhaus-Sperren).
"""
import pygame
import numpy as np
from math_vec import Vec2
from game_config import (
    TILEWIDTH, TILEHEIGHT, WHITE, RED,
    UP, DOWN, LEFT, RIGHT, PORTAL,
    PACMAN, BLINKY, PINKY, INKY, CLYDE, FRUIT
)

ALL_ACTOR_TYPES = [PACMAN, BLINKY, PINKY, INKY, CLYDE, FRUIT]

class NavNode(object):
    """
    Repräsentiert einen Knotenpunkt bzw. eine Kreuzung im Labyrinth-Graphen.
    """
    def __init__(self, x, y):
        self.position = Vec2(x, y)
        self.neighbors = {UP: None, DOWN: None, LEFT: None, RIGHT: None, PORTAL: None}
        # Zugriffsbeschränkungen für jede Richtung (z. B. nur bestimmte Entitäten dürfen passieren)
        self.access = {
            UP: list(ALL_ACTOR_TYPES),
            DOWN: list(ALL_ACTOR_TYPES),
            LEFT: list(ALL_ACTOR_TYPES),
            RIGHT: list(ALL_ACTOR_TYPES)
        }

    def denyAccess(self, direction, entity):
        """Sperrt eine Richtung für eine bestimmte Entität."""
        if direction in self.access and entity.name in self.access[direction]:
            self.access[direction].remove(entity.name)

    def allowAccess(self, direction, entity):
        """Erlaubt einer Entität das Betreten in die angegebene Richtung."""
        if direction in self.access and entity.name not in self.access[direction]:
            self.access[direction].append(entity.name)

    def render(self, screen):
        """Debug-Visualisierung des Graphennetzwerks."""
        for neighbor in self.neighbors.values():
            if neighbor is not None:
                start_p = self.position.as_tuple()
                end_p = neighbor.position.as_tuple()
                pygame.draw.line(screen, WHITE, start_p, end_p, 4)
                pygame.draw.circle(screen, RED, self.position.as_int(), 12)


class NavigationGraph(object):
    """
    Erstellt den vollständigen Navigationsgraphen aus einer Map-Matrix.
    """
    # Symbole aus der Textdatei, die als Knotenpunkte (Wegekreuzungen) interpretiert werden
    NODE_SYMBOLS = {'+', 'P', 'n'}
    # Symbole, die als durchgehende Pfade zwischen Knoten interpretiert werden
    PATH_SYMBOLS = {'.', '-', '|', 'p'}

    def __init__(self, map_file):
        self.nodesLUT = {}
        self.homekey = None
        self.build_from_file(map_file)

    def build_from_file(self, map_file):
        """Liest die Textdatei ein und verknüpft Knotenpunkte horizontal und vertikal."""
        grid_data = np.loadtxt(map_file, dtype='<U1')
        self.createNodeTable(grid_data)
        self.connectHorizontally(grid_data)
        self.connectVertically(grid_data)

    def constructKey(self, col, row):
        """Erzeugt einen eindeutigen Schlüssel basierend auf Pixelkoordinaten."""
        return col * TILEWIDTH, row * TILEHEIGHT

    def createNodeTable(self, grid_data, x_off=0, y_off=0):
        rows, cols = grid_data.shape
        for r in range(rows):
            for c in range(cols):
                if grid_data[r][c] in self.NODE_SYMBOLS:
                    key = self.constructKey(c + x_off, r + y_off)
                    self.nodesLUT[key] = NavNode(*key)

    def connectHorizontally(self, grid_data, x_off=0, y_off=0):
        """Verbindet benachbarte Knoten entlang horizontaler Pfade."""
        rows, cols = grid_data.shape
        for r in range(rows):
            prev_key = None
            for c in range(cols):
                val = grid_data[r][c]
                if val in self.NODE_SYMBOLS:
                    curr_key = self.constructKey(c + x_off, r + y_off)
                    if prev_key is not None:
                        self.nodesLUT[prev_key].neighbors[RIGHT] = self.nodesLUT[curr_key]
                        self.nodesLUT[curr_key].neighbors[LEFT] = self.nodesLUT[prev_key]
                    prev_key = curr_key
                elif val not in self.PATH_SYMBOLS:
                    prev_key = None

    def connectVertically(self, grid_data, x_off=0, y_off=0):
        """Verbindet benachbarte Knoten entlang vertikaler Pfade."""
        grid_t = grid_data.transpose()
        cols, rows = grid_t.shape
        for c in range(cols):
            prev_key = None
            for r in range(rows):
                val = grid_t[c][r]
                if val in self.NODE_SYMBOLS:
                    curr_key = self.constructKey(c + x_off, r + y_off)
                    if prev_key is not None:
                        self.nodesLUT[prev_key].neighbors[DOWN] = self.nodesLUT[curr_key]
                        self.nodesLUT[curr_key].neighbors[UP] = self.nodesLUT[prev_key]
                    prev_key = curr_key
                elif val not in self.PATH_SYMBOLS:
                    prev_key = None

    def getStartTempNode(self):
        """Gibt einen beliebigen Startknoten zurück (z. B. für die Geisterinitialisierung)."""
        return next(iter(self.nodesLUT.values()))

    def setPortalPair(self, pair1, pair2):
        """Verbindet zwei Portal-Knoten miteinander (Tunnel-Teleportation)."""
        key1 = self.constructKey(*pair1)
        key2 = self.constructKey(*pair2)
        if key1 in self.nodesLUT and key2 in self.nodesLUT:
            self.nodesLUT[key1].neighbors[PORTAL] = self.nodesLUT[key2]
            self.nodesLUT[key2].neighbors[PORTAL] = self.nodesLUT[key1]

    def createHomeNodes(self, xoffset, yoffset):
        """Erstellt die interne Knotenstruktur für das zentrale Geisterhaus."""
        home_matrix = np.array([
            ['X', 'X', '+', 'X', 'X'],
            ['X', 'X', '.', 'X', 'X'],
            ['+', 'X', '.', 'X', '+'],
            ['+', '.', '+', '.', '+'],
            ['+', 'X', 'X', 'X', '+']
        ])
        self.createNodeTable(home_matrix, xoffset, yoffset)
        self.connectHorizontally(home_matrix, xoffset, yoffset)
        self.connectVertically(home_matrix, xoffset, yoffset)
        self.homekey = self.constructKey(xoffset + 2, yoffset)
        return self.homekey

    def connectHomeNodes(self, home_key, other_tile, direction):
        other_key = self.constructKey(*other_tile)
        if home_key in self.nodesLUT and other_key in self.nodesLUT:
            self.nodesLUT[home_key].neighbors[direction] = self.nodesLUT[other_key]
            self.nodesLUT[other_key].neighbors[direction * -1] = self.nodesLUT[home_key]

    def getNodeFromPixels(self, x_px, y_px):
        return self.nodesLUT.get((x_px, y_px), None)

    def getNodeFromTiles(self, col, row):
        """Sucht den Knoten anhand von Kachelkoordinaten (Spalte, Zeile)."""
        return self.nodesLUT.get(self.constructKey(col, row), None)

    def denyAccess(self, col, row, direction, entity):
        target_node = self.getNodeFromTiles(col, row)
        if target_node is not None:
            target_node.denyAccess(direction, entity)

    def allowAccess(self, col, row, direction, entity):
        target_node = self.getNodeFromTiles(col, row)
        if target_node is not None:
            target_node.allowAccess(direction, entity)

    def denyAccessList(self, col, row, direction, entities):
        for ent in entities:
            self.denyAccess(col, row, direction, ent)

    def allowAccessList(self, col, row, direction, entities):
        for ent in entities:
            self.allowAccess(col, row, direction, ent)

    def denyHomeAccess(self, entity):
        """Verhindert, dass Pacman das Geisterhaus betreten kann."""
        if self.homekey in self.nodesLUT:
            self.nodesLUT[self.homekey].denyAccess(DOWN, entity)

    def allowHomeAccess(self, entity):
        if self.homekey in self.nodesLUT:
            self.nodesLUT[self.homekey].allowAccess(DOWN, entity)

    def denyHomeAccessList(self, entities):
        for ent in entities:
            self.denyHomeAccess(ent)

    def allowHomeAccessList(self, entities):
        for ent in entities:
            self.allowHomeAccess(ent)

    def render(self, screen):
        for node in self.nodesLUT.values():
            node.render(screen)


# Kompatibilitäts-Aliase
Node = NavNode
NodeGroup = NavigationGraph
