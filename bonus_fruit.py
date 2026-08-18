"""
Bonusfrüchte-Modul (BonusFruit).
Erzeugt zeitlich begrenzte Bonusfrüchte mit levelabhängiger Punktevergabe,
die nach dem Fressen bestimmter Pellet-Schwellenwerte im Labyrinth erscheinen.
"""
from actor import Actor
from game_config import FRUIT, GREEN, RIGHT
from graphics_engine import FruitVisuals

class BonusFruit(Actor):
    """
    Bonusfrucht, die für eine begrenzte Zeit im Labyrinth erscheint.
    """
    def __init__(self, node, level=0):
        super(BonusFruit, self).__init__(node)
        self.name = FRUIT
        self.color = GREEN
        # Anpassbar: Anzeigedauer der Frucht in Sekunden (Standard: 5 Sekunden)
        self.lifespan = 5.0
        self.timer = 0.0
        self.destroy = False
        # Anpassbar: Punkteberechnung basierend auf dem aktuellen Level
        self.points = 100 + level * 20
        self.setBetweenNodes(RIGHT)
        # Grafische Repräsentation aus dem Spritesheet laden
        self.sprites = FruitVisuals(self, level)

    def update(self, dt):
        """Zählt die Lebensdauer herunter und markiert die Frucht nach Ablauf zur Zerstörung."""
        self.timer += dt
        if self.timer >= self.lifespan:
            self.destroy = True


# Kompatibilitäts-Alias
Fruit = BonusFruit
