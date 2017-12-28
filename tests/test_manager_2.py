"""
TODO: REFACTOR TO PYTEST
"""

import sys
import os
import yaml
import logging
import pytest

print(sys.path)
print(os.getcwd())


from blocky.fieldmap import Zone
from blocky.entities import Unit
from blocky.manager import Manager
from blocky.custom_exceptions import IllegalActionException
from blocky.entities import TemplateUnitFactory, ActiveLoader

logging.basicConfig(level=logging.DEBUG)

# Map annotations
with open("data/map_ann.yaml") as f:
    map_ann = yaml.load(f)


@pytest.fixture(scope="function")
def setup_map():
    """
    Sets up the map fixture for other tests
    """
    target = "data/maps/map1.map"
    zone = Zone()
    zone.load_map(map_ann, target)
    manager = Manager(zone)

    actives = ActiveLoader("data/actives.yaml")
    # Create Unitfactory
    uf = TemplateUnitFactory("data/units.yaml", actives)
    knight1 = uf.create_unit("knight", "knight1", 1, owner="p1")
    knight2 = uf.create_unit("knight", "knight2", 1, owner="p2")
    knight3 = uf.create_unit("knight", "knight3", 1, owner="p1")
    manager.add_entity(knight1, 0, 0, 0)
    manager.add_entity(knight2, 1, 0, 0)
    manager.add_entity(knight3, 2, 0, 0)
    return (manager, (knight1, knight2, knight3))

@pytest.fixture(scope="function")
def setup_map_walled():
    target = "data/maps/map3_wall.map"
    zone = Zone()
    zone.load_map(map_ann, target)
    manager = Manager(zone)

    actives = ActiveLoader("data/actives.yaml")
    # Create Unitfactory
    uf = TemplateUnitFactory("data/units.yaml", actives)
    knight1 = uf.create_unit("knight", "knight1", 1, owner="p1")
    knight2 = uf.create_unit("knight", "knight2", 1, owner="p2")
    knight3 = uf.create_unit("knight", "knight3", 1, owner="p1")
    manager.add_entity(knight1, 0, 0, 0)
    manager.add_entity(knight2, 1, 0, 0)
    manager.add_entity(knight3, 3, 0, 0)
    return (manager, (knight1, knight2, knight3))

# Test of basic Attack functionality
def test_attack_basic(setup_map):
    manager, knights = setup_map
    knight1, knight2 = knights[:2]
    prev_hp = knight2.hp
    # Test normal attack and hp loss
    manager.interact_attack(knight1, (1, 0, 0), 1)
    # Check that damage was done
    assert knight2.hp < prev_hp


def test_attack_range(setup_map):
    manager, knights = setup_map
    knight1, knight2, knight3 = knights
    manager.interact_attack(knight1, (2, 0, 0), 2)


@pytest.mark.xfail
def test_attack_lowrange(setup_map):
    manager, knights = setup_map
    knight1, knight2, knight3 = knights
    manager.interact_attack(knight1, (2, 0, 0), 1)


def test_active_attack_single(setup_map):
    manager, knights = setup_map
    knight1, knight2, knight3 = knights
    prev_hp = knight2.hp
    manager.interact_active(knight1, knight1.actives[0], (1, 0, 0))
    assert(knight2.hp < prev_hp)
    # raise


def test_active_attack_aoe(setup_map):
    manager, knights = setup_map
    knight1, knight2, knight3 = knights
    k2_prev_hp = knight2.hp
    k1_prev_hp = knight1.hp
    actives = ActiveLoader("data/actives.yaml")
    aoe_attack = actives["attack_1"]
    assert(aoe_attack.name == "basic_aoe")
    manager.interact_active(knight2, aoe_attack, (1, 0, 0))
    assert(knight2.hp == k2_prev_hp)
    assert(knight1.hp < k1_prev_hp)

def test_active_attack_aoe_ff(setup_map):
    manager, knights = setup_map
    knight1, knight2, knight3 = knights
    k2_prev_hp = knight2.hp
    k1_prev_hp = knight1.hp
    actives = ActiveLoader("data/actives.yaml")
    aoe_attack = actives["attack_1"]
    assert(aoe_attack.name == "basic_aoe")
    # Now lets test friendly fire
    aoe_attack.properties.add("friendly_fire")
    print(aoe_attack.properties)
    manager.interact_active(knight2, aoe_attack, (1, 0, 0))
    assert(knight2.hp < k2_prev_hp)
    assert(knight1.hp < k1_prev_hp)


def test_active_attack_aoe_spread(setup_map_walled):
    manager, knights = setup_map_walled
    knight1, knight2, knight3 = knights
    k3_prev_hp = knight3.hp
    k1_prev_hp = knight1.hp
    actives = ActiveLoader("data/actives.yaml")
    aoe_attack = actives["attack_1"]
    assert(aoe_attack.name == "basic_aoe")
    # The Normal attack is blocked
    manager.interact_active(knight2, aoe_attack, (1, 0, 0))
    assert(knight1.hp < k1_prev_hp)
    assert(knight3.hp == k3_prev_hp)

    # spread should not be blocked
    aoe_attack.properties.add("spread")
    print(aoe_attack.properties)
    k1_prev_hp = knight1.hp
    manager.interact_active(knight2, aoe_attack, (1, 0, 0))
    assert(knight3.hp < k3_prev_hp)
    assert(knight1.hp < k1_prev_hp)


def test_move(setup_map):
    manager, knights = setup_map
    knight1, knight2, knight3 = knights
    manager.interact_move(knight3, (4, 0, 0))
    assert(knight3.pos == (4, 0, 0))
    assert(manager.zone.get_cell(2, 0, 0).contents is None)


@pytest.mark.skip
def test_move_unpassable(setup_map):
    pass


@pytest.mark.xfail
def test_move_insufficient(setup_map):
    manager, knights = setup_map
    knight1, knight2, knight3 = knights
    manager.interact_move(knight3, (0, 2, 0))


def test_move_forced(setup_map):
    manager, knights = setup_map
    knight1, knight2, knight3 = knights
    manager.manip_force_move(knight3, (0, 2, 0))
    assert(knight3.pos == (0, 2, 0))
    assert(manager.zone.get_cell(2, 0, 0).contents is None)


# # Test interact-move illegal target (Occupied space)
# try:
#     manager.interact_move(manager.zone.get_cell(1, 0, 0), manager.zone.get_cell(0, 0, 0))
# except IllegalActionException as e:
#     print(e)
#     print("  Expected EXCEPTION CAUGHT")

# # Test illegal movement (Move through enemy target)
# try:
#     manager.interact_move(manager.zone.get_cell(0, 0, 0), manager.zone.get_cell(2, 0, 0))
# except IllegalActionException as e:
#     print(e)
#     print("  Expected EXCEPTION CAUGHT")
# else:
#     raise Exception("Unexpected success")