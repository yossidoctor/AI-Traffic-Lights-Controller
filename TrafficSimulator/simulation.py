from copy import deepcopy
from itertools import chain
from statistics import mean

from .road import Road, distance
from .traffic_signal import TrafficSignal
from .vehicle_generator import VehicleGenerator


class Simulation:
    def __init__(self, generation_limit=None):
        self.t = 0.0  # Time keeping
        self.dt = 1 / 60  # Simulation time step
        self.generation_limit = generation_limit

        # Lists of objects
        self.roads = []
        self.vehicle_generators = []
        self.traffic_signals = []

        self._intersections = {}  # {Road index: List of all intersecting roads' indexes}

        # Simulation stats
        self.completed = False
        self.collision_detected = False  # True is a terminal state (as defined under the MDP of the task)
        self.collisions = 0
        self.n_vehicles_generated = 0
        self.n_vehicles_on_map = 0  # 0 is a terminal state (as defined under the MDP of the task)
        self.standing_times_log = []
        self.standing_ems_times_log = []
        self.average_wait_time = 0
        self.average_ems_wait_time = 0
        self.passed_green_signal = 0

    def non_empty_roads(self, roads=None):
        """
        :param roads: A list of indexes (of roads), by default range(len(self.roads))
        :return: A list of indexes (of non-empty roads)
        """
        if not roads:
            roads = range(len(self.roads))
        return list(filter(lambda road: self.roads[road].vehicles, roads))

    @property
    def intersections(self):
        """
        Reduces the intersections' dict to non-empty roads
        :return: a dictionary of {non-empty road indexes: non-empty intersecting road indexes}
        """
        return dict((road, self.non_empty_roads(intersecting_roads)) for (road, intersecting_roads) in
                    self._intersections.items() if self.roads[road].vehicles and
                    self.non_empty_roads(intersecting_roads))

    def get_vehicles(self, roads=None):
        """
        :param roads: A list of indexes (of roads), by default self.non_empty_roads()
        :return: A list of vehicles
        """
        if not roads:
            roads = self.non_empty_roads()
        vehicles = list(chain.from_iterable([self.roads[road].vehicles for road in roads]))
        return list(filter(lambda vehicle: vehicle.is_on_map, vehicles))

    def detect_collisions(self) -> None:
        """Detects collisions between roads in the intersections"""
        radius = 15
        if self.n_vehicles_on_map > 1:
            for road, intersecting_roads in self.intersections.items():
                vehicles = self.roads[road].vehicles
                intersecting_vehicles = self.get_vehicles(intersecting_roads)
                for vehicle in vehicles:
                    for intersecting_vehicle in intersecting_vehicles:
                        if distance.euclidean(vehicle.position, intersecting_vehicle.position) < radius:
                            # for debugging purposes, todo: remove after completion
                            vehicle.color = (255, 0, 0)
                            intersecting_vehicle.color = (255, 0, 0)
                            self.collision_detected = True
                            self.collisions += 1
                            return

    def create_intersections(self, intersections_dict):
        self._intersections = self._intersections | intersections_dict

    def create_roads(self, roads):
        for start, end in roads:
            road = Road(start, end)
            self.roads.append(road)

    def create_gen(self, vehicle_rate, paths_dict, ems=False):
        gen = VehicleGenerator(self, vehicle_rate, paths_dict, ems)
        self.vehicle_generators.append(gen)

    def create_signal(self, road_groups, cycle, slow_distance, slow_factor, stop_distance):
        roads = [[self.roads[i] for i in road_group] for road_group in road_groups]
        sig = TrafficSignal(road_groups, roads, cycle, slow_distance, slow_factor, stop_distance)
        self.traffic_signals.append(sig)

    def update_signals(self):
        self.traffic_signals[0].update()

    # def update_signals(self, actions_list):
    # for i, signal in enumerate(self.traffic_signals):
    #     if actions_list[i]:
    #         signal.update(self.t)

    def update(self):
        """
        Updates the simulation roads, generates vehicles, updates the traffic signals,
        updates varius vehicle statistics and increments the time
        """
        roads = self.non_empty_roads()

        # Update every road
        for i in roads:
            self.roads[i].update(self.dt, self.t)

        group = []
        signal = self.traffic_signals[0]
        if signal.current_cycle[1]:  # (True, False) [0,2] [1, 3]
            group = [1, 3]
        else:
            group = [0, 2]

        # Add vehicles
        for gen in self.vehicle_generators:
            if self.generation_limit and self.n_vehicles_generated == self.generation_limit:
                break
            generated = gen.update()
            self.n_vehicles_generated += generated
            self.n_vehicles_on_map += generated

        # Check roads for out of bounds vehicle
        for i in roads:
            road = self.roads[i]
            vehicle = road.vehicles[0]
            # If first vehicle is out of road bounds
            if vehicle.x >= road.length:
                # If vehicle has a next road
                if vehicle.current_road_index + 1 < len(vehicle.path):
                    if i in group:
                        self.passed_green_signal += 1
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
                    if removed_vehicle.is_ems:
                        self.standing_ems_times_log.append(removed_vehicle.total_standing_t)
                    else:
                        self.standing_times_log.append(removed_vehicle.total_standing_t)

        self.calculate_average_waiting_time()

        self.completed = self.n_vehicles_generated == self.generation_limit and not self.n_vehicles_on_map

        # Increment time
        self.t += self.dt

    def calculate_average_waiting_time(self):
        vehicles = self.get_vehicles()
        current_standing_times = []
        current_ems_standing_times = []
        for vehicle in vehicles:
            if vehicle.is_stopped:
                if vehicle.is_ems:
                    current_ems_standing_times.append(self.t - vehicle.last_stop_t)
                else:
                    current_standing_times.append(self.t - vehicle.last_stop_t)
            else:
                if vehicle.is_ems:
                    current_ems_standing_times.append(vehicle.total_standing_t)
                else:
                    current_standing_times.append(vehicle.total_standing_t)
        if self.standing_times_log or current_standing_times:
            self.average_wait_time = mean(self.standing_times_log + current_standing_times)
        if self.standing_ems_times_log or current_ems_standing_times:
            self.average_ems_wait_time = mean(self.standing_ems_times_log + current_ems_standing_times)
