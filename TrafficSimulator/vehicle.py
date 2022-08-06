from typing import List, Tuple

import numpy as np


class Vehicle:
    def __init__(self, first_road, path: List[int]):
        self.length = 4
        self.width = 2
        self.s0 = 4
        self.T = 1
        self.v_max = 16.6
        self.a_max = 1.44
        self.b_max = 4.61
        self.sqrt_ab = 2 * np.sqrt(self.a_max * self.b_max)
        self._v_max = self.v_max

        self.x = 0
        self.v = self.v_max
        self.a = 0

        self.is_stopped = False
        self._waiting_time = 0
        self.last_time_stopped = None

        self.path: List[int] = path
        self.position: Tuple = first_road.start
        self.current_road_index = 0

        # For debugging purposes, todo comment-out before project submission
        self.generation_index = 0

    def get_waiting_time(self, sim_t):
        if self.is_stopped:
            return self._waiting_time + (sim_t - self.last_time_stopped)
        return self._waiting_time

    def update(self, lead, dt, road):
        # Update position and velocity
        if self.v + self.a * dt < 0:
            self.x -= 1 / 2 * self.v * self.v / self.a
            self.v = 0
        else:
            self.v += self.a * dt
            self.x += self.v * dt + self.a * dt * dt / 2

        # Update acceleration
        alpha = 0
        if lead:
            delta_x = lead.x - self.x - lead.length
            delta_v = self.v - lead.v

            alpha = (self.s0 + max(0, self.T * self.v + delta_v * self.v / self.sqrt_ab)) / delta_x

        self.a = self.a_max * (1 - (self.v / self.v_max) ** 4 - alpha ** 2)

        if self.is_stopped:
            self.a = -self.b_max * self.v / self.v_max

        # Update position
        sin, cos = road.angle_sin, road.angle_cos
        x = road.start[0] + cos * self.x
        y = road.start[1] + sin * self.x
        self.position = x, y

    def stop(self, t):
        if not self.is_stopped:
            self.last_time_stopped = t
            self.is_stopped = True

    def unstop(self, t):
        if self.is_stopped:
            self._waiting_time += (t - self.last_time_stopped)
            self.last_time_stopped = None
            self.is_stopped = False

    def slow(self, v):
        self.v_max = v

    def unslow(self):
        self.v_max = self._v_max
