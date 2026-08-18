"""
Basis-Akteur-Modul (Actor).
Definiert die universelle Bewegungslogik für alle beweglichen Entitäten (Pacman, Geister, Früchte),
inklusive Kachel-Navigation, Kollisionsgrenzen, Zielsuche und Portal-Teleportation.
"""
import random
import pygame
from math_vec import Vec2
from game_config import (
    TILEWIDTH, TILEHEIGHT, WHITE, STOP, UP, DOWN, LEFT, RIGHT, PORTAL
)

class Actor(object):
    """
    Basisklasse für alle sich auf dem Navigationsgraphen bewegenden Entitäten.
    """
    def __init__(self, node):
        self.name = None
        # Vektorielle Richtungszuordnung
        self.directions = {
            UP: Vec2(0, -1),
            DOWN: Vec2(0, 1),
            LEFT: Vec2(-1, 0),
            RIGHT: Vec2(1, 0),
            STOP: Vec2(0, 0)
        }
        self.direction = STOP
        
        # Anpassbar: Grundgeschwindigkeit und Kollisionsradien für Hitboxen
        self.speed = 100.0
        self.radius = 10
        self.collideRadius = 5
        self.color = WHITE
        self.visible = True
        self.disablePortal = False
        self.goal = None
        self.directionMethod = self.randomDirection
        self.node = None
        self.startNode = None
        self.target = None
        self.position = Vec2()
        self.image = None
        
        self.setSpeed(100)
        self.setStartNode(node)

    def setPosition(self):
        """Setzt die Position der Entität exakt auf den aktuellen Knotenpunkt."""
        if self.node is not None:
            self.position = self.node.position.copy()

    def update(self, dt):
        """
        Bewegt die Entität kontinuierlich entlang ihrer aktuellen Richtung.
        Bei Erreichen oder Überschreiten des Zielknotens wird die nächste gültige Richtung ermittelt.
        """
        step_vec = self.directions[self.direction] * (self.speed * dt)
        self.position += step_vec

        if self.overshotTarget():
            self.node = self.target
            valid_dirs = self.validDirections()
            chosen_dir = self.directionMethod(valid_dirs)

            # Portal-Überprüfung (Teleportation durch den Seitentunnel)
            if not self.disablePortal:
                if self.node.neighbors[PORTAL] is not None:
                    self.node = self.node.neighbors[PORTAL]

            self.target = self.getNewTarget(chosen_dir)
            if self.target is not self.node:
                self.direction = chosen_dir
            else:
                self.target = self.getNewTarget(self.direction)

            self.setPosition()

    def validDirection(self, direction):
        """Prüft, ob die Entität in die angegebene Richtung abbiegen darf."""
        if direction != STOP and self.node is not None:
            if direction in self.node.access and self.name in self.node.access[direction]:
                if self.node.neighbors.get(direction) is not None:
                    return True
        return False

    def getNewTarget(self, direction):
        """Gibt den Nachbarknoten in der gewählten Richtung zurück oder verbleibt auf dem aktuellen Knoten."""
        if self.validDirection(direction):
            return self.node.neighbors[direction]
        return self.node

    def overshotTarget(self):
        """Ermittelt, ob die Entität über den Zielknoten hinausgefahren ist."""
        if self.target is not None and self.node is not None:
            delta_target = self.target.position - self.node.position
            delta_pos = self.position - self.node.position
            return delta_pos.magnitude_squared() >= delta_target.magnitude_squared()
        return False

    def reverseDirection(self):
        """Kehrt die Fahrtrichtung sofort um und tauscht aktuellen Knoten und Zielknoten."""
        self.direction *= -1
        self.node, self.target = self.target, self.node

    def oppositeDirection(self, direction):
        """Prüft, ob eine Richtung der aktuellen Gegenrichtung entspricht."""
        return (direction != STOP) and (direction == self.direction * -1)

    def validDirections(self):
        """
        Gibt alle möglichen Abzweigungen zurück.
        Ein direktes Umdrehen ist verboten, außer es handelt sich um eine Sackgasse.
        """
        choices = []
        for d in (UP, DOWN, LEFT, RIGHT):
            if self.validDirection(d):
                if d != self.direction * -1:
                    choices.append(d)
        if not choices:
            choices.append(self.direction * -1)
        return choices

    def randomDirection(self, directions):
        """Wählt eine zufällige Richtung aus (z. B. für Geister im Fluchtmodus)."""
        return random.choice(directions) if directions else STOP

    def goalDirection(self, directions):
        """
        Wählt die Richtung, deren nächster Knoten die geringste Distanz zum Zielpunkt (Goal) aufweist.
        Kern der klassischen Arcade-Geister-Wegfindung.
        """
        if not directions:
            return STOP
        best_dir = directions[0]
        min_dist_sq = float('inf')
        for d in directions:
            future_node_pos = self.node.position + (self.directions[d] * TILEWIDTH)
            dist_sq = (future_node_pos - self.goal).magnitude_squared()
            if dist_sq < min_dist_sq:
                min_dist_sq = dist_sq
                best_dir = d
        return best_dir

    def setStartNode(self, node):
        """Setzt den Startknoten und initialisiert die Zielpunkte."""
        self.node = node
        self.startNode = node
        self.target = node
        self.setPosition()

    def setBetweenNodes(self, direction):
        """Platziert die Entität genau in die Mitte zwischen dem aktuellen und dem nächsten Knoten."""
        if self.node is not None and self.node.neighbors.get(direction) is not None:
            self.target = self.node.neighbors[direction]
            self.position = (self.node.position + self.target.position) / 2.0

    def reset(self):
        """Setzt die Entität auf ihren Ausgangszustand zurück."""
        self.setStartNode(self.startNode)
        self.direction = STOP
        self.speed = 100.0
        self.visible = True

    # Anpassbar: Skalierung der Geschwindigkeit proportional zur Kachelgröße
    def setSpeed(self, speed_val):
        self.speed = float(speed_val) * (TILEWIDTH / 16.0)

    # Zeichnen des Sprites oder Fallback-Kreises
    def render(self, screen):
        if not self.visible:
            return
        if self.image is not None:
            half_offset = Vec2(TILEWIDTH, TILEHEIGHT) / 2.0
            blit_coord = self.position - half_offset
            screen.blit(self.image, blit_coord.as_tuple())
        else:
            # Fallback falls keine Sprites geladen sind
            pygame.draw.circle(screen, self.color, self.position.as_int(), self.radius)


# Kompatibilitäts-Alias
Entity = Actor
