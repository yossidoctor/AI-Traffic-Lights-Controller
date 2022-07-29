import numpy as np
from gym import Env
from gym.spaces import Discrete, Box

from TrafficSimulatorGUI import Window
from simulation_setup import two_way_intersection

# 1080p 14" laptop monitor with 150% scaling
WINDOW_ARGS = {'width': 1000, 'height': 700, 'zoom': 6}


class TrafficEnvironment(Env):
    def __init__(self):
        """
        The Action Space object corresponding to valid actions: Switch (1) and Don't Switch (0)
        The Observation Space object corresponding to valid observations:
        An array of the waiting times of all the vehicles on the map
        """
        self.generation_limit = 30
        self.window = Window(**WINDOW_ARGS)
        self.action_space = Discrete(2)
        self.observation_space = Box(low=np.array([0]), high=np.array([self.generation_limit]))
        self.observation = 0

    def step(self, action: int):
        """
        Takes a step in the environment using an action returning the next observation, reward,
        if the environment terminated and more information.
        :param action: 1 (Switch) or 0 (Don't Switch)
        """
        # Applies the action and runs a single simulation update cycle.
        self.window.run(action)

        new_observation = self.window.sim.average_wait_time

        # A calculated reward based on pre-defined parameters.
        reward = self.calculate_reward(new_observation)

        # Whether a terminal state (as defined under the MDP of the task) is reached.
        terminated = self.window.sim.n_vehicles_on_map == 0 or self.window.sim.collision_detected

        # Whether a truncation condition outside the scope of the MDP is satisfied.
        # Ends the episode prematurely before a terminal state is reached.
        truncated = self.window.closed

        # Step information
        info = {}

        # Return step information
        return new_observation, reward, terminated, truncated, info

    def calculate_reward(self, new_observation):
        if self.window.sim.collision_detected:
            reward = -100
        else:
            if new_observation >= self.observation:
                reward = -1
            else:
                reward = 3
        return reward

    def render(self, mode="human"):
        """
        Renders the environment observation with modes depending on the output
        """
        self.window.update_display()
        self.window.clock.tick(60)

    def reset(self):
        """
        Resets the environment to an initial state, returning the initial observation.
        :return: the initial observation
        """
        self.window.sim = two_way_intersection(generation_limit=self.generation_limit)
        self.window.update_display()
        self.observation = 0

        return self.observation


env = TrafficEnvironment()

# from gym.utils.env_checker import check_env
# check_env(env) # todo

episodes = 10
for episode in range(1, episodes + 1):
    state = env.reset()
    terminated = False
    truncated = False
    score = 0

    while not terminated:
        env.render()
        action = env.action_space.sample()
        new_state, reward, terminated, truncated, info = env.step(action)
        if truncated:
            break
        score += reward
    if truncated:
        break

    print('Episode:{} Score:{}'.format(episode, score))
