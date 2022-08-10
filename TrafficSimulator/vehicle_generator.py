from typing import List, Dict

from numpy.random import randint

from TrafficSimulator import Vehicle, Road


class VehicleGenerator:
    def __init__(self, vehicle_rate, paths: List[List], inbound_roads: Dict[int, Road]):
        self._inbound_roads: Dict[int: Road] = inbound_roads
        self._vehicle_rate = vehicle_rate
        self._paths: List[List] = paths
        self._last_added_time = 0

    def _generate_vehicle(self):
        """Returns a random vehicle from self.vehicles with random proportions"""
        total = sum(weight for weight, path in self._paths)
        r = randint(0, total)
        for (weight, path) in self._paths:
            r -= weight
            if r <= 0:
                return Vehicle(path)

    def update(self, sim_t, n_vehicles_generated):
        """Generates a vehicle if the generation conditions are satisfied"""
        # If there's no vehicles on the map, or if the time elapsed after last
        # generation is greater than the vehicle rate, generate a vehicle
        time_elapsed = sim_t - self._last_added_time >= 60 / self._vehicle_rate
        if (not n_vehicles_generated) or time_elapsed:
            vehicle: Vehicle = self._generate_vehicle()
            road: Road = self._inbound_roads[vehicle.path[0]]
            # If the road is empty, or there's enough space for the generated vehicle, add it
            if not road.vehicles or road.vehicles[-1].x > vehicle.s0 + vehicle.length:
                vehicle.index = n_vehicles_generated
                vehicle.position = road.start
                road.vehicles.append(vehicle)
                self._last_added_time = sim_t
                return True
        return False
