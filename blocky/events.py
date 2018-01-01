"""Do I want to take this the emit recieve paraidigm or the end of turn check
I think emit is more sane performance wise, but end of turn block
allows for easier modularization. Lets work with the emit-recieve for now"""
from collections import defaultdict
from itertools import count
import logging

# from blocky.effects import EffectLoader
import yaml

class EventLoader:
    """Loads stage events
    """
    def __init__(self, gamestate_manager, event_data, effect_manager):
        self.counter = count()
        self.effect_manager = effect_manager
        self.dispatch = {"time_elapsed": TimeElapsed}

    def load_events(self, event_data):
        events = defaultdict(list)
        for event_code, kwarg_params, effect_data in event_data:
            effects = []
            for effect_datum in effect_data:
                effects.append(self.effect_manager.create_effect(effect_datum))
            logging.debug("Loading event: {}".format(kwarg_params))
            event = self.dispatch[event_code](next(self.counter), effects, **kwarg_params)
            events[event.code].append(event)
        return events



    # @classmethod
    # def from_path(self, gamestate_manager, event_data, effect_manager):
    #     with open(effect_path) as f:
    #         return cls(gamestate_manager, event_data, yaml.load(f))

class EventManager:
    def __init__(self, gamestate_manager, event_data, effect_manager):
        self.gamestate_manager = gamestate_manager
        self.effect_manager = effect_manager
        self.event_loader = EventLoader(self.gamestate_manager, event_data, self.effect_manager)
        self.events = self.event_loader.load_events(event_data)
        self.load_dispatch = {}
        self.dispatch = {"time_elapsed": self._handle_time_elapsed}

    def register_event(self, event):
        self.events[event.type].append(event)

    def handle_event(self, event):
        pass

    def recieve_trigger(self, params):
        code = params["code"]
        logging.debug("RECEIVED_TRIGGER: {}".format(params))
        return self.dispatch[code](params)


    def _handle_time_elapsed(self, params=None):
        """Checks if a time_elapsed trigger has procced
        This must be generalized to handle the various time-elapsed type conditions
        """
        logging.debug("HANDLING TIME ELAPSED: {}".format(self.events))
        if not self.events["time_elapsed"]:
            logging.debug("h_time_elap: No events, skipped")
            return 0

        events = self.events["time_elapsed"]
        while events and events[0].check(self.gamestate_manager.round_counter):
            logging.info("Triggering event {}".format(events[0]))
            event = events.pop(0)
            event.execute()

    def _entity_death_handler(self, event):
        pass

    def _entity_in_region_handler(self, event):
        pass

    def _entity_hp_less_than_handler(self, event):
        pass

    def handle_turn_end(self):
        pass

class Event:
    def __init__(self, code, effects, id):
        self.id = id
        self.code = code
        self.effects = effects
        self.gamestate_manager = None
        self.effect_manager = None

    def __repr__(self):
        return "<Event: cond={}, effects={}>".format(self.code, self.effects)

    def link_gsm(self, gamestate_manager):
        self.gamestate_manager = gamestate_manager

    def link_em(self, effect_manager):
        self.effect_manager = effect_manager


class TimeElapsed(Event):
    def __init__(self, id, effects, time_elapsed, start=0):
        super().__init__(code="time_elapsed",
                         effects=effects, id=id)
        self.trigger_time = start + time_elapsed

    def __repr__(self):
        return "<TimeElapsed Event: triggers on: {}>".format(self.trigger_time)

    def __lt__(self, te_event):
        """Sorts the TimeElapsed events based off the activation timing, then order of creation
        """
        return (self.trigger_time, self.id) < (te_event.trigger_time, te_event.id)

    def check(self, current_time):
        return self.trigger_time <= current_time

    def execute(self):
        logging.debug("Executing effects: {}".format(self.effects))
        for effect in self.effects:
            effect.execute()


class DamageTaken(Event):
    def __init__(self):
        pass

class EntityHpLessThan(Event):
    def __init__(self):
        pass

class EntityKilled(Event):
    def __init__(self, entity):
        pass

class UnitInRegion(Event):
    pass


class MultiEvent:
    def __init__(self, events):
        # super().__init
        self.events = events

    def check(self):
        return all(i.check() for i in events())


if __name__ == "__main__":
    # Sample unit dies event
    # effects = 
    event_raw = ["time_elapsed", 3, ["spawn_unit", "knight_3", [2, 0, 0]]]
    # event = EntityKilled()