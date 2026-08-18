"""
Zustandsautomat & Modus-Steuerung für Geister.
Verwaltet die zeitgesteuerten Zyklen zwischen Scatter- und Chase-Phasen
sowie die Übergänge in den Freight-Modus (Power-Pellet) und Spawn-Modus (Augen).
"""
from game_config import SCATTER, CHASE, FREIGHT, SPAWN

class PhaseCycleTimer(object):
    """
    Steuert die periodischen Wechsel zwischen Scatter (Rückzug) und Chase (Jagd).
    """
    def __init__(self):
        self.timer = 0.0
        # Anpassbar: Standarddauer der ersten Scatter-Phase
        self.time = 7.0
        self.mode = SCATTER
        self.scatter()

    def update(self, dt):
        self.timer += dt
        if self.timer >= self.time:
            if self.mode == SCATTER:
                self.chase()
            elif self.mode == CHASE:
                self.scatter()

    # Anpassbar: Dauer der Streu-/Rückzugsphase in Sekunden (Standard: 7s)
    def scatter(self):
        self.mode = SCATTER
        self.time = 7.0
        self.timer = 0.0

    # Anpassbar: Dauer der Verfolgungsphase in Sekunden (Standard: 20s)
    def chase(self):
        self.mode = CHASE
        self.time = 20.0
        self.timer = 0.0


class GhostStateManager(object):
    """
    Verwaltet die Zustandsübergänge für einen einzelnen Geist.
    """
    def __init__(self, ghost_entity):
        self.timer = 0.0
        self.time = None
        self.cycle_timer = PhaseCycleTimer()
        self.mainmode = self.cycle_timer
        self.current = self.cycle_timer.mode
        self.entity = ghost_entity

    def update(self, dt):
        self.cycle_timer.update(dt)

        # Wenn der Angstmodus abläuft, Rückkehr in den regulären Scatter/Chase-Zyklus
        if self.current == FREIGHT:
            self.timer += dt
            if self.timer >= self.time:
                self.time = None
                self.entity.normalMode()
                self.current = self.cycle_timer.mode
        elif self.current in (SCATTER, CHASE):
            self.current = self.cycle_timer.mode

        # Sobald die Augen das Geisterhaus erreichen, wird der Geist wiederbelebt
        if self.current == SPAWN:
            if self.entity.node == self.entity.spawnNode:
                self.entity.normalMode()
                self.current = self.cycle_timer.mode

    # Anpassbar: Dauer des Angstmodus nach Fressen eines Power-Pellets (Standard: 7s)
    def setFreightMode(self):
        if self.current in (SCATTER, CHASE):
            self.timer = 0.0
            self.time = 7.0
            self.current = FREIGHT
        elif self.current == FREIGHT:
            self.timer = 0.0

    def setSpawnMode(self):
        """Wechselt in den Spawn-Modus (Geist wurde gefressen)."""
        if self.current == FREIGHT:
            self.current = SPAWN


# Kompatibilitäts-Aliase
MainMode = PhaseCycleTimer
ModeController = GhostStateManager
