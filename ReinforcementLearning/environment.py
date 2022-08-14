from TrafficSimulator import Window, two_way_intersection


class Environment:
    def __init__(self):
        self.max_gen = 30
        self.window = Window()
        # self.observation_space_size = 43776  # Yossi
        self.observation_space_size = 784  # Adi
        self.action_space = [0, 1]
        self._vehicles_to_pass = 0  # Vehicles on inbound roads

    def get_state(self, reset=False):
        # Adi's State:
        if reset:
            return tuple([self.window.sim.roads[0].traffic_signal_state, 0, 0, 0])
        # West, east inbound = [0, 2]
        # South, north inbound = [1, 3]
        west_east_signal_state = self.window.sim.roads[0].traffic_signal_state
        west_east_n_vehicles = sum(len(self.window.sim.roads[i].vehicles) for i in [0, 2])
        south_north_n_vehicles = sum(len(self.window.sim.roads[i].vehicles) for i in [1, 3])
        out_bound_vehicles = sum(len(self.window.sim.roads[i].vehicles) for i in [4, 5, 6, 7])
        # non_empty_junction = len(self.window.sim.intersections) != 0  # todo: validate,
        #  todo: comapre to Adi's indicator
        non_empty_junction = bool(self.window.sim.n_vehicles_on_map - out_bound_vehicles -
                                  west_east_n_vehicles - south_north_n_vehicles)
        state = [west_east_signal_state, west_east_n_vehicles, south_north_n_vehicles,
                 non_empty_junction]
        return tuple(state)

        # # Yossi's State
        # # Observation space:
        # # State = (vehicle, n_green_route_vehicles, n_red_route_vehicles)  # 171 * 16 * 16 = 43776
        # # vehicle: closest lead vehicle to a red traffic light
        # # n_{color}_route_vehicles: the number of vehicles on the route with {color} traffic light
        # # Vehicle = (vehicle.x, vehicle.v)  # n = 10 * 17 + 1 (for None) = 171
        # # vehicle.x: {0, 5, 10, ..., 45} (rounded down), vehicle.v: {1, 2, 3, ..., 17}
        # if reset:
        #     # return initial state
        #     return (None, None), 0, 0
        # n_green_route_vehicles = 0
        # n_red_route_vehicles = 0
        # red_light_lead_vehicles = []
        # for signal in self.window.sim.traffic_signals:
        #     for i in signal.roads_indexes:
        #         # a road with a traffic signal
        #         road = self.window.sim.roads[i]
        #         if road.traffic_signal_state:
        #             # green light road
        #             n_green_route_vehicles += len(road.vehicles)
        #         else:
        #             # red light road
        #             n_red_route_vehicles += len(road.vehicles)
        #             if road.vehicles:
        #                 # if the red light road isn't empty, get the lead vehicle
        #                 red_light_lead_vehicles.append(road.vehicles[0])
        # if not red_light_lead_vehicles:
        #     # roads with red light have no vehicles
        #     vehicle_stats = None, None
        # else:
        #     # get the lead vehicle closest to the traffic signal
        #     first_lead_vehicle = max(red_light_lead_vehicles, key=lambda vehicle: vehicle.x)
        #     x = 5 * (math.ceil(first_lead_vehicle.x / 5))
        #     v = math.ceil(first_lead_vehicle.v)
        #     vehicle_stats: Tuple = x, v
        # state = vehicle_stats, n_green_route_vehicles, n_red_route_vehicles
        # return state

    def step(self, step_action):
        self.window.run(step_action)

        new_state = self.get_state()

        step_reward = self.get_reward(new_state)

        # Set the number of vehicles on inbound roads in the new state
        self._vehicles_to_pass = new_state[1] + new_state[2]

        # Whether a terminal state (as defined under the MDP of the task) is reached.
        terminated = self.window.sim.completed

        # Whether a truncation condition outside the scope of the MDP is satisfied.
        # Ends the episode prematurely before a terminal state is reached.
        truncated = self.window.closed

        return new_state, step_reward, terminated, truncated

    def get_reward(self, state):
        # Adi's Reward
        # todo: validate non_empty_junction usage in reward or remove it
        west_east_signal_state, west_east_n_vehicles, south_north_n_vehicles, non_empty_junction = state
        # reward = step_action * non_empty_junction * -2
        # reward = self.window.sim.collision_detected * -100
        reward = self._vehicles_to_pass - (west_east_n_vehicles + south_north_n_vehicles)
        return reward

        # # Yossi's Reward
        # vehicle, n_green_route_vehicles, n_red_route_vehicles = state
        # collision_factor = -50 * self.window.sim.collision_detected  # high-weighted negative reward
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
        if not self.window.screen:
            self.window.init_screen()
        self.window.update_screen()

    def reset(self):
        self.window.sim = two_way_intersection(self.max_gen)
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
    #     for signal in self.window.sim.traffic_signals:
    #         for i in signal.roads_indexes:
    #             road = self.window.sim.roads[i]
    #             if not road.traffic_signal_state and road.vehicles and \
    #                     road.vehicles[0].x > safe_stop_zone:
    #                 new_road = deepcopy(road)
    #                 while len(new_road.vehicles) > 1:
    #                     new_road.vehicles.pop()
    #                 red_light_roads.append(new_road)
    #     if not red_light_roads:
    #         return False
    #     t, dt = self.window.sim.t, self.window.sim.dt  # Set local time variables
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
