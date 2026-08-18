"""
UI- & HUD-Overlay-Manager.
Rendert Bitmap-Schriftarten, Punktestand, Level-Indikatoren, Status-Banner
(READY!, PAUSED!, GAMEOVER!) und temporäre Punkte-Popups beim Fressen von Geistern und Früchten.
"""
import pygame
from math_vec import Vec2
from game_config import (
    TILEWIDTH, TILEHEIGHT, WHITE, YELLOW,
    SCORETXT, LEVELTXT, READYTXT, PAUSETXT, GAMEOVERTXT
)

# Anpassbar: Schriftart-Datei (Standard: PressStart2P-Regular.ttf)
DEFAULT_FONT = "PressStart2P-Regular.ttf"

class HudTextItem(object):
    """
    Repräsentiert ein einzelnes Text-Element auf der Bildschirmoberfläche.
    """
    def __init__(self, text, color, x, y, size, time=None, id=None, visible=True, font_file=DEFAULT_FONT):
        self.id = id
        self.text = str(text)
        # Anpassbar: Textfarbe
        self.color = color
        # Anpassbar: Schriftgröße
        self.size = size
        self.visible = visible
        self.position = Vec2(x, y)
        self.timer = 0.0
        self.lifespan = time
        self.destroy = False
        self.font = pygame.font.Font(font_file, self.size)
        self.label = None
        self._render_surface()

    def _render_surface(self):
        """Rendert die Text-Surface neu."""
        self.label = self.font.render(self.text, True, self.color)

    def setText(self, new_text):
        """Aktualisiert den Textinhalt."""
        self.text = str(new_text)
        self._render_surface()

    def update(self, dt):
        """Timer für temporäre Texte (z. B. 200 Punkte-Anzeige nach Geisterkollision)."""
        if self.lifespan is not None:
            self.timer += dt
            if self.timer >= self.lifespan:
                self.timer = 0.0
                self.lifespan = None
                self.destroy = True

    def render(self, screen):
        if self.visible and self.label is not None:
            pos = self.position.as_tuple()
            screen.blit(self.label, pos)


class HudManager(object):
    """
    Verwaltet das gesamte HUD-Layout, Scoreboards und dynamische Text-Meldungen.
    """
    def __init__(self):
        self.nextid = 10
        self.alltext = {}
        self._init_layout()
        self.showText(READYTXT)

    def addText(self, text, color, x, y, size, time=None, id=None):
        """Fügt ein neues dynamisches Text-Element hinzu und gibt dessen ID zurück."""
        self.nextid += 1
        item = HudTextItem(text, color, x, y, size, time=time, id=id)
        self.alltext[self.nextid] = item
        return self.nextid

    def removeText(self, item_id):
        if item_id in self.alltext:
            del self.alltext[item_id]

    def _init_layout(self):
        """
        Anpassbar: Initiales Layout für Punktestand, Level und Status-Banner.
        """
        font_sz = TILEHEIGHT
        self.alltext[SCORETXT] = HudTextItem("0".zfill(8), WHITE, 0, TILEHEIGHT, font_sz)
        self.alltext[LEVELTXT] = HudTextItem(str(1).zfill(3), WHITE, 23 * TILEWIDTH, TILEHEIGHT, font_sz)
        self.alltext[READYTXT] = HudTextItem("READY!", YELLOW, 11.25 * TILEWIDTH, 20 * TILEHEIGHT, font_sz, visible=False)
        self.alltext[PAUSETXT] = HudTextItem("PAUSED!", YELLOW, 10.625 * TILEWIDTH, 20 * TILEHEIGHT, font_sz, visible=False)
        self.alltext[GAMEOVERTXT] = HudTextItem("GAMEOVER!", YELLOW, 10 * TILEWIDTH, 20 * TILEHEIGHT, font_sz, visible=False)
        
        # Statische Titelzeilen
        self.addText("SCORE", WHITE, 0, 0, font_sz)
        self.addText("LEVEL", WHITE, 23 * TILEWIDTH, 0, font_sz)

    def setupText(self):
        self._init_layout()

    def update(self, dt):
        for key in list(self.alltext.keys()):
            item = self.alltext[key]
            item.update(dt)
            if item.destroy:
                self.removeText(key)

    def showText(self, text_id):
        """Zeigt ein Status-Banner an und blendet alle anderen aus."""
        self.hideText()
        if text_id in self.alltext:
            self.alltext[text_id].visible = True

    def hideText(self):
        """Blendet temporäre Status-Banner (READY, PAUSED, GAMEOVER) aus."""
        for banner in (READYTXT, PAUSETXT, GAMEOVERTXT):
            if banner in self.alltext:
                self.alltext[banner].visible = False

    def updateScore(self, score):
        """Aktualisiert die 8-stellige Score-Anzeige."""
        self.updateText(SCORETXT, str(score).zfill(8))

    def updateLevel(self, level):
        """Aktualisiert die 3-stellige Level-Anzeige."""
        self.updateText(LEVELTXT, str(level + 1).zfill(3))

    def updateText(self, text_id, new_val):
        if text_id in self.alltext:
            self.alltext[text_id].setText(new_val)

    def render(self, screen):
        for item in self.alltext.values():
            item.render(screen)


# Kompatibilitäts-Aliase
Text = HudTextItem
TextGroup = HudManager
