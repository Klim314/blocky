import pytest

from blocky.manager import GameStateManager

# @pytest.fixture(scope="function")
# def setup_gamestate():


def test_load_stage():
    gsm = GameStateManager.from_path("data/stages/stage1.yaml")
    zm = gsm.zone_manager
    zone = zm.zone
    # Check that active units were loaded
    u1 = zone.get_unit(0, 0, 0)
    assert(u1.unit_class == "knight")
    assert(u1.name == "knight1")

    # Check that inactive units were loaded
    print(gsm.inactive_entities)
    assert("knight_3" in gsm.inactive_entities)

    # Check if events were loaded
    assert(len(gsm.event_manager.events["time_elapsed"]) == 1)
    # raise

def test_event():
    gsm = GameStateManager.from_path("data/stages/stage1.yaml")
    zm = gsm.zone_manager
    zone = zm.zone
    gsm.end_round()
    gsm.end_round()
    gsm.end_round()
    assert(zone.get_cell(2, 0, 0).has_unit())
