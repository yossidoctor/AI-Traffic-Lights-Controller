from random import randint

from .vehicle import Vehicle


class VehicleGenerator:
    def __init__(self, sim, vehicle_rate, paths_dict, ems):
        self._sim = sim
        # todo: make _vehicle_rate adaptive, allow to change mid simulation -
        #  to simulate real-life conditions, with a randomness factor (line in _generate_vehicle)
        self.is_ems = ems
        self._vehicle_rate = vehicle_rate
        self._paths_dict = paths_dict  # {weight: path}
        self._last_gen_t = 0

    def _generate_vehicle(self):
        """Generates a random vehicle
        @rtype: Vehicle
        """
        total = sum(weight for weight, path in self._paths_dict)
        r = randint(0, total)
        for (weight, path) in self._paths_dict:
            r -= weight
            if r <= 0:
                first_road = self._sim.roads[path[0]]
                return Vehicle(path, first_road.start, self.is_ems)

    def update(self):
        """Generates a vehicle if the generation conditions are satisfied
        @rtype: bool
        """
        # If there's no vehicles on the map, or if the time elapsed after last
        # generation is greater than the vehicle rate, generate a vehicle
        if not self._sim.n_vehicles_generated or self._sim.t - self._last_gen_t >= 60 / self._vehicle_rate:
            vehicle = self._generate_vehicle()
            road = self._sim.roads[vehicle.path[0]]
            # If the road is empty, or there's enough space for the generated vehicle, add it
            if not road.vehicles or road.vehicles[-1].x > vehicle.s0 + vehicle.length:
                vehicle.generation_index = self._sim.n_vehicles_generated  # for debugging purposes
                road.vehicles.append(vehicle)
                self._last_gen_t = self._sim.t
                return True
        return False
