from copy import deepcopy
from statistics import mean
from typing import List, Dict

from scipy.spatial import distance

from TrafficSimulator import Road, VehicleGenerator, TrafficSignal


class Simulation:
    def __init__(self, max_gen=0):
        self.t = 0.0  # Time keeping
        self.frame_count = 0  # Frame count keeping
        self.dt = 1 / 60  # Simulation time step
        self.roads: List[Road] = []  # Array to store roads
        self.generators: List[VehicleGenerator] = []
        self.traffic_signals: List[TrafficSignal] = []

        self._intersections: Dict[int, List[int]] = {}  # {Road index: List of all intersecting roads' indexes}
        self.collision_detected = False
        self.max_gen = max_gen  # Limits the amount of cars generated in a single simulation
        self.n_vehicles_generated = 0
        self.n_vehicles_on_map = 0
        self.completed = False
        self._waiting_time_log = []  # Of vehicles that completed the journey

    @property
    def intersections(self) -> Dict[int, List[int]]:
        """
        Reduces the intersections' dict to non-empty roads
        :return: a dictionary of {non-empty road indexes: non-empty intersecting road indexes}
        """
        output: Dict[int, List[int]] = {}
        for road_index, intersecting_indexes in self._intersections.items():
            if self.roads[road_index].vehicles:
                intersecting_indexes = [i for i in intersecting_indexes if self.roads[i].vehicles]
                if intersecting_indexes:
                    output[road_index] = intersecting_indexes
        return output

    def get_average_wait_time(self):
        """Returns the average wait time of the vehicles that completed their journey and were removed from the map"""
        if not self._waiting_time_log:
            return 0
        return mean(self._waiting_time_log)

    def detect_collisions(self) -> None:
        """Detects collisions between roads in the intersections"""
        radius = 15
        for i, intersecting_indexes in self.intersections.items():
            vehicles = self.roads[i].vehicles
            intersecting_vehicles = []
            for j in intersecting_indexes:
                intersecting_vehicles += [vehicle for vehicle in self.roads[j].vehicles]
            for vehicle in vehicles:
                for intersecting_vehicle in intersecting_vehicles:
                    if distance.euclidean(vehicle.position, intersecting_vehicle.position) < radius:
                        self.collision_detected = True
                        return

    def create_intersections(self, intersections_dict):
        self._intersections = self._intersections | intersections_dict

    def create_road(self, start, end):
        road = Road(start, end)
        self.roads.append(road)
        return road

    def create_roads(self, road_list):
        for road in road_list:
            self.create_road(*road)

    def create_gen(self, vehicle_rate, paths_dict):
        gen = VehicleGenerator(self, vehicle_rate, paths_dict)
        self.generators.append(gen)
        return gen

    def create_signal(self, roads, cycle, slow_distance, slow_factor, stop_distance):
        roads = [[self.roads[i] for i in road_group] for road_group in roads]
        sig = TrafficSignal(roads, cycle, slow_distance, slow_factor, stop_distance)
        self.traffic_signals.append(sig)
        return sig

    def update_signals(self):
        for signal in self.traffic_signals:
            signal.update()

    def update(self):
        # Update every road
        for road in self.roads:
            road.update(self.dt, self.t)

        # Add vehicles
        for gen in self.generators:
            if 0 < self.n_vehicles_generated == self.max_gen:
                break
            generated = gen.update()
            self.n_vehicles_generated += generated
            self.n_vehicles_on_map += generated

        # Check roads for out of bounds vehicle
        for road in self.roads:
            # If road has no vehicles, continue
            if len(road.vehicles) == 0:
                continue
            # If not
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
                    self.n_vehicles_on_map -= 1
                    # Update the log
                    self._waiting_time_log.append(removed_vehicle.get_waiting_time(self.t))

        # Increment time
        self.t += self.dt
        self.frame_count += 1

        self.completed = (self.n_vehicles_generated == self.max_gen) and (not self.n_vehicles_on_map)
