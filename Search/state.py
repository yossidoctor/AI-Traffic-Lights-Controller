from enum import Enum
from TrafficSimulator.window import Window
import copy



class Action(Enum):
    OFF = 0
    ON = 1
    STOP = 2


class State:
    def __init__(self, my_window):
        self.window = my_window

    def is_terminal(self):
        return self.window.sim.completed

    def get_legal_actions(self):
        # we need to know if there are cars in the junction-if so so do nothing
        # if not, we need to list all the legal combinations of traffic lights
        # in the junction
        if len(self.window.sim.intersections) > 0:
            return [Action.STOP]
        # only in case of one dual lights
        return [0, 1]

    def score(self):
        # the amount of cars that passed junction-the amount of cars that
        # are waiting in the junction
        return self.window.sim.get_passed_junction()

    def apply_action(self, action):
        # apply the action in the simulation
        if action != Action.STOP:
            self.window.run(action)

    def generate_successor(self, action):
        # create a new state and apply the action on the new state
        if action == Action.STOP:
            return None
        successor = State(Window(self.window.sim))
        successor.apply_action(action)
        return successor
