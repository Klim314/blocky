import os
import logging
import yaml

from random import randint
from heapdict import heapdict
from blocky.custom_exceptions import IllegalActionException, MissingResourceException
from blocky.fieldmap import pathfind, Zone
from blocky.entities import TemplateUnitFactory, ActiveLoader


def calc_damage(unit, attack, target):
    return eval(attack.formula.format(uatk=unit.atk,
                                      updef=unit.pdef,
                                      tpdef=target.pdef,
                                      tmdef=target.mdef))


# Might want to break this down into the gamemanager, gamestatemanager and zonemanager

class GameStateManager:
    """Manages a stage instance including objectives, etc
    """
    def __init__(self, stage_data):
        self.actives = ActiveLoader(os.path.join("data", stage_data["active_ann"]))
        self.uf = TemplateUnitFactory(os.path.join("data", stage_data["unit_ann"]),
                                      self.actives)
        self.buffs = None
        self.zone_manager = self._init_zone(stage_data)

    def _init_zone(self, stage_data):
        zone = Zone.from_paths(os.path.join("data", stage_data["map_ann"]),
                               os.path.join("data/maps", stage_data["map"]))
        zone_manager = Manager(zone)

        # Create the units and place them in the zone
        for unit_dict in stage_data["entities"]["units"]:
            unit = self.uf.create_unit(unit_dict["unit_class"],
                                       unit_dict["name"],
                                       unit_dict["level"],
                                       owner=unit_dict["owner"])
            zone_manager.add_entity(unit, *unit_dict["pos"])

        return zone_manager

    @classmethod
    def from_path(cls, stage_data_path):
        with open(stage_data_path) as f:
            temp = yaml.load(f)
        return cls(temp)




class Manager:
    """Manages a zone
    """
    def __init__(self, zone):
        """Initializes the gamestate
        arguments
            zone: Zone object
            package: mission package
        """
        self.zone = zone
        self.entities = []

        # All the various triggers that must be cleaned up
        self.triggers = []

    def _in_range(self, p1, p2, atk_range, filters={}):
        """Checks if p2 is in range of p1
        args:
            p1: tup (x, y z) indication source position
            p2: tup (x, y z) indication target position
            atk_range: int. Range of attack

        """
        path = pathfind(self.zone, p1, p2)
        logging.debug("Test attack. target_dist: {}, atk_range: {}, passed: {}".format(len(path), atk_range, len(path) - 1 <= atk_range))
        if len(path) - 1 > atk_range:  # Do we need a check if it reached?
            return False

        return True

    def _get_aoe_units(self, pos, aoe, filters):
        """Gets all units within an AoE centered on pos. Currently 2d only
        TODO: Modify using a proper pathfinding algorithim so it doesn't go through walls.
        This is just for ease of use
        """
        # Leave the hacky filter here for now, figure out what's the best way to do this later
        def check_filter(cell, filters):
            logging.debug((cell, cell.properties, filters))
            for filt, cond in filters.items():
                logging.debug(("Filter loop", filt, cond))
                # Check if it's filtering for PRESENCE
                if cond:
                    if filt not in cell.properties:
                        return False
                elif filt in cell.properties:
                    return False
            return True

        if not self.zone.check_coords(*pos):
            raise IllegalActionException("Pos is out of bounds.")

        units = []
        pq = heapdict()
        visited = set()
        pq[self.zone.get_cell(*pos)] = 0
        while pq:
            cell, dist = pq.popitem()
            if cell.contents:
                units.append(cell.contents)
            visited.add(cell.pos)
            if dist >= aoe:
                continue
            for neighbour in cell.get_neighbours():
                if neighbour.pos in visited:
                    continue
                # Check if the tile is a legal tile
                if not check_filter(neighbour, filters):
                    logging.debug("--SKIPPING--")
                    continue

                pq[neighbour] = dist + 1
        logging.debug("Units: {}".format(units))
        return units

    def add_entity(self, entity, x, y, z):
        entity.manager = self
        self.zone.add_entity(entity, x, y, z)
        self.entities.append(entity)  # Probably need a unique identifier for entities in the future
        entity.pos = (x, y, z)
        return 0

    # def get_cell(self, x, y, z):
    #     if not self.zone:
    #         raise MissingResourceException("No zone loaded to find cell in")
    #     return self.zone.get_cell(x, y, z)

    def interact_attack(self, unit, target_pos, atk_range):
        """Performs an interact action of type attack between two units
        Attack is from u1 -> u2

        """
        logging.debug("Beginning attack from {} to {}".format(unit.pos, target_pos))
        # Pathfind from start to end, check if within range
        if not self._in_range(unit.pos, target_pos, atk_range):
            raise IllegalActionException("Insufficient attack range")
        target = self.zone.get_unit(*target_pos)
        if not target:
            raise IllegalActionException("Attempted to attack cell {} with no target".format(target_pos))
        damage = max(0, randint(1, 6) + unit.atk - target.pdef)
        target_prev_hp = target.hp
        target.take_dmg(damage)
        print("Unit {} attacked Unit {} for {} damage.".format(unit.name, target.name, damage))
        print("  {} HP: {} -> {}".format(target.name, target_prev_hp, target.hp))
        if target.is_dead():
            print("  Unit {} was killed".format(target.name))

    def interact_active(self, unit, active, target_pos):
        """Performs an interact action using active a1 of u1 on u2
        Dispatches as following
            "attack_single: target is unit"
        """
        if not self.zone.check_coords(*target_pos):
            raise IllegalActionException("Target is out of bounds.")
        dispatch = {"attack_single": self._attack_single,
                    "attack_aoe": self._attack_aoe,
                    }
        logging.debug(active.active_type)
        return dispatch[active.active_type](unit, active, target_pos)

    # Dispatch commadns for interact_active
    def _attack_single(self, unit, active, target_pos):
        """Performs a single attack ability using single target active attack a1 on u2
        args:
            unit: Unit. Source unit using active
            active: Active. Active to be used
            target_unit Unit. Target Unit to be attacked
        """
        logging.debug("Beginning attack_single from {} to {}".format(unit.pos, target_pos))
        if not self._in_range(unit.pos, target_pos, active.range):
            raise IllegalActionException("Insufficient attack range")
        target = self.zone.get_unit(*target_pos)
        if not target:
            raise IllegalActionException("Attempted to attack cell {} with no target".format(target_pos))

        damage_dealt = calc_damage(unit, active, target)

        outstr = "{unit_class} {unit_name} attacked {target_name} with {ability_name} for {dmg} damage."
        logging.info(outstr.format(unit_class=unit.unit_class,
                                   unit_name=unit.name,
                                   target_name=target.name,
                                   ability_name=active.name,
                                   dmg=damage_dealt))
        target.take_dmg(damage_dealt)

        return 0

    def _attack_aoe(self, unit, active, target_pos):
        """Performs an AoE  attack from unit at target
        args:
            unit: Unit. Source unit using active
            active: Active. Active to be used
            target_unit tuple (x, y, z): Position to be used
        """
        logging.debug("Beginning attack_aoe from {} to {}".format(unit.pos, target_pos))
        if not self._in_range(unit.pos, target_pos, active.range):
            raise IllegalActionException("Insufficient attack range")

        # Does this go through walls
        spread = "spread" in active.properties
        logging.debug("Spread: {}".format(spread))
        if spread:
            filters = {}
        else:
            filters = {"atk_blocked": False}

        aoe_targets = [i for i in self._get_aoe_units(target_pos, active.aoe, filters=filters)]

        # Does this hit allied units
        friendly_fire = "friendly_fire" in active.properties
        logging.debug("Friendly fire: {}".format(friendly_fire))

        for target in aoe_targets:
            logging.debug((target, target.owner, unit.owner))
            damage_dealt = calc_damage(unit, active, target)
            # Change to proper alliances in the future
            if not friendly_fire and target.owner == unit.owner:
                logging.debug("Skipping {}".format(target))
                continue
            target.take_dmg(damage_dealt)



    def interact_move(self, unit, dest):
        # Check if the source and destination meet parameters
        # if not c1.has_unit():
        #     raise IllegalActionException("Move ordered from cell without unit")

        dest_cell = self.zone.get_cell(*dest)
        # Check if the unit is in the zone
        if not unit.pos:
            raise IllegalActionException("Move issued to unit outside zone")
        if dest_cell.has_unit():
            raise IllegalActionException("Move ordered into cell containing unit")

        unit_cell = self.zone.get_cell(*unit.pos)
        # Check if unit has sufficient movement
        distance = len(pathfind(self.zone, unit_cell.pos, dest_cell.pos)) - 1
        if distance > unit.move:
            raise IllegalActionException("Move requires {} move, unit possesses {}".format(distance,
                                                                                           unit.move))
        unit_cell.contents, dest_cell.contents = None, unit
        unit.pos = dest_cell.pos

        return 0

    """
    Manip type commands represent commands that players should not be using, but
    are accessible to the debug console et. al."""

    def manip_force_move(self, unit, dest):
        dest_cell = self.zone.get_cell(*dest)
        # if not c1.has_unit():
        #     raise IllegalActionException("Move ordered from dest_cell without unit")
        if dest_cell.has_unit():
            raise IllegalActionException("Move ordered into dest_cell containing unit")
        unit_cell = self.zone.get_cell(*unit.pos)
        logging.debug("Moved entity {} from {} to {}".format(unit, unit.pos, dest_cell.pos))
        unit_cell.contents, dest_cell.contents = None, unit
        unit.pos = dest_cell.pos
        return 0
