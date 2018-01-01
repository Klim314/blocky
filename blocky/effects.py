# Effects that result from events
import logging

from blocky.custom_exceptions import TempException

class EffectManager:
    """Handles the creation (and execution?) of effects. Maybe change to loader
    """
    def __init__(self, gamestate_manager):
        self.gamestate_manager = gamestate_manager
        self.dispatch = {"spawn_unit": SpawnUnit}

    def create_effect(self, params):
        code, kwargs = params
        return self.dispatch[code](self.gamestate_manager, **kwargs)


class Effect:
    pass


class SpawnUnit(Effect):
    """Activates an inactive unit from the inactive pool, placing it in the zone
    """
    def __init__(self, gamestate_manager, unit_id, pos):
        self.gamestate_manager = gamestate_manager
        self.unit_id = unit_id
        self.pos = pos

    def execute(self):
        # Come up with a find nearest space alternative. For now, raise
        zone_manager = self.gamestate_manager.zone_manager
        cell = zone_manager.get_cell(*self.pos)
        if cell.has_unit():
            raise TempException("Attempted to spawn unit in cell containing units")
        logging.info("Spawning unit {} in pos {}".format(self.unit_id, self.pos))
        self.gamestate_manager.activate_entity(self.unit_id, self.pos)
        return 0


class SpawnUnitGeneric(Effect):
    def __init__(self, gamestate_manager, unit_class, level, modifiers={}):
        pass
