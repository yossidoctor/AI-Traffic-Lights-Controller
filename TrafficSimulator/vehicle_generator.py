from random import randint

from .vehicle import Vehicle


class VehicleGenerator:
    def __init__(self, sim, vehicle_rate, paths_dict, ems):
        self._sim = sim
        # todo: make _vehicle_rate adaptive, allow to change mid simulation -
        #  to simulate real-life conditions
        self.is_ems = ems
        self._vehicle_rate = vehicle_rate
        self._paths_dict = paths_dict  # {weight: path}
        self._last_added_time = 0
        self._upcoming_vehicle = self._generate_vehicle()

    def _generate_vehicle(self):
        """Returns a random vehicle from self.vehicles with random proportions"""
        total = sum(weight for weight, path in self._paths_dict)
        r = randint(0, total)
        for (weight, path) in self._paths_dict:
            r -= weight
            if r <= 0:
                first_road = self._sim.roads[path[0]]
                return Vehicle(path, first_road.start, self.is_ems)

    def update(self, vehicle_index):
        """Adds a vehicle"""
        vehicle_generated = False
        # If there's no vehicles on the map, or if the time elapsed after last
        # generation is greater than the vehicle rate, generate a vehicle
        if not self._sim.n_vehicles_generated or self._sim.t - self._last_added_time >= 60 / self._vehicle_rate:
            road = self._sim.roads[self._upcoming_vehicle.path[0]]
            if len(road.vehicles) == 0 or \
                    road.vehicles[-1].x > self._upcoming_vehicle.s0 + self._upcoming_vehicle.length:
                # If there is space for the generated vehicle; add it
                self._upcoming_vehicle.time_added = self._sim.t
                self._upcoming_vehicle.index = vehicle_index  # for debugging purposes, todo: remove after completion
                road.vehicles.append(self._upcoming_vehicle)
                self._last_added_time = self._sim.t
                vehicle_generated = True
            # Prepare a vehicle for the next generation
            self._upcoming_vehicle = self._generate_vehicle()
        return vehicle_generated