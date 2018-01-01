import yaml
import logging

from itertools import chain
from blocky.custom_exceptions import MissingResourceException, InvalidDataException


"""
Entities.py
Handles entities that reside within the zones
"""


class UnitData:
    pass


"""
Active skills. These
"""

class Active:
    def __init__(self, active_id, **kwargs):
        self.id = active_id
        for key, item in kwargs.items():
            setattr(self, key, item)
        self.properties = set(self.properties)
        # Add supplementary effects here in the future

    def __repr__(self):
        return "<Active: id={}, name={}>".format(self.id, self.name)
    # @classmethod
    # def from_dict(cls, dictionary):
    #     return cls(**dictionary)


class ActiveLoader:
    def __init__(self, raw_path):
        with open(raw_path) as f:
            raw = yaml.load(f)
        self.check_integrity(raw)
        self.actives = dict()
        self.actives_by_name = dict()
        for active_id, active_dict in raw.items():
            active = Active(active_id, **active_dict)
            self.actives[active_id] = active
            self.actives_by_name[active_dict["name"]] = active

    def check_integrity(self, raw_data):
        # Check that Active names AND ids have no duplicates
        if not len(raw_data) == len({i for i in raw_data}):
            logging.debug(raw_data)
            raise InvalidDataException("Duplicate names found in ability skills")

    def __getitem__(self, active_id):
        if active_id not in self.actives:
            raise MissingResourceException("Active {} not found in active data".format(active_id))
        return self.actives[active_id]

    def by_name(self, active_name):
        if active_name not in self.actives_by_name:
            raise MissingResourceException("Active {} not found in active data".format(active_name))
        return self.actives_by_name[active_name]

"""
Entities
"""


class Entity:
    def __init__(self, manager=None):
        self.pos = (None, None, None)
        self.manager = manager

    @property
    def x(self):
        return self.pos[0]

    @property
    def y(self):
        return self.pos[1]

    @property
    def z(self):
        return self.pos[2]

    def refresh(self):
        pass

    def emit(self, signal, params):
        # Emits a signal to the manager
        if not self.manager:
            raise
        self.manager.recieve(signal, params)


class Unit(Entity):
    """Class for a general use field-unit

    Attributes:

    """
    def __init__(self, level, hp, mp, move, atk, pdef, mdef,
                 name, actives, passives, properties,
                 unit_class,
                 sprite, portrait,
                 manager,
                 id=None):
        super().__init__(manager)
        # System stats
        self.unit_class = unit_class # Class of the 
        self.id = id

        # Core stats
        self.level = level
        self.hp = hp
        self.mp = mp

        self.move = move
        self.atk = atk
        self.pdef = pdef
        self.mdef = mdef



        # Supplementary stats
        self.name = name
        self.actives = actives
        self.passives = passives

        # Variable stats
        self.owner = None

        # Graphics
        self.sprite = sprite
        self.portrait = portrait

    def __repr__(self):
        return "<Unit: {}>".format(self.name)

    def is_dead(self):
        if self.hp <= 0:
            return True
        return False

    def take_dmg(self, dmg):
        self.hp = max(0, self.hp - dmg)
        # Add some checking and callbacks

    @classmethod
    def from_thing(cls):
        pass


class TemplateUnitFactory:
    def __init__(self, unit_template_path, loaded_actives):
        """
        arguments:
            unit_template_path: string. Path to YAML file containing unit stats
            loaded_actives: ActiveLoader object.
        """
        with open(unit_template_path) as f:
            self.unit_data = yaml.load(f)
        self.loaded_actives = loaded_actives
        # Do some preimage loading and stuff for used templates

    # TODO. Allow creation of SPESHUL UNITS
    def create_unit(self, unit_class, unit_name, level, modifiers={}, owner=None, id=None):
        """Unit creation from class template
        args:
            unit_class: str
            unit_name: str
            level: int
            modifiers: 
        """
        if unit_class not in self.unit_data:
            raise MissingResourceException("{} not found in unit_data".format(unit_class))
        datum = self.unit_data[unit_class]
        base, growths = datum["base"], datum["growths"]
        properties = datum["properties"]

        # Create the unit actives
        actives = [self.loaded_actives[active_id] for active_id in base["actives"]]
        print(growths["actives"])
        for skill_level, active_id in growths["actives"]:
            if skill_level > level:
                break
            actives.append(self.loaded_actives[active_id])

        unit = Unit(level,
                    int(base["hp"] + level * growths["hp"]),  # Hp
                    int(base["mp"] + level * growths["mp"]),  # Mp
                    int(base["move"] + level * growths["move"]),  # Move
                    int(base["atk"] + level * growths["atk"]),  # Atk
                    int(base["pdef"] + level * growths["pdef"]),  # Pdef
                    int(base["mdef"] + level * growths["mdef"]),  # Mdef
                    unit_name,  # Name
                    actives,  # Actives
                    [],  # Passives
                    properties,  # Properties
                    unit_class,  # Unit class
                    None,  # Sprite
                    None,  # Portrait
                    None,  # Manager
                    id=id)
        unit.owner = owner
        return unit
