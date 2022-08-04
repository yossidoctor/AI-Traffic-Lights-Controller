from typing import List, Dict

from numpy.random import randint

from TrafficSimulator import Vehicle, Road


class VehicleGenerator:
    def __init__(self, sim, vehicle_rate, paths_dict):
        self.sim = sim
        self.vehicle_rate = vehicle_rate
        self.paths_dict: Dict[int, List[int]] = paths_dict
        self.last_added_time = 0

    def generate_vehicle(self):
        """Returns a random vehicle from self.vehicles with random proportions"""
        total = sum(weight for weight, path in self.paths_dict)
        r = randint(0, total)
        for (weight, path) in self.paths_dict:
            r -= weight
            if r <= 0:
                first_road = self.sim.roads[path[0]]
                return Vehicle(first_road, path)

    def update(self):
        """Generates a vehicle if the generation conditions are satisfied"""
        # If there's no vehicles on the map, or if the time elapsed after last
        # generation is greater than the vehicle rate, generate a vehicle
        time_elapsed = self.sim.t - self.last_added_time >= 60 / self.vehicle_rate
        if not self.sim.n_vehicles_generated or time_elapsed:
            vehicle: Vehicle = self.generate_vehicle()
            road: Road = self.sim.roads[vehicle.path[0]]
            # If the road is empty, or there's enough space for the generated vehicle, add it
            if not road.vehicles or road.vehicles[-1].x > vehicle.s0 + vehicle.length:
                # For debugging purposes, todo comment-out before project submission
                vehicle.generation_index = self.sim.n_vehicles_generated
                road.vehicles.append(vehicle)
                self.last_added_time = self.sim.t
                return True
        return False
