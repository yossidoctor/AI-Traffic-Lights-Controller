from tensorforce import Environment
import numpy as np
from trafficSimulator.two_way_intersection import two_way_intersection, Simulation


class IntersectionEnvironment(Environment):

    def __init__(self):
        super().__init__()
        self.intersection: Simulation = two_way_intersection()

    def states(self):
        return dict(type='Simulation')

    def actions(self):
        return {'switch': dict(type='int', num_values=2)}  # EW, NS

    # Optional: should only be defined if environment has a natural fixed
    # maximum episode length; restrict training timesteps via
    #     Environment.create(..., max_episode_timesteps=???)
    def max_episode_timesteps(self):
        return super().max_episode_timesteps()

    # Optional additional steps to close environment
    def close(self):
        super().close()

    def reset(self):
        state = np.random.random(size=(8,))
        return state

    def execute(self, actions):
        next_state = np.random.random(size=(8,))
        terminal = np.random.random() < 0.5
        reward = np.random.random()
        return next_state, terminal, reward

    def terminal(self):
        return self.intersection.vehicles_on_map == 0

    def reward(self):
        # self.intersection.average_wait_time
        # self.intersection.vehicles_on_map
        # self.intersection.average_wait_time of ems vehicles
        # self.intersection.vehicles_on_map of ems vehicles
        pass
