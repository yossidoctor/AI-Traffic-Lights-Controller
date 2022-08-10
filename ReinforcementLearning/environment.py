from typing import Tuple

from TrafficSimulator import Window, two_way_intersection

MAX_GEN = 50


class Environment:
    def __init__(self):
        """ Observation space (size: 142,800):
        State = (route1, route2)
        Route = (vehicle_1, ..., vehicle_n)
        Vehicle = (vehicle.x, vehicle.v, vehicle.a, signal_state)
        0 <= vehicle.x <= 49,   0 <= vehicle.v <= 16,   -4 <= vehicle.a <= 1,   0 <= signal_state <= 1 """
        self.window = Window()
        self.action_space = [0, 1]

    def get_state(self) -> Tuple[Tuple, Tuple]:
        def get_stats(vehicle) -> Tuple[int, int, int, bool]:
            signal_state = self.window.sim.roads[vehicle.path[vehicle.current_road_index]].traffic_signal_state
            return int(vehicle.x), int(vehicle.v), int(vehicle.a), signal_state

        west_east_indexes = [0, 2]
        west_east_roads = [self.window.sim.roads[i] for i in west_east_indexes]
        west_east_vehicles = [vehicle for road in west_east_roads for vehicle in road.vehicles]
        west_east_route = [get_stats(vehicle) for vehicle in west_east_vehicles]

        south_north_indexes = [1, 3]
        south_north_roads = [self.window.sim.roads[i] for i in south_north_indexes]
        south_north_vehicles = [vehicle for road in south_north_roads for vehicle in road.vehicles]
        south_north_route = [get_stats(vehicle) for vehicle in south_north_vehicles]

        return tuple(west_east_route), tuple(south_north_route)

    def step(self, step_action):
        self.window.run(step_action)

        new_state = self.get_state()

        step_reward = self.get_reward(new_state, step_action)

        # Whether a terminal state (as defined under the MDP of the task) is reached.
        terminated = self.window.sim.completed

        # Whether a truncation condition outside the scope of the MDP is satisfied.
        # Ends the episode prematurely before a terminal state is reached.
        truncated = self.window.closed

        return new_state, step_reward, terminated, truncated

    def get_reward(self, new_state, step_action):
        return 0

    def render(self):
        if not self.window.screen:
            self.window.init_display()

    def reset(self):
        self.window.sim = two_way_intersection(MAX_GEN)
        init_state = self.get_state()
        return init_state
