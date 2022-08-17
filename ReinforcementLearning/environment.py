from typing import Optional, List, Tuple

from TrafficSimulator import Simulation
from TrafficSimulator.Setups import two_way_intersection_setup


class Environment:
    def __init__(self):
        self.action_space: List = [0, 1]
        self.sim: Optional[Simulation] = None
        self.max_gen: int = 50
        self._vehicles_to_pass: int = 0  # Vehicles on inbound roads

    def step(self, step_action) -> Tuple[Tuple, float, bool, bool]:
        self.sim.run(step_action)
        new_state: Tuple = self.get_state()
        step_reward: float = self.get_reward(new_state)
        # Set the number of vehicles on inbound roads in the new state
        self._vehicles_to_pass = new_state[1] + new_state[2]
        # Whether a terminal state (as defined under the MDP of the task) is reached.
        terminated: bool = self.sim.completed
        # Whether a truncation condition outside the scope of the MDP is satisfied.
        # Ends the episode prematurely before a terminal state is reached.
        truncated: bool = self.sim.gui_closed
        return new_state, step_reward, terminated, truncated

    def get_state(self, reset: bool = False) -> Tuple:
        """ a state optimized for two_way_intersection:
        (signal_state, n_route_1_vehicles, n_route_2_vehicles, non_empty_junction)"""
        state = []
        traffic_signal = self.sim.traffic_signals[0]
        traffic_signal_state = traffic_signal.current_cycle[0]
        state.append(traffic_signal_state)
        if reset:
            state.extend([0, 0])
        else:
            for route in traffic_signal.roads:
                state.append(sum(len(road.vehicles) for road in route))  # n_vehicles in each route
        n_route_1_vehicles, n_route_2_vehicles = state[1], state[2]
        out_bound_vehicles = sum(len(self.sim.roads[i].vehicles) for i in [4, 5, 6, 7])
        non_empty_junction = bool(self.sim.n_vehicles_on_map - out_bound_vehicles -
                                  n_route_1_vehicles - n_route_2_vehicles)
        state.append(non_empty_junction)
        return tuple(state)

    def get_reward(self, state: Tuple) -> float:
        """ Check whether the flow change is positive or negative using the difference
        in the number of vehicles in the inbound roads from the previous state """
        signal_state, n_route_1_vehicles, n_route_2_vehicles, non_empty_junction = state
        flow_change = self._vehicles_to_pass - n_route_1_vehicles - n_route_2_vehicles
        return flow_change

    def render(self) -> None:
        self.sim.init_gui()

    def reset(self) -> Tuple:
        self.sim: Simulation = two_way_intersection_setup(self.max_gen)
        init_state: Tuple = self.get_state(reset=True)
        self._vehicles_to_pass = 0
        return init_state
