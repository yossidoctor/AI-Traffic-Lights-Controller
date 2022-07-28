import numpy as np

RED = (255, 51, 51)
BLUE = (51, 51, 255)


class Vehicle:
    def __init__(self, generation_time, path, position, ems):
        """
        :param generation_time: simulation time at which the vehicle was generated
        :param path: a list of road indexes
        :param position: simulation position (x, y)
        """
        self.position = position
        self.path = path
        self.current_road_index = 0
        self.generation_time = generation_time
        self.total_standing_time = 0
        self.ems = ems
        self.ems_color = RED
        self._is_stopped = False
        self._last_time_stopped = 0

        # for debugging purposes, remove after completion
        self.index = None  # Initiated at vehicle generator
        self.color = (0, 0, 0) if ems else (0, 0, 255)
        self.crashed = False

        self.length = 4
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

    def change_ems_color(self):
        if self.ems_color == RED:
            self.ems_color = BLUE
        else:
            self.ems_color = RED

    def update(self, lead, dt):
        """
        Updates the vehicle position, velocity and acceleration
        :param lead: leading vehicle
        :param dt: simulation time step
        """

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

        if self._is_stopped:
            self.a = -self.b_max * self.v / self.v_max

    def stop(self, time):
        self._last_time_stopped = time
        self._is_stopped = True

    def unstop(self, time):
        if self._is_stopped:
            standing_time = time - self._last_time_stopped
            self.total_standing_time += standing_time
            self._last_time_stopped = 0
        self._is_stopped = False

    def slow(self, v):
        self.v_max = v

    def unslow(self):
        self.v_max = self._v_max
