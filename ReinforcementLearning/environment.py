from gym.spaces import Discrete  # TODO: REMOVE

from TrafficSimulator import Window, two_way_intersection

WINDOW_ARGS = {'width': 1000, 'height': 700, 'zoom': 5.57}  # 1080p 14" laptop monitor with 150% scaling


class Environment:
    def __init__(self):
        self.generation_limit = 50
        self.window = Window(**WINDOW_ARGS)
        self.action_space = Discrete(2)
        # TODO: make it of length len(env.window.sim.traffic_signals)
        # TODO: remove Discrete action space

    def step(self, step_action, training=False):
        # Applies the action and runs a single simulation update cycle.
        self.window.run(step_action, training=training)

        new_state = self._get_new_state()

        # A calculated reward based on pre-defined parameters.
        step_reward = self._calculate_reward(new_state)

        # Whether a terminal state (as defined under the MDP of the task) is reached.
        terminated = self.window.sim.n_vehicles_on_map == 0 or self.window.sim.collision_detected

        # Whether a truncation condition outside the scope of the MDP is satisfied.
        # Ends the episode prematurely before a terminal state is reached.
        truncated = self.window.closed

        return new_state, step_reward, terminated, truncated

    def _get_new_state(self):
        # TODO: ADD DOCS
        new_state = []
        for i in range(4):
            road = self.window.sim.roads[i]
            signal_state = road.traffic_signal_state
            standing_vehicles = [vehicle for vehicle in road.vehicles if vehicle.is_stopped]
            n_standing_vehicles = len(standing_vehicles)
            has_standing_ems = any(vehicle.is_ems for vehicle in standing_vehicles)
            new_state.append((signal_state, n_standing_vehicles, has_standing_ems))
        return tuple(new_state)

    def _calculate_reward(self, new_state):
        # TODO: ADD DOCS
        step_reward = 0

        step_reward += self.window.sim.passed_green_signal  # TODO: ENCAPSULATE SIM ATTRIBUTE
        self.window.sim.passed_green_signal = 0  # Reset counter
        step_reward -= sum(standing_vehicles for x, standing_vehicles, z in new_state)
        step_reward -= sum(has_standing_ems for x, y, has_standing_ems in new_state) * 2
        if self.window.sim.collision_detected:
            step_reward -= 150
        return step_reward

    def render(self):
        """
        Renders the environment state with modes depending on the output
        """
        self.window.update_display()
        self.window.clock.tick(60)

    def reset(self):
        """
        Resets the environment to an initial state, returning the initial state.
        :return: the initial state
        """

        # dt = self.window.sim.dt if self.window.sim else 1 / 60  # for debugging purposes, todo: remove after completion
        self.window.sim = two_way_intersection(self.generation_limit)
        # self.window.sim.dt = dt  # for debugging purposes, todo: remove after completion
        self.window.update_display()
        init_state = tuple()
        return init_state

# todo:
#        fix ems average thing
#        clean up code, encapsulate sim data
#        train model on 1000+ iterations
#        send a switch action in a fixed cycle (move out of update)
