"""
Grafik-Engine & Sprite-Management.
Verarbeitet Spritesheets, extrahiert Einzel-Frames für Animationen,
rotiert Kacheln und baut die grafische Labyrinth-Oberfläche dynamisch zusammen.
"""
import pygame
import numpy as np
from game_config import (
    TILEWIDTH, TILEHEIGHT, LEFT, RIGHT, UP, DOWN, STOP,
    BLINKY, PINKY, INKY, CLYDE, SCATTER, CHASE, FREIGHT, SPAWN, DEATH_ANIM,
    SPRITESHEET_FILE
)
from animator import SpriteAnimator

BASE_TILE_W = 16
BASE_TILE_H = 16

class SpriteSheetAsset(object):
    """
    Lädt das Spritesheet-Bild, skaliert es proportional zur Ziel-Kachelgröße
    und schneidet Kachel-Rechtecke für Animationen aus.
    """
    # Anpassbar: Bilddatei des Spritesheets (Standardwert kommt aus game_config.py)
    def __init__(self, image_file=SPRITESHEET_FILE):
        raw_sheet = pygame.image.load(image_file).convert()
        # Transparenz über die Farbe des ersten Pixels (oben links) definieren
        key_color = raw_sheet.get_at((0, 0))
        raw_sheet.set_colorkey(key_color)

        scale_w = int(raw_sheet.get_width() / BASE_TILE_W * TILEWIDTH)
        scale_h = int(raw_sheet.get_height() / BASE_TILE_H * TILEHEIGHT)
        self.sheet = pygame.transform.scale(raw_sheet, (scale_w, scale_h))

    def getImage(self, x, y, width, height):
        """Schneidet einen rechteckigen Bereich aus dem Spritesheet als Subsurface aus."""
        clip_rect = pygame.Rect(x * TILEWIDTH, y * TILEHEIGHT, width, height)
        self.sheet.set_clip(clip_rect)
        return self.sheet.subsurface(self.sheet.get_clip())


# ==========================================
# Pacman-Animationen
# ==========================================

class PacmanVisuals(SpriteSheetAsset):
    """
    Verwaltet die Richtungs- und Todes-Animationen von Pacman.
    """
    def __init__(self, entity):
        super(PacmanVisuals, self).__init__()
        self.entity = entity
        self.animations = {}
        self._init_animations()
        self.stop_coords = (8, 0)
        self.entity.image = self.getStartImage()

    def _init_animations(self):
        """
        Anpassbar: Kachelkoordinaten (Spalte, Zeile) auf dem Spritesheet für die Animationen.
        """
        self.animations[LEFT] = SpriteAnimator(((8, 0), (0, 0), (0, 2), (0, 0)))
        self.animations[RIGHT] = SpriteAnimator(((10, 0), (2, 0), (2, 2), (2, 0)))
        self.animations[UP] = SpriteAnimator(((10, 2), (6, 0), (6, 2), (6, 0)))
        self.animations[DOWN] = SpriteAnimator(((8, 2), (4, 0), (4, 2), (4, 0)))
        
        # Frames und Ablaufgeschwindigkeit der Todesanimation
        death_frames = (
            (0, 12), (2, 12), (4, 12), (6, 12), (8, 12),
            (10, 12), (12, 12), (14, 12), (16, 12), (18, 12), (20, 12)
        )
        self.animations[DEATH_ANIM] = SpriteAnimator(death_frames, fps=6, loop=False)

    def defineAnimations(self):
        self._init_animations()

    def update(self, dt):
        """Wählt das passende Sprite-Frame basierend auf Lebenszustand und Blickrichtung."""
        if self.entity.alive:
            dir_code = self.entity.direction
            if dir_code == LEFT:
                frame_coords = self.animations[LEFT].update(dt)
                self.entity.image = self.getImage(*frame_coords)
                self.stop_coords = (8, 0)
            elif dir_code == RIGHT:
                frame_coords = self.animations[RIGHT].update(dt)
                self.entity.image = self.getImage(*frame_coords)
                self.stop_coords = (10, 0)
            elif dir_code == DOWN:
                frame_coords = self.animations[DOWN].update(dt)
                self.entity.image = self.getImage(*frame_coords)
                self.stop_coords = (8, 2)
            elif dir_code == UP:
                frame_coords = self.animations[UP].update(dt)
                self.entity.image = self.getImage(*frame_coords)
                self.stop_coords = (10, 2)
            elif dir_code == STOP:
                self.entity.image = self.getImage(*self.stop_coords)
        else:
            death_frame = self.animations[DEATH_ANIM].update(dt)
            self.entity.image = self.getImage(*death_frame)

    def reset(self):
        for anim in self.animations.values():
            anim.reset()

    def getStartImage(self):
        return self.getImage(8, 0)

    def getImage(self, x, y):
        # 2x2 Kacheln Größe für Figuren
        return super(PacmanVisuals, self).getImage(x, y, 2 * TILEWIDTH, 2 * TILEHEIGHT)


# ==========================================
# Geister-Animationen & Grafiken
# ==========================================

class GhostVisuals(SpriteSheetAsset):
    """
    Verwaltet die Richtungs-Sprites, blauen Angst-Sprites und Augen-Sprites für Geister.
    """
    # Anpassbar: Spalten-Offsets auf dem Spritesheet für Blinky, Pinky, Inky und Clyde
    GHOST_X_COLS = {BLINKY: 0, PINKY: 2, INKY: 4, CLYDE: 6}

    def __init__(self, entity):
        super(GhostVisuals, self).__init__()
        self.entity = entity
        self.x = self.GHOST_X_COLS
        self.entity.image = self.getStartImage()

    def update(self, dt):
        col_x = self.x.get(self.entity.name, 0)
        mode = self.entity.mode.current

        if mode in (SCATTER, CHASE):
            dir_code = self.entity.direction
            if dir_code == LEFT:
                self.entity.image = self.getImage(col_x, 8)
            elif dir_code == RIGHT:
                self.entity.image = self.getImage(col_x, 10)
            elif dir_code == DOWN:
                self.entity.image = self.getImage(col_x, 6)
            elif dir_code == UP:
                self.entity.image = self.getImage(col_x, 4)
        elif mode == FREIGHT:
            # Blaues Sprite für den Flucht-/Angstmodus
            self.entity.image = self.getImage(10, 4)
        elif mode == SPAWN:
            # Augen-Sprites während der Rückkehr ins Geisterhaus
            dir_code = self.entity.direction
            if dir_code == LEFT:
                self.entity.image = self.getImage(8, 8)
            elif dir_code == RIGHT:
                self.entity.image = self.getImage(8, 10)
            elif dir_code == DOWN:
                self.entity.image = self.getImage(8, 6)
            elif dir_code == UP:
                self.entity.image = self.getImage(8, 4)

    def getStartImage(self):
        return self.getImage(self.x.get(self.entity.name, 0), 4)

    def getImage(self, x, y):
        return super(GhostVisuals, self).getImage(x, y, 2 * TILEWIDTH, 2 * TILEHEIGHT)


# ==========================================
# Früchte- & UI-Grafiken
# ==========================================

class FruitVisuals(SpriteSheetAsset):
    """Verwaltet die Sprite-Offsets für Bonusfrüchte je nach aktuellem Level."""
    # Anpassbar: Koordinaten der verschiedenen Früchte (Kirsche, Erdbeere, Orange, Apfel, etc.)
    FRUIT_OFFSETS = {
        0: (16, 8), 1: (18, 8), 2: (20, 8),
        3: (16, 10), 4: (18, 10), 5: (20, 10)
    }

    def __init__(self, entity, level):
        super(FruitVisuals, self).__init__()
        self.entity = entity
        self.fruits = self.FRUIT_OFFSETS
        self.entity.image = self.getStartImage(level % len(self.fruits))

    def getStartImage(self, key):
        return self.getImage(*self.fruits[key])

    def getImage(self, x, y):
        return super(FruitVisuals, self).getImage(x, y, 2 * TILEWIDTH, 2 * TILEHEIGHT)


class LivesVisuals(SpriteSheetAsset):
    """Verwaltet die Icons für verbleibende Leben in der unteren Leiste."""
    def __init__(self, num_lives):
        super(LivesVisuals, self).__init__()
        self.images = []
        self.resetLives(num_lives)

    def removeImage(self):
        if self.images:
            self.images.pop(0)

    def resetLives(self, num_lives):
        self.images = [self.getImage(0, 0) for _ in range(num_lives)]

    def getImage(self, x, y):
        return super(LivesVisuals, self).getImage(x, y, 2 * TILEWIDTH, 2 * TILEHEIGHT)


class MazeBackgroundRenderer(SpriteSheetAsset):
    """
    Baut das Labyrinth-Hintergrundbild aus den Kachel-Definitionen und Rotationsdaten zusammen.
    """
    def __init__(self, map_file, rotation_file):
        super(MazeBackgroundRenderer, self).__init__()
        self.data = np.loadtxt(map_file, dtype='<U1')
        self.rotdata = np.loadtxt(rotation_file, dtype='<U1')

    def getImage(self, x, y):
        return super(MazeBackgroundRenderer, self).getImage(x, y, TILEWIDTH, TILEHEIGHT)

    def rotate(self, sprite, angle_multiplier):
        """Rotiert ein Kachel-Sprite um ein Vielfaches von 90 Grad."""
        return pygame.transform.rotate(sprite, angle_multiplier * 90)

    def constructBackground(self, surface, row_theme):
        """Rendert die Wandsegmente und Geisterhaus-Türen auf die Ziel-Surface."""
        rows, cols = self.data.shape
        for r in range(rows):
            for c in range(cols):
                char = self.data[r][c]
                if char.isdigit():
                    tile_col = int(char) + 12
                    tile_sprite = self.getImage(tile_col, row_theme)
                    rot_factor = int(self.rotdata[r][c])
                    rotated = self.rotate(tile_sprite, rot_factor)
                    surface.blit(rotated, (c * TILEWIDTH, r * TILEHEIGHT))
                elif char == '=':
                    door_sprite = self.getImage(10, 8)
                    surface.blit(door_sprite, (c * TILEWIDTH, r * TILEHEIGHT))
        return surface


# Kompatibilitäts-Aliase
Spritesheet = SpriteSheetAsset
PacmanSprites = PacmanVisuals
GhostSprites = GhostVisuals
FruitSprites = FruitVisuals
LifeSprites = LivesVisuals
MazeSprites = MazeBackgroundRenderer
