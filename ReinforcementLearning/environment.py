from typing import Optional, List

from TrafficSimulator import Simulation
from two_way_intersection import setup


class Environment:
    def __init__(self):
        self.max_gen: int = 30
        self.sim: Optional[Simulation] = None
        self.action_space: List = [0, 1]
        self._vehicles_to_pass: int = 0  # Vehicles on inbound roads

    def step(self, step_action):
        self.sim.run(step_action)
        new_state = self.get_state(step_action)
        step_reward: float = self.get_reward(new_state)
        # Set the number of vehicles on inbound roads in the new state
        self._vehicles_to_pass = new_state[1] + new_state[2]
        # Whether a terminal state (as defined under the MDP of the task) is reached.
        terminated = self.sim.completed
        # Whether a truncation condition outside the scope of the MDP is satisfied.
        # Ends the episode prematurely before a terminal state is reached.
        truncated = self.sim.gui_closed
        return new_state, step_reward, terminated, truncated

    def get_state(self, reset=False):
        """ a state optimized for two_way_intersection:
        (signal_state, n_route_1_vehicles, n_route_2_vehicles)"""
        state = []
        traffic_signal = self.sim.traffic_signals[0]
        traffic_signal_state = traffic_signal.current_cycle[0]
        state.append(traffic_signal_state)
        if reset:
            state.extend([0, 0])
        else:
            for route in traffic_signal.roads:
                state.append(sum(len(road.vehicles) for road in route))  # n_vehicles in each route
        return tuple(state)

    def get_reward(self, state):
        signal_state, n_route_1_vehicles, n_route_2_vehicles = state
        collision_factor = -50 * self.sim.collision_detected  # (high-weighted negative reward)
        # Check whether the flow change is positive or negative using the difference in the number
        # of vehicles in the inbound roads from the previous state (low-weighted positive reward)
        flow_change = self._vehicles_to_pass - n_route_1_vehicles - n_route_2_vehicles
        return flow_change + collision_factor

    def render(self):
        self.sim.init_gui()

    def reset(self):
        self.sim = setup(self.max_gen)
        init_state = self.get_state(reset=True)
        self._vehicles_to_pass = 0
        return init_state
