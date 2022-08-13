import abc
from Search.state import *

class MultiAgentSearchAgent:
    """
    This class provides some common elements to all of your
    multi-agent searchers.  Any methods defined here will be available
    to the MinmaxAgent, AlphaBetaAgent & ExpectimaxAgent.
    You *do not* need to make any changes here, but you can if you want to
    add functionality to all your adversarial search agents.  Please do not
    remove anything, however.
    Note: this is an abstract class: one that should not be instantiated.  It's
    only partially specified, and designed to be extended.  Agent (game.py)
    is another abstract class.
    """

    def __init__(self, evaluation_function, depth=2):
        self.evaluation_function = evaluation_function
        self.depth = depth

    @abc.abstractmethod
    def get_action(self, state):
        return


class MinmaxAgent(MultiAgentSearchAgent):

    def in_depth_max_player(self, state, level):
        act_list = state.get_legal_actions()
        if level == self.depth or state.is_terminal():
            return self.evaluation_function(state), Action.STOP
        i = 0
        successor_dict = dict()
        values_dict = dict()
        act_dict = dict()
        for act in act_list:
            child = state.generate_successor(act)
            value, given_action = self.in_depth_min_pc(child, level)
            successor_dict[i] = child
            values_dict[i] = value
            act_dict[i] = act
            i += 1
        chosen_index = max(values_dict, key=values_dict.get)
        return values_dict[chosen_index], act_dict[chosen_index]

    def in_depth_min_pc(self, state, level):
        act_list = state.get_legal_actions()
        if level == self.depth or state.is_terminal():
            return self.evaluation_function(state), Action.STOP
        i = 0
        successor_dict = dict()
        values_dict = dict()
        act_dict = dict()
        for act in act_list:
            child = state.generate_successor(act)
            value, given_action = self.in_depth_max_player(child, level + 1)
            successor_dict[i] = child
            values_dict[i] = value
            act_dict[i] = act
            i += 1
        chosen_index = min(values_dict, key=values_dict.get)
        return values_dict[chosen_index], act_dict[chosen_index]

    def get_action(self, state):
        successor, action = self.in_depth_max_player(state, 0)
        return action
