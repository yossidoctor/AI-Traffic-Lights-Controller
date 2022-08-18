from collections import deque
from typing import Deque, Optional

from scipy.spatial import distance

from TrafficSimulator.traffic_signal import TrafficSignal
from TrafficSimulator.vehicle import Vehicle


class Road:
    def __init__(self, start: int, end: int, index: int):
        self.start: int = start
        self.end: int = end
        self.index: int = index

        self.vehicles: Deque[Vehicle] = deque()

        self.length: float = distance.euclidean(self.start, self.end)
        self.angle_sin: float = (self.end[1] - self.start[1]) / self.length
        self.angle_cos: float = (self.end[0] - self.start[0]) / self.length

        self.has_traffic_signal: bool = False
        self.traffic_signal: Optional[TrafficSignal] = None
        self.traffic_signal_group: Optional[int] = None

    def set_traffic_signal(self, signal: TrafficSignal, group):
        self.has_traffic_signal = True
        self.traffic_signal = signal
        self.traffic_signal_group = group

    def __str__(self):
        return f'Road {self.index}'

    @property
    def traffic_signal_state(self):
        """ Returns the traffic signal state if the road has a traffic signal, else True"""
        if self.has_traffic_signal:
            i = self.traffic_signal_group
            return self.traffic_signal.current_cycle[i]
        return True

    def update(self, dt, sim_t):
        n = len(self.vehicles)
        if n > 0:
            lead: Vehicle = self.vehicles[0]
            # Check for traffic signal
            if self.traffic_signal_state:
                # If traffic signal is green or doesn't exist, let vehicles pass
                lead.unstop(sim_t)
                for vehicle in self.vehicles:
                    vehicle.unslow()
            elif lead.x <= self.length - self.traffic_signal.stop_distance / 2:
                # If traffic signal is red - slow and stop vehicles if they're able to slow safely
                if lead.x >= self.length - self.traffic_signal.slow_distance:
                    # Slow vehicles in slowing zone
                    lead.slow(self.traffic_signal.slow_factor)
                if self.length - self.traffic_signal.stop_distance <= lead.x:
                    # Stop vehicles in the stop zone
                    lead.stop(sim_t)

            # Update first vehicle
            lead.update(None, dt, self)
            # Update other vehicles
            for i in range(1, n):
                lead = self.vehicles[i - 1]
                self.vehicles[i].update(lead, dt, self)
