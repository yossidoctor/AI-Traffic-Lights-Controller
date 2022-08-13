from typing import Tuple

from TrafficSimulator import Window, two_way_intersection


class Environment:
    def __init__(self):
        """ Observation space:
        State = (vehicle, n_green_route_vehicles, n_red_route_vehicles)  # 181 * 16 * 16 = 46336
        vehicle: closest lead vehicle to a red traffic light
        n_{color}_route_vehicles: the number of vehicles on the route with {color} traffic light
        Vehicle = (vehicle.x, vehicle.v, signal_state)  # n = 10 * 9 * 2 + 1 (for None) = 181
        vehicle.x: {0, 5, 10, ..., 45} (rounded down),   vehicle.v: {0, 2, 4, ..., 16},   signal_state: {0, 1} """
        self.max_gen = 30
        self.window = Window()
        self.observation_space_size = 46336
        self.action_space = [0, 1]

    def get_state(self) -> Tuple[Tuple, Tuple]:
        # todo: don't forget to round (int()) the vehicle stats
        return ()

    def step(self, step_action):
        self.window.run(step_action)

        new_state = self.get_state()

        step_reward = self.get_reward(new_state)

        # Whether a terminal state (as defined under the MDP of the task) is reached.
        terminated = self.window.sim.completed

        # Whether a truncation condition outside the scope of the MDP is satisfied.
        # Ends the episode prematurely before a terminal state is reached.
        truncated = self.window.closed

        return new_state, step_reward, terminated, truncated

    def get_reward(self, state):
        # todo: check if any lead vehicle is unable to stop and it has a red light (low-weighted negative reward)
        # todo: check how many vehicles passed since the last step, for positive reward (low-weighted positive reward)
        # todo: check if simulation completed (high-weighted positive reward)
        # todo: check if there's any collisions (high-weighted negative reward)
        return 0

    def render(self):
        if not self.window.screen:
            self.window.init_screen()
        self.window.update_screen()

    def reset(self):
        self.window.sim = two_way_intersection(self.max_gen)
        init_state = self.get_state()
        return init_state
