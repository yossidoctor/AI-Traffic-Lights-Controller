from itertools import chain


class TrafficSignal:
    def __init__(self, roads, cycle, slow_distance, slow_factor, stop_distance):
        self.roads = roads
        self.roads_indexes = set(road.index for road in chain.from_iterable(roads))
        self.cycle = cycle
        self.current_cycle_index = 0
        self.slow_distance = slow_distance
        self.slow_factor = slow_factor
        self.stop_distance = stop_distance
        self.last_update_t = 0
        for i in range(len(self.roads)):
            for road in self.roads[i]:
                road.set_traffic_signal(self, i)

    @property
    def current_cycle(self):
        return self.cycle[self.current_cycle_index]

    def update(self):
        self.current_cycle_index = (self.current_cycle_index + 1) % len(self.cycle)
        # cycle_length = 30
        # k = (sim.t // cycle_length) % 2
        # self.current_cycle_index = int(k)
