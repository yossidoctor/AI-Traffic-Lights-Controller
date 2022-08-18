from typing import Optional, List, Tuple

from TrafficSimulator import Simulation
from TrafficSimulator.Setups import two_way_intersection_setup


class Environment:
    def __init__(self):
        self.action_space: List = [0, 1]
        self.sim: Optional[Simulation] = None
        self.max_gen: int = 50
        self._vehicles_on_inbound_roads: int = 0

    def step(self, step_action) -> Tuple[Tuple, float, bool, bool]:
        self.sim.run(step_action)

        new_state: Tuple = self.get_state()

        step_reward: float = self.get_reward(new_state)

        # Set the number of vehicles on inbound roads in the new state
        n_west_east_vehicles, n_south_north_vehicles = new_state[1], new_state[2]
        self._vehicles_on_inbound_roads = n_west_east_vehicles + n_south_north_vehicles

        # Whether a terminal state (as defined under the MDP of the task) is reached.
        terminated: bool = self.sim.completed

        # Whether a truncation condition outside the scope of the MDP is satisfied.
        # Ends the episode prematurely before a terminal state is reached.
        truncated: bool = self.sim.gui_closed

        return new_state, step_reward, terminated, truncated

    def get_state(self) -> Tuple:
        """ a state optimized for two_way_intersection:
        west_east_signal_state, n_west_east_vehicles, n_south_north_vehicles, non_empty_junction"""
        west_east_signal_state = self.sim.roads[0].traffic_signal_state
        n_west_east_vehicles = sum(len(self.sim.roads[i].vehicles) for i in [0, 2])
        n_south_north_vehicles = sum(len(self.sim.roads[i].vehicles) for i in [1, 3])
        vehicles_on_outbound_roads = sum(len(self.sim.roads[i].vehicles) for i in [4, 5, 6, 7])
        non_empty_junction = bool(self.sim.n_vehicles_on_map - vehicles_on_outbound_roads -
                                  n_west_east_vehicles - n_south_north_vehicles)
        state = [west_east_signal_state, n_west_east_vehicles,
                 n_south_north_vehicles, non_empty_junction]
        return tuple(state)

    def get_reward(self, state: Tuple) -> float:
        """ Check whether the flow change is positive or negative using the difference
        in the number of vehicles in the inbound roads from the previous state """
        west_east_signal_state, n_west_east_vehicles, n_south_north_vehicles, non_empty_junction = state
        flow_change = self._vehicles_on_inbound_roads - n_west_east_vehicles - n_south_north_vehicles
        return flow_change

    def reset(self, render=False) -> Tuple:
        self.sim = two_way_intersection_setup(self.max_gen)
        if render:
            self.sim.render()
        init_state = self.get_state()
        self._vehicles_on_inbound_roads = 0
        return init_state
