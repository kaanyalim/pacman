"""
Haupt-Einstiegspunkt & Game-Engine (PacmanGame).
Koordiniert die Hauptspielschleife (Main-Loop), Event-Verarbeitung,
Spielzustände, Kollisions-Events, Rendering und Levelübergänge.
"""
import sys
import pygame
from pygame.locals import QUIT, KEYDOWN, K_SPACE

from game_config import (
    SCREENSIZE, SCREENWIDTH, SCREENHEIGHT,
    BLACK, WHITE, RIGHT, LEFT,
    PAUSETXT, READYTXT, GAMEOVERTXT, POWERPELLET,
    FREIGHT, SPAWN, FPS
)
from player import PacmanPlayer
from nav_grid import NavigationGraph
from collectibles import CollectibleManager
from ghost_actors import GhostSquad
from bonus_fruit import BonusFruit
from pause_manager import PauseController
from ui_overlay import HudManager
from graphics_engine import LivesVisuals, MazeBackgroundRenderer
from level_maps import LevelMapRegistry

class PacmanGame(object):
    """
    Zentrale Game-Controller-Klasse.
    """
    def __init__(self):
        pygame.init()
        # Anpassbar: Fenstertitel
        pygame.display.set_caption("Pacman Arcade")
        self.screen = pygame.display.set_mode(SCREENSIZE, 0, 32)
        self.background = None
        self.background_norm = None
        self.background_flash = None
        self.clock = pygame.time.Clock()
        self.fruit = None
        self.pause = PauseController(True)
        self.level = 0
        # Anpassbar: Anzahl der Startleben (Standard: 5)
        self.lives = 5
        self.score = 0
        self.textgroup = HudManager()
        self.lifesprites = LivesVisuals(self.lives)
        # Anpassbar: Blink-Effekt bei Levelabschluss
        self.flashBG = False
        self.flashTime = 0.2
        self.flashTimer = 0.0
        self.fruitCaptured = []
        self.mazedata = LevelMapRegistry()
        self.mazesprites = None
        self.nodes = None
        self.pacman = None
        self.pellets = None
        self.ghosts = None

    def setBackground(self):
        """Erzeugt das normale Hintergrundbild und die blinkende Variante für den Levelwechsel."""
        self.background_norm = pygame.surface.Surface(SCREENSIZE).convert()
        self.background_norm.fill(BLACK)
        self.background_flash = pygame.surface.Surface(SCREENSIZE).convert()
        self.background_flash.fill(BLACK)

        theme_row = self.level % 5
        self.background_norm = self.mazesprites.constructBackground(self.background_norm, theme_row)
        self.background_flash = self.mazesprites.constructBackground(self.background_flash, 5)
        self.flashBG = False
        self.background = self.background_norm

    def startGame(self):
        """Initialisiert die Map, Entitäten, Graphenverbindungen und Sperren für das aktuelle Level."""
        self.mazedata.loadMaze(self.level)
        map_name = self.mazedata.obj.name
        self.mazesprites = MazeBackgroundRenderer(f"{map_name}.txt", f"{map_name}_rotation.txt")
        self.setBackground()

        self.nodes = NavigationGraph(f"{map_name}.txt")
        self.mazedata.obj.setPortalPairs(self.nodes)
        self.mazedata.obj.connectHomeNodes(self.nodes)

        pacman_start = self.nodes.getNodeFromTiles(*self.mazedata.obj.pacmanStart)
        self.pacman = PacmanPlayer(pacman_start)
        self.pellets = CollectibleManager(f"{map_name}.txt")
        self.ghosts = GhostSquad(self.nodes.getStartTempNode(), self.pacman)

        # Geister-Startpositionen im Geisterhaus setzen
        self.ghosts.pinky.setStartNode(self.nodes.getNodeFromTiles(*self.mazedata.obj.addOffset(2, 3)))
        self.ghosts.inky.setStartNode(self.nodes.getNodeFromTiles(*self.mazedata.obj.addOffset(0, 3)))
        self.ghosts.clyde.setStartNode(self.nodes.getNodeFromTiles(*self.mazedata.obj.addOffset(4, 3)))
        self.ghosts.setSpawnNode(self.nodes.getNodeFromTiles(*self.mazedata.obj.addOffset(2, 3)))
        self.ghosts.blinky.setStartNode(self.nodes.getNodeFromTiles(*self.mazedata.obj.addOffset(2, 0)))

        # Zugriffsrechte und Geisterhaus-Sperren einrichten
        self.nodes.denyHomeAccess(self.pacman)
        self.nodes.denyHomeAccessList(self.ghosts)
        self.ghosts.inky.startNode.denyAccess(RIGHT, self.ghosts.inky)
        self.ghosts.clyde.startNode.denyAccess(LEFT, self.ghosts.clyde)
        self.mazedata.obj.denyGhostsAccess(self.ghosts, self.nodes)

    def update(self):
        """Haupt-Update-Zyklus: Taktung, Eingabeverarbeitung, Spielzustände und Rendering."""
        dt = self.clock.tick(FPS) / 1000.0
        self.textgroup.update(dt)
        self.pellets.update(dt)

        if not self.pause.paused:
            self.ghosts.update(dt)
            if self.fruit is not None:
                self.fruit.update(dt)
            self.checkPelletEvents()
            self.checkGhostEvents()
            self.checkFruitEvents()

        if self.pacman.alive:
            if not self.pause.paused:
                self.pacman.update(dt)
        else:
            self.pacman.update(dt)

        # Blink-Effekt bei Levelabschluss aktualisieren
        if self.flashBG:
            self.flashTimer += dt
            if self.flashTimer >= self.flashTime:
                self.flashTimer = 0.0
                self.background = self.background_flash if self.background == self.background_norm else self.background_norm

        pause_callback = self.pause.update(dt)
        if pause_callback is not None:
            pause_callback()

        self.checkEvents()
        self.render()

    def checkEvents(self):
        """Verarbeitet Fenster- und Tastatur-Ereignisse."""
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                # Anpassbar: Pausentaste (Standard: Leertaste)
                if event.key == K_SPACE:
                    if self.pacman.alive:
                        self.pause.setPause(playerPaused=True)
                        if not self.pause.paused:
                            self.textgroup.hideText()
                            self.showEntities()
                        else:
                            self.textgroup.showText(PAUSETXT)

    def checkPelletEvents(self):
        """Prüft Pellet-Kollisionen, Punktevergabe und die Freilassung von Inky und Clyde."""
        pellet = self.pacman.eatPellets(self.pellets.pelletList)
        if pellet is not None:
            self.pellets.numEaten += 1
            self.updateScore(pellet.points)

            # Anpassbar: Schwellenwerte für die Geisterfreilassung (Inky bei 30, Clyde bei 70 Pellets)
            if self.pellets.numEaten == 30:
                self.ghosts.inky.startNode.allowAccess(RIGHT, self.ghosts.inky)
            if self.pellets.numEaten == 70:
                self.ghosts.clyde.startNode.allowAccess(LEFT, self.ghosts.clyde)

            self.pellets.pelletList.remove(pellet)

            # Power-Pellet aktiviert den Angstmodus für alle Geister
            if pellet.name == POWERPELLET:
                self.ghosts.startFreight()

            # Alle Pellets gefressen -> Level gewonnen
            if self.pellets.isEmpty():
                self.flashBG = True
                self.hideEntities()
                self.pause.setPause(pauseTime=3.0, func=self.nextLevel)

    def checkGhostEvents(self):
        """Prüft Kollisionen mit Geistern: Entweder wird der Geist gefressen oder Pacman verliert ein Leben."""
        for ghost in self.ghosts:
            if self.pacman.collideGhost(ghost):
                if ghost.mode.current == FREIGHT:
                    # Geist gefressen
                    self.pacman.visible = False
                    ghost.visible = False
                    self.updateScore(ghost.points)
                    self.textgroup.addText(str(ghost.points), WHITE, ghost.position.x, ghost.position.y, 8, time=1.0)
                    self.ghosts.updatePoints()
                    self.pause.setPause(pauseTime=1.0, func=self.showEntities)
                    ghost.startSpawn()
                    self.nodes.allowHomeAccess(ghost)
                elif ghost.mode.current != SPAWN:
                    # Pacman verliert ein Leben
                    if self.pacman.alive:
                        self.lives -= 1
                        self.lifesprites.removeImage()
                        self.pacman.die()
                        self.ghosts.hide()
                        if self.lives <= 0:
                            self.textgroup.showText(GAMEOVERTXT)
                            self.pause.setPause(pauseTime=3.0, func=self.restartGame)
                        else:
                            self.pause.setPause(pauseTime=3.0, func=self.resetLevel)

    def checkFruitEvents(self):
        """Spawnt Bonusfrüchte bei 50 und 140 gefressenen Pellets und prüft deren Einsammeln."""
        # Anpassbar: Schwellenwerte für das Erscheinen von Bonusfrüchten
        if self.pellets.numEaten in (50, 140):
            if self.fruit is None:
                fruit_pos = self.mazedata.obj.fruitStart
                self.fruit = BonusFruit(self.nodes.getNodeFromTiles(*fruit_pos), self.level)

        if self.fruit is not None:
            if self.pacman.collideCheck(self.fruit):
                self.updateScore(self.fruit.points)
                self.textgroup.addText(str(self.fruit.points), WHITE, self.fruit.position.x, self.fruit.position.y, 8, time=1.0)
                
                # Gesammelte Früchte in die Inventarleiste aufnehmen
                if not any(f.get_offset() == self.fruit.image.get_offset() for f in self.fruitCaptured):
                    self.fruitCaptured.append(self.fruit.image)
                self.fruit = None
            elif self.fruit.destroy:
                self.fruit = None

    def showEntities(self):
        self.pacman.visible = True
        self.ghosts.show()

    def hideEntities(self):
        self.pacman.visible = False
        self.ghosts.hide()

    def nextLevel(self):
        """Lädt das nächste Level und erhöht den Level-Zähler."""
        self.showEntities()
        self.level += 1
        self.pause.paused = True
        self.startGame()
        self.textgroup.updateLevel(self.level)

    def restartGame(self):
        """Startet das gesamte Spiel nach einem Game Over neu."""
        self.lives = 5
        self.level = 0
        self.pause.paused = True
        self.fruit = None
        self.startGame()
        self.score = 0
        self.textgroup.updateScore(self.score)
        self.textgroup.updateLevel(self.level)
        self.textgroup.showText(READYTXT)
        self.lifesprites.resetLives(self.lives)
        self.fruitCaptured = []

    def resetLevel(self):
        """Setzt die Figuren nach einem Lebensverlust auf ihre Startpositionen zurück."""
        self.pause.paused = True
        self.pacman.reset()
        self.ghosts.reset()
        self.fruit = None
        self.textgroup.showText(READYTXT)

    def updateScore(self, points):
        self.score += points
        self.textgroup.updateScore(self.score)

    def render(self):
        """Rendert alle Spielkomponenten auf den Bildschirm."""
        self.screen.blit(self.background, (0, 0))
        self.pellets.render(self.screen)
        if self.fruit is not None:
            self.fruit.render(self.screen)
        self.pacman.render(self.screen)
        self.ghosts.render(self.screen)
        self.textgroup.render(self.screen)

        # Anzeige der verbleibenden Leben (unten links)
        for i, life_img in enumerate(self.lifesprites.images):
            x = life_img.get_width() * i
            y = SCREENHEIGHT - life_img.get_height()
            self.screen.blit(life_img, (x, y))

        # Anzeige der gesammelten Bonusfrüchte (unten rechts)
        for i, fruit_img in enumerate(self.fruitCaptured):
            x = SCREENWIDTH - fruit_img.get_width() * (i + 1)
            y = SCREENHEIGHT - fruit_img.get_height()
            self.screen.blit(fruit_img, (x, y))

        pygame.display.update()


# Kompatibilitäts-Alias
GameController = PacmanGame

def run():
    game = PacmanGame()
    game.startGame()
    while True:
        game.update()

if __name__ == "__main__":
    run()
