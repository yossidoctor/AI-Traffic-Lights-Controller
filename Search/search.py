from TrafficSimulator import *
from Search.search_agents import MinmaxAgent
from Search.state import State, Action

MAX_GEN = 50

def eval(state):
    return state.score()

class GameRunner:
    def __init__(self, state, agent):
        self._state = state
        self._agent = agent



if __name__ == '__main__':
    sim = two_way_intersection(MAX_GEN)
    window = Window(sim)

    current_state = State(window)
    current_state.window.init_display()
    search_agent = MinmaxAgent(eval, 4)


    while(not current_state.is_terminal()):
        action = search_agent.get_action(current_state)
        if action == Action.STOP:
            break

        current_state.apply_action(action)

