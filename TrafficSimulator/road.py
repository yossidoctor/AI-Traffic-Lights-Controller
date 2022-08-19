from collections import deque
from typing import Deque, Optional, Tuple

from scipy.spatial import distance

from TrafficSimulator.traffic_signal import TrafficSignal
from TrafficSimulator.vehicle import Vehicle


class Road:
    def __init__(self, start: Tuple[int, int], end: Tuple[int, int], index: int):
        self.start = start
        self.end = end
        self.index = index

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
            lead_in_safe_zone = lead.x <= self.length - self.traffic_signal.stop_distance / 2
            # Check for traffic signal
            if self.traffic_signal_state:
                # If traffic signal is green or doesn't exist, let vehicles pass
                lead.unstop(sim_t)
                for vehicle in self.vehicles:
                    vehicle.unslow()
            elif lead_in_safe_zone:
                # If traffic signal is red, and the lead vehiclein the safe zone
                lead.slow(self.traffic_signal.slow_factor)  # slow vehicles in slow zone
                lead_in_stop_zone = self.length - self.traffic_signal.stop_distance <= lead.x
                if lead_in_stop_zone:
                    lead.stop(sim_t)
            # else, if there's a red/yellow light and the vehicle isn't in the safe zone
            # just let it pass

            # Update first vehicle
            lead.update(None, dt, self)
            # Update other vehicles
            for i in range(1, n):
                lead = self.vehicles[i - 1]
                self.vehicles[i].update(lead, dt, self)
