from TrafficSimulator import Window, two_way_intersection

MAX_GEN = 50  # limit the amount of cars generated in a single simulation


# def get_reward(state, step_action):
#     """A reward function based on pre-defined parameters"""
#     # west_east_signal_state, west_east_n_vehicles, south_north_n_vehicles,
#     # non_empty_junction, vehicles_unable_to_brake = state
#     west_east_signal_state, west_east_n_vehicles, south_north_n_vehicles, non_empty_junction = state
#
#     # Junction clearance factor
#     # reward = step_action * non_empty_junction * -150
#     reward = 10
#     reward -= step_action * non_empty_junction * -500
#
#     # Low efficiency switching action factor
#     if west_east_n_vehicles > south_north_n_vehicles:
#         if not west_east_signal_state:
#             # there's a red light for a route with more vehicles
#             reward -= 10
#     elif south_north_n_vehicles > west_east_n_vehicles:
#         if west_east_signal_state:
#             # there's a red light for a route with more vehicles
#             reward -= 10
#
#     # # Braking condition evaluation factor
#     # reward -= (1 * vehicles_unable_to_brake)
#     return reward


class Environment:
    def __init__(self):
        self.window = Window()
        self.action_space = [1, 0]  # Switch, or don't switch
        self.vehicles_to_pass = 0
        self.prev_step_wait_time = 0

    def step(self, step_action):
        self.window.run(step_action)

        new_state = self._get_state()

        step_reward = self.get_reward(new_state, step_action)

        # Whether a terminal state (as defined under the MDP of the task) is reached.
        terminated = self.window.sim.completed or self.window.sim.collision_detected

        # Whether a truncation condition outside the scope of the MDP is satisfied.
        # Ends the episode prematurely before a terminal state is reached.
        truncated = self.window.closed

        return new_state, step_reward, terminated, truncated

    # def get_reward(self, state, step_action):
    #     west_east_signal_state, west_east_n_vehicles, south_north_n_vehicles, non_empty_junction = state
    #
    #     # Junction clearance factor
    #     # reward = step_action * non_empty_junction * -250
    #     # reward = self.window.sim.collision_detected * -250
    #     reward = 0
    #     # Low efficiency switching action factor
    #     if west_east_n_vehicles > south_north_n_vehicles:
    #         if not west_east_signal_state:
    #             # there's a red light for a route with more vehicles
    #             reward -= 2 ** (west_east_n_vehicles - south_north_n_vehicles)
    #     elif south_north_n_vehicles > west_east_n_vehicles:
    #         if west_east_signal_state:
    #             # there's a red light for a route with more vehicles
    #             reward -= 2 ** (south_north_n_vehicles - west_east_n_vehicles)
    #     return reward

    # def get_reward(self, state, step_action):
    #     west_east_signal_state, west_east_n_vehicles, south_north_n_vehicles, non_empty_junction = state
    #     # reward = self.window.sim.collision_detected * -250
    #     roads = [self.window.sim.roads[i] for i in range(4)]
    #     sim_t = self.window.sim.t
    #     accumulated_waiting_time = sum(vehicle.get_waiting_time(sim_t) for road in roads for vehicle in road.vehicles)
    #     # cur_step_wait_time = accumulated_waiting_time - self.prev_step_wait_time
    #     # self.prev_step_wait_time = cur_step_wait_time
    #     # reward -= accumulated_waiting_time
    #     return - (accumulated_waiting_time ** 10)
    #     # reward = self.prev_step_wait_time - accumulated_waiting_time
    #     # self.prev_step_wait_time = accumulated_waiting_time - self.prev_step_wait_time
    #     # return reward

    def get_reward(self, state, step_action):
        west_east_signal_state, west_east_n_vehicles, south_north_n_vehicles, non_empty_junction = state
        # reward = step_action * non_empty_junction * -2
        # reward = self.window.sim.collision_detected * -100
        reward = self.vehicles_to_pass - (west_east_n_vehicles + south_north_n_vehicles)
        self.vehicles_to_pass = west_east_n_vehicles + south_north_n_vehicles  # todo: shouldn't happen here
        return reward

    def _get_state(self):
        # West, east inbound = [0, 2]
        # South, north inbound = [1, 3]
        west_east_signal_state = self.window.sim.roads[0].traffic_signal_state
        west_east_n_vehicles = sum(len(self.window.sim.roads[i].vehicles) for i in [0, 2])
        south_north_n_vehicles = sum(len(self.window.sim.roads[i].vehicles) for i in [1, 3])
        out_bound_vehicles = sum(len(self.window.sim.roads[i].vehicles) for i in [4, 5, 6, 7])
        # non_empty_junction = len(self.window.sim.intersections) != 0  # todo: doesn't work
        non_empty_junction = bool(
            self.window.sim.n_vehicles_on_map - out_bound_vehicles - west_east_n_vehicles - south_north_n_vehicles)

        # if west_east_signal_state:
        #     red_light_group = [1, 3]
        # else:
        #     red_light_group = [0, 2]
        # red_light_roads = [self.window.sim.roads[i] for i in red_light_group]
        # standing_vehicles = [vehicle for road in red_light_roads for vehicle in road.vehicles if vehicle.is_stopped]
        # waiting_times = [vehicle.get_waiting_time(self.window.sim.t) for vehicle in standing_vehicles]
        # average_wait_time = round(mean(waiting_times), 0) if waiting_times else 0

        # vehicles_unable_to_brake = self._evaluate_breaking_conditions()
        # state = [west_east_signal_state, west_east_n_vehicles, south_north_n_vehicles,
        # non_empty_junction, vehicles_unable_to_brake]
        state = [west_east_signal_state, west_east_n_vehicles, south_north_n_vehicles, non_empty_junction]
        return tuple(state)

    # def _evaluate_breaking_conditions(self):
    #     """ The function simulates changing the green lights to red and checks whether the first vehicles
    #     will be able to safely brake"""
    #     # Get the roads with the green lights
    #     west_east_signal_state = self.window.sim.roads[0].traffic_signal_state
    #     if west_east_signal_state:
    #         green_light_group = [0, 2]
    #     else:
    #         green_light_group = [1, 3]
    #     # Create new copies of non-empty roads, each containing only its the first vehicle
    #     green_light_roads = [deepcopy(self.window.sim.roads[i]) for i in green_light_group if
    #                          self.window.sim.roads[i].vehicles]
    #     if not green_light_roads:
    #         return 0
    #     for road in green_light_roads:
    #         road.traffic_signal.update()  # Change the lights to red
    #         road.vehicles = [road.vehicles[0]]  # Keep only the first vehicle
    #     t, dt = self.window.sim.t, self.window.sim.dt  # Set local time variables
    #     # Run the simulation
    #     for _ in range(100):
    #         for road in green_light_roads:
    #             road.update(dt, t)
    #         t += dt
    #     for road in green_light_roads:
    #         if road.vehicles[0].x > road.length:
    #             # Vehicle passed the traffic signal, meaning it didn't brake successfully
    #             return True
    #     return False

    def render(self):
        if not self.window.screen:
            self.window.init_display()

    def reset(self):
        self.window.sim = two_way_intersection(MAX_GEN)
        init_state = self._get_state()
        return init_state
