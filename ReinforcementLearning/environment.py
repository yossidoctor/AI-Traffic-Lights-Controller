from gym.spaces import Discrete

from TrafficSimulator import Window, two_way_intersection

WINDOW_ARGS = {'width': 1000, 'height': 700, 'zoom': 5.57}  # 1080p 14" laptop monitor with 150% scaling


class Environment:
    def __init__(self):
        self.generation_limit = 50
        self.window = Window(**WINDOW_ARGS)
        self.action_space = Discrete(2)  # TODO: remove Discrete action space

    def step(self, step_action, training=False):
        # Applies the action and runs a single simulation update cycle.
        self.window.run(step_action, training=training)

        new_state = self._get_new_state()

        # A calculated reward based on pre-defined parameters.
        step_reward = self._calculate_reward(new_state, step_action)

        # Whether a terminal state (as defined under the MDP of the task) is reached.
        terminated = self.window.sim.completed or self.window.sim.collision_detected

        # Whether a truncation condition outside the scope of the MDP is satisfied.
        # Ends the episode prematurely before a terminal state is reached.
        truncated = self.window.closed

        return new_state, step_reward, terminated, truncated

    def _get_new_state(self):
        # TODO: ADD DOCS
        # for group in [[0, 2], [1, 3]]
        green_roads, red_roads, cycle = self.window.sim.get_green_light_roads()
        return tuple(green_roads), tuple(red_roads), cycle

    def _calculate_reward(self, new_state, step_action):
        if step_action:
            return -self.window.sim.risk_factor  # if switch and there was a risk factor, bad. if there was no risk, its fine cuz its 0 and fine.
        return 0
        # risk_factor = sum(risk_factor for x, y, z, risk_factor in new_state)
        # civ_factor = 5 * sum(n_standing_vehicles for x, n_standing_vehicles, z, w in new_state)
        # ems_factor = 10 * sum(n_standing_ems_vehicles for x, y, n_standing_ems_vehicles, w in new_state)
        # # print(ems_factor)
        # return -risk_factor - ems_factor - civ_factor

        # TODO: ADD DOCS
        # step_reward = -self.window.sim.risk_factor
        # # print(step_reward)
        #

        # # step_reward += self.window.sim.passed_green_signal  # TODO: ENCAPSULATE SIM ATTRIBUTE
        # # self.window.sim.passed_green_signal = 0  # Reset counter
        # test = sum(standing_vehicles for x, standing_vehicles, z in new_state)
        # print(test)
        # step_reward -= sum(standing_vehicles for x, standing_vehicles, z in new_state)
        # # step_reward -= sum(has_standing_ems for x, y, has_standing_ems in new_state) * 2
        # if self.window.sim.collision_detected:
        #     step_reward -= 150
        # return step_reward

    def render(self):
        """
        Renders the environment state with modes depending on the output
        """
        self.window.update_display()

    def reset(self, training=False):
        """
        Resets the environment to an initial state, returning the initial state.
        :return: the initial state
        """
        self.window.sim = two_way_intersection(self.generation_limit)
        if not training:
            self.render()
        init_state = tuple()
        return init_state

# todo:
#        fix ems average thing
#        clean up code, encapsulate sim data
#        train model on 1000+ iterations
#        send a switch action in a fixed cycle (move out of update)
