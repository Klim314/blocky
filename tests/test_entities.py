import pytest

from blocky.entities import ActiveLoader, TemplateUnitFactory

def test_ActiveLoader():
    data_raw = "data/actives.yaml"
    loaded = ActiveLoader(data_raw)
    actives = loaded.actives
    # assert(len(actives) == 4)
    assert("attack_0" in actives)
    a = actives["attack_0"] 
    assert(a.name == "basic_single")
    assert(a.formula == "({uatk} + randint(1, 6)) - {tpdef}")

def test_TemplateUnitFactory():
    actives = ActiveLoader("data/actives.yaml")
    # Create Unitfactory
    uf = TemplateUnitFactory("data/units.yaml", actives)
    l1_knight = uf.create_unit("knight", "l1_knight", 1)
    l10_knight = uf.create_unit("knight", "l10_knight", 10)
    assert(l1_knight.level == 1)
    assert(l1_knight.unit_class == "knight")
    assert(len(l1_knight.actives) == 1)
    assert(len(l10_knight.actives) == 2)
    assert(l1_knight.actives[0].id == "attack_0")
    assert(l10_knight.actives[0].id == "attack_0")
    assert(l10_knight.actives[1].id == "attack_2")
