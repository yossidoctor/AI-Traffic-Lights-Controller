from collections import deque

from scipy.spatial import distance


class Road:
    def __init__(self, start, end):
        self.start = start
        self.end = end
        self.vehicles = deque()

        self.length = distance.euclidean(self.start, self.end)
        self.angle_sin = (self.end[1] - self.start[1]) / self.length
        self.angle_cos = (self.end[0] - self.start[0]) / self.length

        self.traffic_signal = None
        self.traffic_signal_group = None
        self.has_traffic_signal = False

    def set_traffic_signal(self, signal, group):
        self.traffic_signal = signal
        self.traffic_signal_group = group
        self.has_traffic_signal = True

    @property
    def traffic_signal_state(self):
        if self.has_traffic_signal:
            i = self.traffic_signal_group
            return self.traffic_signal.current_cycle[i]
        return True

    def update(self, dt, t):
        """
        Updates all the vehicles on the road, depending on traffic and traffic signal conditions
        :param dt: simulation time step
        :param t: simulation time
        """
        n = len(self.vehicles)

        # TODO: FIX: WHEN SWITCHING TO A RED LIGHT FOR A VEHICLE THAT APPROACHES A TRAFFIC LIGHT AT HIGH SPEED
        #  AND ITS CLOSE, THE VEHICLE DOESNT STOP.

        if n > 0:
            # Update first vehicle
            self.vehicles[0].update(None, dt)
            # Update other vehicles
            for i in range(1, n):
                lead = self.vehicles[i - 1]
                self.vehicles[i].update(lead, dt)

            # Check for traffic signal
            if self.traffic_signal_state:
                # If traffic signal is green or doesn't exist, let the vehicles through
                self.vehicles[0].unstop(t)
                for vehicle in self.vehicles:
                    vehicle.unslow()
            else:
                # If traffic signal is red
                if self.vehicles[0].x >= self.length - self.traffic_signal.slow_distance:
                    # Slow vehicles in slowing zone
                    self.vehicles[0].slow(self.traffic_signal.slow_factor * self.vehicles[0]._v_max)
                slow_distance = self.traffic_signal.stop_distance
                if self.length - slow_distance <= self.vehicles[0].x <= self.length - slow_distance / 2:
                    # Stop vehicles in the stop zone
                    self.vehicles[0].stop(t)
