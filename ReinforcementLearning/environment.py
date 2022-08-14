import math

from TrafficSimulator import Simulation, two_way_intersection


class EnvironmentOne:
    """ Observation space:
        State = (vehicle, n_green_route_vehicles, n_red_route_vehicles)  # 171 * 16 * 16 = 43776
        vehicle: closest lead vehicle to a red traffic light
        n_{color}_route_vehicles: the number of vehicles on the route with {color} traffic light
        Vehicle = (vehicle.x, vehicle.v)  # n = 10 * 17 + 1 (for None) = 171
        vehicle.x: {0, 5, 10, ..., 45} (rounded down), vehicle.v: {1, 2, 3, ..., 17}"""

    def __init__(self):
        self.max_gen: int = 30
        self.sim: Simulation = Simulation()
        self.observation_space_size: int = 43776
        self.action_space = [0, 1]
        self._vehicles_to_pass: int = 0  # Vehicles on inbound roads

    def get_state(self, reset=False):
        if reset:
            # return initial state
            return (None, None), 0, 0
        n_green_route_vehicles, n_red_route_vehicles = 0, 0
        red_light_lead_vehicles = []
        for signal in self.sim.traffic_signals:
            for i in signal.roads_indexes:
                road = self.sim.roads[i]
                # Green light
                if road.traffic_signal_state:
                    n_green_route_vehicles += len(road.vehicles)
                # Red light
                else:
                    n_red_route_vehicles += len(road.vehicles)
                    # if the red light road isn't empty, get the lead vehicle
                    if road.vehicles:
                        red_light_lead_vehicles.append(road.vehicles[0])
        if not red_light_lead_vehicles:
            # roads with red light have no vehicles
            vehicle_stats = None, None
        else:
            # get the lead vehicle closest to the traffic signal
            first_lead_vehicle = max(red_light_lead_vehicles, key=lambda vehicle: vehicle.x)
            # round stats
            vehicle_position = 5 * (math.ceil(first_lead_vehicle.x / 5))
            vehicle_velocity = math.ceil(first_lead_vehicle.v)
            vehicle_stats = vehicle_position, vehicle_velocity
        state = vehicle_stats, n_green_route_vehicles, n_red_route_vehicles
        return state

    def step(self, step_action):
        self.sim.run(step_action)

        new_state = self.get_state()

        step_reward = self.get_reward(new_state)

        # Set the number of vehicles on inbound roads in the new state
        self._vehicles_to_pass = new_state[1] + new_state[2]

        # Whether a terminal state (as defined under the MDP of the task) is reached.
        terminated = self.sim.completed

        # Whether a truncation condition outside the scope of the MDP is satisfied.
        # Ends the episode prematurely before a terminal state is reached.
        truncated = self.sim.gui_closed

        return new_state, step_reward, terminated, truncated

    def get_reward(self, state):
        vehicle, n_green_route_vehicles, n_red_route_vehicles = state
        collision_factor = -50 * self.sim.collision_detected  # high-weighted negative reward
        # high_risk_factor = -10 * int(self._lead_unable_to_brake())  # low-weighted negative reward

        # Check whether the flow change is positive or negative using the difference in the number
        # of vehicles in the inbound roads from the previous state - low-weighted positive reward
        flow_change = self._vehicles_to_pass - (n_green_route_vehicles + n_red_route_vehicles)

        # reward = collision_factor + high_risk_factor + flow_change
        reward = collision_factor + flow_change
        return reward

    def render(self):
        self.sim.init_gui()

    def reset(self):
        self.sim = two_way_intersection(self.max_gen)
        init_state = self.get_state(reset=True)
        self._vehicles_to_pass = 0
        return init_state

    # def _lead_unable_to_brake(self):
    #     # Create new copies of non-empty roads, each containing only its the first vehicle
    #     # (in case it's not in the safe_zone_stop)
    #     safe_stop_zone = 3
    #     red_light_roads = []
    #     # todo: bad implementation of getting roads with traffic signal
    #     #  get with traffic signal road groups
    #     for signal in self.sim.traffic_signals:
    #         for i in signal.roads_indexes:
    #             road = self.sim.roads[i]
    #             if not road.traffic_signal_state and road.vehicles and \
    #                     road.vehicles[0].x > safe_stop_zone:
    #                 new_road = deepcopy(road)
    #                 while len(new_road.vehicles) > 1:
    #                     new_road.vehicles.pop()
    #                 red_light_roads.append(new_road)
    #     if not red_light_roads:
    #         return False
    #     t, dt = self.sim.t, self.sim.dt  # Set local time variables
    #     # Simulate a single step
    #     for road in red_light_roads:
    #         init = road.vehicles[0].index, round(road.vehicles[0].x, 2), round(road.vehicles[0].v,
    #                                                                            2)
    #         for _ in range(180):
    #             road.update(dt, t)
    #             if road.vehicles[0].x > road.length:
    #                 print(init)
    #                 # Vehicle passed the traffic signal, meaning it can't brake successfully
    #                 return True
    #             t += dt
    #     return False


class EnvironmentTwo:
    def __init__(self):
        self.max_gen = 30
        self.sim = Simulation()
        self.observation_space_size = 784
        self.action_space = [0, 1]
        self._vehicles_to_pass = 0  # Vehicles on inbound roads

    def get_state(self, reset=False):
        """NOTE: THIS IS OPTIMIZED FOR A SINGLE-JUNCTION SETUP"""
        state = []  # signal state, n_route_1_vehicles, n_route_2_vehicles
        traffic_signal = self.sim.traffic_signals[0]
        if reset:
            return tuple([traffic_signal, 0, 0, 0])
        state.append(traffic_signal.current_cycle[0])  # Traffic signal state
        for route in traffic_signal.roads:
            state.append(sum(len(road.vehicles) for road in route))  # n_vehicles in each route
        out_bound_vehicles = sum(len(self.sim.roads[i].vehicles) for i in [4, 5, 6, 7])
        non_empty_junction = bool(self.sim.n_vehicles_on_map - out_bound_vehicles -
                                  state[1] - state[2])
        state.append(non_empty_junction)
        return tuple(state)

    def step(self, step_action):
        self.sim.run(step_action)

        new_state = self.get_state()

        step_reward = self.get_reward(new_state)

        # Set the number of vehicles on inbound roads in the new state
        self._vehicles_to_pass = new_state[1] + new_state[2]

        # Whether a terminal state (as defined under the MDP of the task) is reached.
        terminated = self.sim.completed

        # Whether a truncation condition outside the scope of the MDP is satisfied.
        # Ends the episode prematurely before a terminal state is reached.
        truncated = self.sim.gui_closed

        return new_state, step_reward, terminated, truncated

    def get_reward(self, state):
        # Adi's Reward
        # todo: validate non_empty_junction usage in reward or remove it
        west_east_signal_state, west_east_n_vehicles, south_north_n_vehicles, non_empty_junction = state
        # reward = step_action * non_empty_junction * -2
        # reward = self.sim.collision_detected * -100
        reward = self._vehicles_to_pass - (west_east_n_vehicles + south_north_n_vehicles)
        return reward

        # # Yossi's Reward
        # vehicle, n_green_route_vehicles, n_red_route_vehicles = state
        # collision_factor = -50 * self.sim.collision_detected  # high-weighted negative reward
        # # high_risk_factor = -10 * int(self._lead_unable_to_brake())  # low-weighted negative reward
        #
        # # Check whether the flow change is positive or negative using the difference in the number
        # # of vehicles in the inbound roads from the previous state - low-weighted positive reward
        # flow_change = self._vehicles_to_pass - (n_green_route_vehicles + n_red_route_vehicles)
        #
        # # reward = collision_factor + high_risk_factor + flow_change
        # reward = collision_factor + flow_change
        # return reward

    def render(self):
        self.sim.init_gui()

    def reset(self):
        self.sim = two_way_intersection(self.max_gen)
        init_state = self.get_state(reset=True)
        self._vehicles_to_pass = 0
        return init_state
