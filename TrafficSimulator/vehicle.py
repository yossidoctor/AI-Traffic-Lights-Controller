import numpy as np

RED = (255, 51, 51)
BLUE = (51, 51, 255)


class Vehicle:
    def __init__(self, path, position, is_ems):
        self.path = path
        self.current_road_index = 0

        self.position = position

        self.is_ems = is_ems
        self.ems_color = RED

        self.is_stopped = False
        self.last_stop_t = None
        self.last_ems_update_t = 0
        self.total_standing_t = 0

        self.generation_index = None  # for debugging purposes, initiated at vehicle generator

        self.length = 4
        self.width = 2

        self.s0 = 5
        self.T = 1
        self.v_max = 16.6
        self.a_max = 1.44
        self.b_max = 4.61
        self.sqrt_ab = 2 * np.sqrt(self.a_max * self.b_max)
        self._v_max = self.v_max
        self.x = 0
        self.v = self.v_max
        self.a = 0

    def update_ems_color(self):
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

        if self.is_stopped:
            self.a = -self.b_max * self.v / self.v_max

    def stop(self, t):
        self.last_stop_t = t
        self.is_stopped = True

    def unstop(self, t):
        if self.is_stopped:
            standing_time = t - self.last_stop_t
            self.total_standing_t += standing_time
            self.last_stop_t = None
        self.is_stopped = False

    def slow(self, v):
        self.v_max = v

    def unslow(self):
        self.v_max = self._v_max
