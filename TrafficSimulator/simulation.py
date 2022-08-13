from copy import deepcopy
from statistics import mean
from typing import List, Dict, Tuple

from scipy.spatial import distance

from TrafficSimulator import Road, VehicleGenerator, TrafficSignal


class Simulation:
    def __init__(self, max_gen=None):
        self.t = 0.0  # Time keeping
        self.dt = 1 / 60  # Simulation time step
        self.roads: List[Road] = []  # Array to store roads
        self.generators: List[VehicleGenerator] = []
        self.traffic_signals: List[TrafficSignal] = []

        self._intersections: Dict[int, List[int]] = {}  # {Road index: List of all intersecting roads' indexes}
        self.collision_detected = False
        self._max_gen = max_gen  # Limits the amount of cars generated in a single simulation
        self.n_vehicles_generated = 0
        self.n_vehicles_on_map = 0
        self._waiting_time_log = []  # for vehicles that completed the journey

        # TODO comment
        self.vehicles_passed_junction = 0

    @property
    def completed(self) -> bool:
        """
        Whether a terminal state (as defined under the MDP of the task) is reached.
        """
        a = self.collision_detected
        b = self._max_gen and (self.n_vehicles_generated == self._max_gen) and (not self.n_vehicles_on_map)
        return a or b

    @property
    def non_empty_roads(self) -> List[Road]:
        return list(filter(lambda road: road.vehicles, self.roads))

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

    def get_passed_junction(self):
        """ TODO comment """
        return self.vehicles_passed_junction

    def detect_collisions(self) -> None:
        """Detects collisions between roads in the intersections"""
        radius = 2
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
        road = Road(start, end, index=len(self.roads))
        self.roads.append(road)
        return road

    def create_roads(self, roads: List[Tuple]):
        for road in roads:
            self.create_road(*road)

    def create_gen(self, vehicle_rate, paths: List[List]):
        inbound_roads: List[Road] = [self.roads[roads[0]] for weight, roads in paths]
        inbound_dict: Dict[int: Road] = {road.index: road for road in inbound_roads}
        gen = VehicleGenerator(vehicle_rate, paths, inbound_dict)
        self.generators.append(gen)
        return gen

    def create_signal(self, roads: List[List[int]], cycle, slow_distance, slow_factor, stop_distance):
        roads = [[self.roads[i] for i in road_group] for road_group in roads]
        sig = TrafficSignal(roads, cycle, slow_distance, slow_factor, stop_distance)
        self.traffic_signals.append(sig)
        return sig

    def update_signals(self):
        for signal in self.traffic_signals:
            signal.update()

    def update_vehicles(self):
        """ TODO comment """
        inter_list = self.intersections.keys()

        for road in self.non_empty_roads:
            # road = self.roads[road_index]
            if road.index in inter_list:
                for vehicle in road.vehicles:
                    if not vehicle.is_in_junction:
                        vehicle.is_in_junction = True
            else:
                for vehicle in road.vehicles:
                    if vehicle.is_in_junction:
                        self.vehicles_passed_junction += 1
                        vehicle.is_in_junction = False

    def update(self) -> None:
        """
        Updates the non-empty roads and the vehicle generators, check roads for out of bounds vehicle,
        detects collisions and increments time
        """
        # Update every road
        for road in self.non_empty_roads:
            road.update(self.dt, self.t)

        # Update every existing vehicle
        self.update_vehicles()

        # Add vehicles
        for gen in self.generators:
            if self._max_gen and self.n_vehicles_generated == self._max_gen:
                break
            generated = gen.update(self.t, self.n_vehicles_generated)
            self.n_vehicles_generated += generated
            self.n_vehicles_on_map += generated

        # Check roads for out of bounds vehicle
        for road in self.non_empty_roads:
            lead = road.vehicles[0]
            # If first vehicle is out of road bounds
            if lead.x >= road.length:
                # If vehicle has a next road
                if lead.current_road_index + 1 < len(lead.path):
                    # Update current road to next road
                    lead.current_road_index += 1
                    # Create a copy and reset some vehicle properties
                    new_vehicle = deepcopy(lead)
                    new_vehicle.x = 0
                    # Add it to the next road
                    next_road_index = lead.path[lead.current_road_index]
                    self.roads[next_road_index].vehicles.append(new_vehicle)
                    # Remove it from its road
                    road.vehicles.popleft()
                else:
                    # Remove it from its road
                    removed_vehicle = road.vehicles.popleft()
                    self.n_vehicles_on_map -= 1
                    # Update the log
                    self._waiting_time_log.append(removed_vehicle.get_total_waiting_time(self.t))

        self.detect_collisions()

        # Increment time
        self.t += self.dt
