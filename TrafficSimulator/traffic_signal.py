class TrafficSignal:
    def __init__(self, road_groups, roads, cycle, slow_distance, slow_factor, stop_distance):
        self.road_groups = road_groups
        self.roads = roads
        self.cycle = cycle
        self.slow_distance = slow_distance
        self.slow_factor = slow_factor
        self.stop_distance = stop_distance
        self.current_cycle_index = 0
        self.last_update_t = 0

        for i, roads in enumerate(self.roads):
            for road in roads:
                road.set_traffic_signal(self, i)

    @property
    def current_cycle(self):
        return self.cycle[self.current_cycle_index]

    def update(self, t):
        if self.current_cycle_index:
            self.current_cycle_index = 0
        else:
            self.current_cycle_index = 1
