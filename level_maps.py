"""
Labyrinth- & Level-Konfigurationen.
Definiert Geometrie, Startkoordinaten, Portale, Geisterhaus-Offsets und
Einbahnstraßen-Regeln für verschiedene Level-Maps.
"""
from game_config import UP, DOWN, LEFT, RIGHT

class BaseMapConfig(object):
    """
    Basis-Konfiguration für Labyrinth-Layouts und Spawn-Beschränkungen.
    """
    def __init__(self):
        self.name = "map1"
        self.portalPairs = {}
        self.homeoffset = (0.0, 0.0)
        self.homenodeconnectLeft = (0, 0)
        self.homenodeconnectRight = (0, 0)
        self.pacmanStart = (0, 0)
        self.fruitStart = (0, 0)
        self.ghostNodeDeny = {UP: (), DOWN: (), LEFT: (), RIGHT: ()}

    def setPortalPairs(self, nodes):
        """Verknüpft die Portal-Tunnelpaare im Navigationsgraphen."""
        for pair in self.portalPairs.values():
            nodes.setPortalPair(*pair)

    def connectHomeNodes(self, nodes):
        """Verbindet das Geisterhaus mit den Außenwegen des Labyrinths."""
        home_key = nodes.createHomeNodes(*self.homeoffset)
        nodes.connectHomeNodes(home_key, self.homenodeconnectLeft, LEFT)
        nodes.connectHomeNodes(home_key, self.homenodeconnectRight, RIGHT)

    def addOffset(self, x, y):
        """Addiert den Geisterhaus-Offset zu relativen Kachelkoordinaten."""
        return x + self.homeoffset[0], y + self.homeoffset[1]

    def denyGhostsAccess(self, ghosts, nodes):
        """Sperrt die Seitenausgänge des Geisterhauses und wendet einbahnige Verbote an."""
        ghost_home_exit = self.addOffset(2, 3)
        nodes.denyAccessList(*(ghost_home_exit + (LEFT, ghosts)))
        nodes.denyAccessList(*(ghost_home_exit + (RIGHT, ghosts)))

        # Layout-spezifische Richtungsbeschränkungen für Geister anwenden
        for direction, tile_tuples in self.ghostNodeDeny.items():
            for coords in tile_tuples:
                nodes.denyAccessList(*(coords + (direction, ghosts)))


class LevelMap1(BaseMapConfig):
    """
    Level 1: Klassisches Arcade-Labyrinth-Layout.
    """
    def __init__(self):
        super(LevelMap1, self).__init__()
        # Dateiname der Map (erwartet map1.txt und map1_rotation.txt)
        self.name = "map1"
        # Anpassbar: Koordinaten der Tunnel-Portale am linken und rechten Rand (Spalte, Zeile)
        self.portalPairs = {0: ((0, 17), (27, 17))}
        self.homeoffset = (11.5, 14)
        self.homenodeconnectLeft = (12, 14)
        self.homenodeconnectRight = (15, 14)
        # Anpassbar: Startposition von Pacman
        self.pacmanStart = (15, 26)
        # Anpassbar: Erscheinungsort für Bonusfrüchte
        self.fruitStart = (9, 20)
        # Spezifische Aufwärts-Sperren oberhalb des Geisterhauses für Geister
        self.ghostNodeDeny = {
            UP: ((12, 14), (15, 14), (12, 26), (15, 26)),
            LEFT: (self.addOffset(2, 3),),
            RIGHT: (self.addOffset(2, 3),)
        }


class LevelMap2(BaseMapConfig):
    """
    Level 2: Alternatives Labyrinth-Layout mit zwei separaten Portal-Tunneln.
    """
    def __init__(self):
        super(LevelMap2, self).__init__()
        # Dateiname der Map (erwartet map2.txt und map2_rotation.txt)
        self.name = "map2"
        # Zwei Tunnelpaare (oben und unten)
        self.portalPairs = {
            0: ((0, 4), (27, 4)),
            1: ((0, 26), (27, 26))
        }
        self.homeoffset = (11.5, 14)
        self.homenodeconnectLeft = (9, 14)
        self.homenodeconnectRight = (18, 14)
        self.pacmanStart = (16, 26)
        self.fruitStart = (11, 20)
        self.ghostNodeDeny = {
            UP: ((9, 14), (18, 14), (11, 23), (16, 23)),
            LEFT: (self.addOffset(2, 3),),
            RIGHT: (self.addOffset(2, 3),)
        }


class LevelMapRegistry(object):
    """
    Verwaltet und instanziiert die passende Map-Konfiguration für das aktuelle Level.
    """
    # Anpassbar: Hier können weitere Level-Maps registriert werden (z. B. 2: LevelMap3)
    MAP_SEQUENCE = {0: LevelMap1, 1: LevelMap2}

    def __init__(self):
        self.obj = None
        self.mazedict = self.MAP_SEQUENCE

    def loadMaze(self, level):
        map_index = level % len(self.mazedict)
        self.obj = self.mazedict[map_index]()


# Kompatibilitäts-Aliase
MazeBase = BaseMapConfig
Maze1 = LevelMap1
Maze2 = LevelMap2
MazeData = LevelMapRegistry
