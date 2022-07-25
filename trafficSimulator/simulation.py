from copy import deepcopy

from .road import Road
from .traffic_signal import TrafficSignal
from .vehicle_generator import VehicleGenerator


class Simulation:
    def __init__(self):
        self.t = 0.0  # Time keeping
        self.dt = 1 / 60  # Simulation time step
        self.frame_count = 0  # Frame time keeping
        self.roads = []
        self.vehicle_generators = []
        self.traffic_signals = []

        self.intersections_dict = {}

        self.vehicles_generated = 0
        self.vehicles_on_map = 0
        self.vehicles_reached_destination = 0

        self.journey_times = []
        self.standing_times = []
        self.average_wait_time = 0
        self.average_journey_time = 0

    def create_intersections(self, intersections_dict):
        self.intersections_dict = intersections_dict

    # def create_road(self, start, end):
    #     road = Road(start, end)
    #     self.roads.append(road)

    def create_roads(self, roads):
        for start, end in roads:
            road = Road(start, end)
            self.roads.append(road)

    def create_gen(self, vehicle_rate, paths, ems=False):
        gen = VehicleGenerator(self, vehicle_rate, paths, ems)
        self.vehicle_generators.append(gen)

    def create_signal(self, roads, cycle, slow_distance, slow_factor, stop_distance):
        roads = [[self.roads[i] for i in road_group] for road_group in roads]
        sig = TrafficSignal(roads, cycle, slow_distance, slow_factor, stop_distance)
        self.traffic_signals.append(sig)

    def update(self):
        """
        Updates the simulation roads, generates vehicles, updates the traffic signals,
        updates varius vehicle statistics and increments the time
        """
        # Update every road
        for road in self.roads:
            road.update(self.dt, self.t)

        # Add vehicles
        for gen in self.vehicle_generators:
            self.vehicles_generated += gen.update()

        for signal in self.traffic_signals:
            signal.update(self)

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
                    # Update stats
                    self.vehicles_on_map -= 1
                    self.vehicles_reached_destination += 1
                    self.journey_times.append(self.t - removed_vehicle.generation_time)
                    self.standing_times.append(removed_vehicle.total_standing_time)
                    self.average_journey_time = sum(self.journey_times) / len(self.journey_times)
                    self.average_wait_time = sum(self.standing_times) / len(self.standing_times)

        # Reset the counter
        self.vehicles_on_map = sum(len(road.vehicles) for road in self.roads)

        # Increment time
        self.t += self.dt
        self.frame_count += 1
