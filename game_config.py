"""
Zentrale Spielkonfiguration und globale Konstanten.
Enthält alle Dimensionen, Farbpaletten, Richtungs-Enums und Status-IDs für das Projekt.
"""

# ==========================================
# Spielfeld- & Raster-Dimensionen
# ==========================================
# Anpassbar: Grundgröße einer Kachel in Pixeln (Standard: 16x16 Pixel)
TILE_SIZE = 16
TILEWIDTH = TILE_SIZE
TILEHEIGHT = TILE_SIZE

# Labyrinth-Dimensionen (36 Zeilen x 28 Spalten)
NROWS = 36
NCOLS = 28
SCREENWIDTH = NCOLS * TILEWIDTH
SCREENHEIGHT = NROWS * TILEHEIGHT
SCREENSIZE = (SCREENWIDTH, SCREENHEIGHT)

# Anpassbar: Bildwiederholrate (60 FPS für flüssige Bewegungen, 30 FPS für Retro-Look)
FPS = 60

# ==========================================
# Grafik- & Asset-Konfiguration
# ==========================================
# Anpassbar: Aktives Spritesheet (z.B. "spritesheet_mspacman.png", "spritesheet.png", "spritesheet_pacman2.png")
SPRITESHEET_FILE = "spritesheet.png"

# ==========================================
# Farbpalette (RGB)
# ==========================================
# Anpassbar: Hier können die Farbwerte für UI, Geister und Effekte angepasst werden
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
PINK = (255, 100, 150)
TEAL = (100, 255, 255)
ORANGE = (230, 190, 40)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# ==========================================
# Richtungs-Definitionen
# ==========================================
# Hinweis für Entwickler: Gegenüberliegende Richtungen sind das negative Äquivalent (z.B. UP = -DOWN),
# was einfache Richtungsumkehrungen per `direction *= -1` ermöglicht.
STOP = 0
UP = 1
DOWN = -1
LEFT = 2
RIGHT = -2
PORTAL = 3

# ==========================================
# Entitäts-IDs
# ==========================================
PACMAN = 0
PELLET = 1
POWERPELLET = 2
GHOST = 3
BLINKY = 4
PINKY = 5
INKY = 6
CLYDE = 7
FRUIT = 8

# ==========================================
# Geister-KI-Zustände
# ==========================================
# SCATTER: Geister ziehen sich in ihre Ecken zurück
# CHASE: Geister verfolgen Pacman nach ihrer individuellen Ziel-Logik
# FREIGHT: Geister sind blau/verwundbar nach einem Power-Pellet
# SPAWN: Geist wurde gefressen und kehrt als Augen zum Geisterhaus zurück
SCATTER = 0
CHASE = 1
FREIGHT = 2
SPAWN = 3

# ==========================================
# HUD & UI Text-IDs
# ==========================================
SCORETXT = 0
LEVELTXT = 1
READYTXT = 2
PAUSETXT = 3
GAMEOVERTXT = 4

# Animations-Index für die Todessequenz
DEATH_ANIM = 5
