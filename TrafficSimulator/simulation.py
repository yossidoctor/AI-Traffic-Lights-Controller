from copy import deepcopy
# import itertools
from itertools import product, chain
from statistics import mean
from typing import List, Dict, Tuple, Set, FrozenSet

from TrafficSimulator import Road, VehicleGenerator, TrafficSignal


class Simulation:
    def __init__(self, max_gen=None):
        self.t = 0.0  # Time keeping
        self.dt = 1 / 60  # Simulation time step
        self.roads: List[Road] = []  # Array to store roads
        self.generators: List[VehicleGenerator] = []
        self.traffic_signals: List[TrafficSignal] = []
        self.non_empty_roads: Set[int] = set()

        self._intersections: Dict[int, Set[int]] = {}  # {Road index: List of all intersecting roads' indexes}
        self.collision_detected = False
        self._max_gen = max_gen  # Limits the amount of cars generated in a single simulation
        self.n_vehicles_generated = 0
        self.n_vehicles_on_map = 0
        self._waiting_time_log = []  # for vehicles that completed the journey

    @property
    def completed(self) -> bool:
        """
        Whether a terminal state (as defined under the MDP of the task) is reached.
        """
        a = self.collision_detected
        b = self._max_gen and (self.n_vehicles_generated == self._max_gen) and (not self.n_vehicles_on_map)
        return a or b

    @property
    def intersections(self) -> Dict[int, Set[int]]:
        """
        Reduces the intersections' dict to non-empty roads
        :return: a dictionary of {non-empty road index: [non-empty intersecting roads indexes]}
        """
        output: Dict[int, Set[int]] = {k, v.intersection(non_empty_roads) for k, v in self._intersections.items() if k in non_empty_roads and v.intersection(non_empty_roads)}
        return output

    def get_average_wait_time(self):
        """Returns the average wait time of the vehicles that completed their journey and were removed from the map"""
        if not self._waiting_time_log:
            return 0
        return mean(self._waiting_time_log)

    def detect_collisions(self) -> None:
        """Detects collisions between roads in the intersections"""
        radius = 3
        # Transform the intersections' dict of non empty-roads to {vehicles: [all possibly intersecting vehicles]}
        intersections: Dict[FrozenSet[Vehicle], Set[Vehicle]] = {frozenset(self.roads[k].vehicles), set(chain.from_iterable([self.sim.roads[r].vehicles for r in v])) for k, v in self._intersections.items()}
        # Generate all combinations of possibly collided vehicles
        possibly_collided_vehicles = chain.from_iterable(product(vehicles, intersecting_vehicles) for vehicles, intersecting_vehicles in intersections.items()))
        collision_detected = (distance.euclidean(a.position, b.position) < radius for a, b in possibly_collided_vehicles)
        if any(collision_detected):
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

    def update(self) -> None:
        """
        Updates the non-empty roads and the vehicle generators, check roads for out of bounds vehicle,
        detects collisions and increments time
        """
        # Update every road
        for i in self.non_empty_roads:
            self.roads[i].update(self.dt, self.t)

        # Add vehicles
        for gen in self.generators:
            if self._max_gen and self.n_vehicles_generated == self._max_gen:
                break
            road_index = gen.update(self.t, self.n_vehicles_generated)
            if road_index is not None:
                self.n_vehicles_generated += 1
                self.n_vehicles_on_map += 1
                self.non_empty_roads.add(road_index)

        # Check roads for out of bounds vehicle
        new_roads = set()
        empty_roads = set()
        for i in self.non_empty_roads:
            road = self.roads[i]
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
                    new_roads.add(next_road_index)
                    self.roads[next_road_index].vehicles.append(new_vehicle)
                    # Remove it from its road
                    road.vehicles.popleft()
                    if not road.vehicles:
                        empty_roads.add(road.index)
                else:
                    # Remove it from its road
                    removed_vehicle = road.vehicles.popleft()
                    if not road.vehicles:
                        empty_roads.add(road.index)
                    self.n_vehicles_on_map -= 1
                    # Update the log
                    wait_time = removed_vehicle.get_total_waiting_time(self.t)
                    self._waiting_time_log.append(wait_time)

        self.non_empty_roads -= empty_roads
        self.non_empty_roads |= new_roads
        self.detect_collisions()

        # Increment time
        self.t += self.dt
