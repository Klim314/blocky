"""
TODO: REFACTOR TO PYTEST
"""

import yaml
import logging

from fieldmap import Zone
from entities import Unit
from manager import Manager
from custom_exceptions import IllegalActionException
from entities import TemplateUnitFactory

logging.basicConfig(level=logging.DEBUG)

# Map annotations
with open("data/map_ann.yaml") as f:
    map_ann = yaml.load(f)

print(map_ann)
# Test of basic Attack functionality

# Check basic loading of 2d map (1 layer)
target = "data/maps/map1.map"
zone = Zone()
zone.load_map(map_ann, target)

# zone.print_all_planes()
manager = Manager(zone)

# Create Unitfactory
uf = TemplateUnitFactory("data/units.yaml")

knight1 = uf.create_unit("knight", "knight1", 1)
knight2 = uf.create_unit("knight", "knight2", 1)

c1, c2 = zone.get_cell(0, 0, 0), zone.get_cell(1, 0, 0)
c1.contents, c2.contents = knight1, knight2
manager.interact_attack(c1, c2, 1)
manager.interact_attack(c1, c2, 1)
manager.interact_attack(c1, c2, 1)

# Test ranged attacks
logging.debug("---ATTACK TEST 2---")
target = "data/maps/map1.map"
zone = Zone()
zone.load_map(map_ann, target)

manager = Manager(zone)

knight1 = uf.create_unit("knight", "knight1", 1)
knight2 = uf.create_unit("knight", "knight2", 1)

c1, c2 = zone.get_cell(0, 0, 0), zone.get_cell(2, 0, 0)
c1.contents, c2.contents = knight1, knight2
print("POSITIONS:", c1.pos, c2.pos)

# Attacking from out of range should fail
try:
    manager.interact_attack(c1, c2, 1)
except IllegalActionException as e:
    print("Expected EXCEPTION CAUGHT")

# Attacking from out of range should fail
manager.interact_attack(c1, c2, 2)


"""
Movement tests
"""
logging.debug("---MOVEMENT TEST 1---")
target = "data/maps/map1.map"
zone = Zone()
zone.load_map(map_ann, target)

manager = Manager(zone)

knight1 = uf.create_unit("knight", "knight1", 1)

manager.add_entity(knight1, 0, 0, 0)

c1, c2 = zone.get_cell(0, 0, 0), zone.get_cell(2, 0, 0)
print("POSITIONS:", c1.pos, c2.pos)

# Test interact-move legal target
# Knight has move 3
c = zone.get_cell(1, 0, 0)
print(c, c.has_unit())
manager.interact_move(c1, zone.get_cell(1, 0, 0))
assert(c.contents == knight1)
assert(knight1.pos == (1, 0, 0))



#Test illegal moves

logging.debug("---MOVEMENT TEST 2---")
target = "data/maps/map1.map"
zone = Zone()
zone.load_map(map_ann, target)

manager = Manager(zone)

knight1 = uf.create_unit("knight", "knight1", 1, owner="player1")
knight2 = uf.create_unit("knight", "knight2", 2, owner="player2")

manager.add_entity(knight1, 0, 0, 0)
manager.add_entity(knight2, 1, 0, 0)

# Test interact-move illegal target (not enough move)
try:
    manager.interact_move(manager.zone.get_cell(1, 0, 0), manager.zone.get_cell(4, 2, 0))
except IllegalActionException as e:
    print(e)
    print("  Expected EXCEPTION CAUGHT")

# Test interact-move illegal target (Occupied space)
try:
    manager.interact_move(manager.zone.get_cell(1, 0, 0), manager.zone.get_cell(0, 0, 0))
except IllegalActionException as e:
    print(e)
    print("  Expected EXCEPTION CAUGHT")

# Test illegal movement (Move through enemy target)
try:
    manager.interact_move(manager.zone.get_cell(0, 0, 0), manager.zone.get_cell(2, 0, 0))
except IllegalActionException as e:
    print(e)
    print("  Expected EXCEPTION CAUGHT")
else:
    raise Exception("Unexpected success")