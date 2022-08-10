from collections import deque
from typing import Deque

from scipy.spatial import distance

from TrafficSimulator.vehicle import Vehicle


class Road:
    def __init__(self, start, end, index):
        self.start = start
        self.end = end
        self.index = index

        self.vehicles: Deque[Vehicle] = deque()

        self.length = distance.euclidean(self.start, self.end)
        self.angle_sin = (self.end[1] - self.start[1]) / self.length
        self.angle_cos = (self.end[0] - self.start[0]) / self.length
        self.has_traffic_signal = False

        self.traffic_signal = None
        self.traffic_signal_group = None
        self.has_traffic_signal = False

    def set_traffic_signal(self, signal, group):
        self.traffic_signal = signal
        self.traffic_signal_group = group
        self.has_traffic_signal = True

    def __str__(self):
        return f'{self.index}'

    @property
    def traffic_signal_state(self):
        if self.has_traffic_signal:
            i = self.traffic_signal_group
            return self.traffic_signal.current_cycle[i]
        return True

    def update(self, dt, sim_t):
        n = len(self.vehicles)

        if n > 0:
            # Update first vehicle
            self.vehicles[0].update(None, dt, self)
            # Update other vehicles
            for i in range(1, n):
                lead = self.vehicles[i - 1]
                self.vehicles[i].update(lead, dt, self)

            lead: Vehicle = self.vehicles[0]
            # Check for traffic signal
            if self.traffic_signal_state:
                # If traffic signal is green or doesn't exist, let vehicles pass
                lead.unstop(sim_t)
                for vehicle in self.vehicles:
                    vehicle.unslow()
            else:
                # If traffic signal is red
                if lead.x >= self.length - self.traffic_signal.slow_distance:
                    # Slow vehicles in slowing zone
                    lead.slow(self.traffic_signal.slow_factor * lead._v_max)
                if self.length - self.traffic_signal.stop_distance <= lead.x <= \
                        self.length - self.traffic_signal.stop_distance / 2:
                    # Stop vehicles in the stop zone
                    lead.stop(sim_t)
