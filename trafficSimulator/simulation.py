from copy import deepcopy
from itertools import chain
from statistics import mean

from scipy.spatial import distance

from .road import Road
from .traffic_signal import TrafficSignal
from .vehicle_generator import VehicleGenerator


class Simulation:
    def __init__(self):
        self.t = 0.0  # Time keeping
        self.dt = 1 / 60  # Simulation time step
        self.frame_count = 0  # Frame time keeping
        self.roads = []
        self.vehicle_generators = set()
        self.traffic_signals = set()

        self._intersections = {}

        self.vehicles_generated = 0
        self.vehicles_on_map = 0
        self.vehicles_reached_destination = 0

        self.journey_times = []
        self.standing_times = []
        self.average_wait_time = 0
        self.average_journey_time = 0

    def non_empty_roads(self, roads=None) -> set:
        """
        :param roads: a list of road indexes, by default range(len(self.roads))
        :return: a set of non-empty road indexes
        """
        if not roads:
            roads = range(len(self.roads))
        return set(filter(lambda road: self.roads[road].vehicles, roads))

    @property
    def intersections(self) -> dict:
        """
        Reduces the intersections' dict to non-empty roads
        :return: a dictionary of {non-empty road indexes: non-empty intersecting road indexes}
        """
        return dict((road, self.non_empty_roads(intersecting_roads)) for (road, intersecting_roads) in
                    self._intersections.items() if self.roads[road].vehicles and
                    self.non_empty_roads(intersecting_roads))

    def get_vehicles(self, roads=None) -> set:
        """
        :param roads: a list of road indexes, by default self.non_empty_roads()
        :return: a set of all the vehicles on the map
        """
        if not roads:
            roads = self.non_empty_roads()
        return set(chain.from_iterable([self.roads[road].vehicles for road in roads]))

    def detect_collisions(self) -> bool:
        """Detects collisions between roads in the intersections"""
        radius = 15
        for road, intersecting_roads in self.intersections.items():
            vehicles = self.roads[road].vehicles
            intersecting_vehicles = self.get_vehicles(intersecting_roads)
            for vehicle in vehicles:
                for intersecting_vehicle in intersecting_vehicles:
                    # for debugging purposes, remove after completion
                    if vehicle.crashed and intersecting_vehicle.crashed:
                        # ignore a previous crash
                        continue
                    detected = distance.euclidean(vehicle.position, intersecting_vehicle.position) < radius
                    if detected:
                        # for debugging purposes, remove after completion
                        vehicle.crashed = True
                        vehicle.color = (255, 0, 0)
                        intersecting_vehicle.crashed = True
                        intersecting_vehicle.color = (255, 0, 0)
                        return True
        return False

    def create_intersections(self, intersections_dict):
        self._intersections = self._intersections | intersections_dict

    def create_roads(self, roads):
        for start, end in roads:
            road = Road(start, end)
            self.roads.append(road)

    def create_gen(self, vehicle_rate, paths, ems=False):
        gen = VehicleGenerator(self, vehicle_rate, paths, ems)
        self.vehicle_generators.add(gen)

    def create_signal(self, roads, cycle, slow_distance, slow_factor, stop_distance):
        roads = [[self.roads[i] for i in road_group] for road_group in roads]
        sig = TrafficSignal(roads, cycle, slow_distance, slow_factor, stop_distance)
        self.traffic_signals.add(sig)

    def update(self):
        """
        Updates the simulation roads, generates vehicles, updates the traffic signals,
        updates varius vehicle statistics and increments the time
        """
        roads = self.non_empty_roads()

        # Update every road
        for i in roads:
            self.roads[i].update(self.dt, self.t)

        # Add vehicles
        for gen in self.vehicle_generators:
            self.vehicles_generated += gen.update(id=self.vehicles_generated)

        for signal in self.traffic_signals:
            signal.update(self)

        # Check roads for out of bounds vehicle
        for i in roads:
            road = self.roads[i]
            vehicle = road.vehicles[0]
            # If first vehicle is out of road bounds
            if vehicle.x >= road.length:
                # If vehicle has a next road
                if vehicle.current_road_index + 1 < len(vehicle.path):
                    # Update current road to next road
                    vehicle.current_road_index += 1
                    # Create a copy and reset some vehicle properties
                    new_vehicle = deepcopy(vehicle)
                    new_vehicle.x = 0
                    # Add it to the next road
                    next_road_index = vehicle.path[vehicle.current_road_index]
                    self.roads[next_road_index].vehicles.append(new_vehicle)
                    # Remove it from its road
                    road.vehicles.popleft()
                else:
                    # Remove it from its road
                    removed_vehicle = road.vehicles.popleft()
                    # Update stats
                    self.vehicles_on_map -= 1
                    self.vehicles_reached_destination += 1
                    self.journey_times.append(self.t - removed_vehicle.generation_time)
                    self.standing_times.append(removed_vehicle.total_standing_time)
                    self.average_journey_time = mean(self.journey_times)
                    self.average_wait_time = mean(self.standing_times)

        # Reset the counter
        self.vehicles_on_map = len(self.get_vehicles())

        # Increment time
        self.t += self.dt
        self.frame_count += 1
