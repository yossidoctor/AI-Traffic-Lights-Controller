import numpy as np
from gym import Env
from gym.spaces import Discrete, Box, Tuple

from TrafficSimulator import Window, two_way_intersection

WINDOW_ARGS = {'width': 1000, 'height': 700, 'zoom': 5.57}  # 1080p 14" laptop monitor with 150% scaling


class TrafficEnvironment(Env):
    def __init__(self):
        """
        The Action Space object corresponding to valid actions: Switch (1) and Don't Switch (0)
        The Observation Space object corresponding to valid observations:
        A tuple of 2 arrays of the waiting times of civilian and ems vehicles on the map
        """
        self.generation_limit = 30
        self.window = Window(**WINDOW_ARGS)
        self.action_space = Discrete(2)
        observation_space = Box(low=np.array([0]), high=np.array([self.generation_limit]))
        self.observation_space = Tuple(spaces=(observation_space, observation_space))
        self.observation = 0, 0

    def step(self, step_action: int):
        """
        Takes a step in the environment using an action returning the next observation, reward,
        if the environment terminated and more information.
        :param step_action: 1 (Switch) or 0 (Don't Switch)
        """
        # Applies the action and runs a single simulation update cycle.
        self.window.run(step_action)

        new_observation = self.window.sim.average_wait_time, self.window.sim.average_ems_wait_time

        # A calculated reward based on pre-defined parameters.
        step_reward = self._calculate_reward(*new_observation)

        # Whether a terminal state (as defined under the MDP of the task) is reached.
        terminated = self.window.sim.n_vehicles_on_map == 0 or self.window.sim.collision_detected

        # truncated - whether a truncation condition outside the scope of the MDP is satisfied.
        # Ends the episode prematurely before a terminal state is reached.
        step_info = {'truncated': self.window.closed}

        return new_observation, step_reward, terminated, step_info

    def _calculate_reward(self, average_wait_time, average_ems_wait_time):
        # self.average_wait_time = 0
        # self.average_ems_wait_time = 0
        if self.window.sim.collision_detected:
            step_reward = -100
        else:
            if average_wait_time >= self.observation[0]:
                step_reward = -1
            else:
                step_reward = 3
            if average_ems_wait_time >= self.observation[1]:
                step_reward -= 3
            else:
                step_reward += 6

        return step_reward

    def render(self, episode_data):
        """
        Renders the environment observation with modes depending on the output
        """
        self.window.update_display(episode_data)
        self.window.clock.tick(60)

    def reset(self, episode_data):
        """
        Resets the environment to an initial state, returning the initial observation.
        :return: the initial observation
        """
        # for debugging purposes, todo: remove after completion
        dt = self.window.sim.dt if self.window.sim else 1 / 60

        self.window.sim = two_way_intersection(self.generation_limit)
        self.window.sim.dt = dt  # for debugging purposes, todo: remove after completion
        self.window.update_display(episode_data)
        self.observation = 0, 0

        return self.observation


env = TrafficEnvironment()

n_episodes = 10
for episode in range(1, n_episodes + 1):
    state = env.reset((0, n_episodes))
    done = False
    truncated = False
    score = 0

    while not done:
        env.render((episode, n_episodes))
        action = env.action_space.sample()  # agent action
        new_state, reward, done, info = env.step(action)
        if info['truncated']:
            truncated = True
            break
        score += reward

    if truncated:
        break

    print('Episode:{} Score:{}'.format(episode, score))
