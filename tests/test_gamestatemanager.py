import pytest

from blocky.manager import GameStateManager

# @pytest.fixture(scope="function")
# def setup_gamestate():


def test_load_stage():
    gsm = GameStateManager.from_path("data/stages/stage1.yaml")
    zm = gsm.zone_manager
    zone = zm.zone
    u1 = zone.get_unit(0, 0, 0)
    assert(u1.unit_class == "knight")
    assert(u1.name == "knight1")

def test_event():
    pass