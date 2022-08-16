from itertools import chain
from typing import List, Tuple, Set

from TrafficSimulator.road import Road


class TrafficSignal:
    def __init__(self, roads: List[List[Road]], cycle: List[Tuple],
                 slow_distance: float, slow_factor: float, stop_distance: float):
        self.roads: List[List[Road]] = roads
        self.roads_indexes: Set[int] = set(road.index for road in chain.from_iterable(roads))
        self.cycle: List[Tuple[bool]] = cycle
        self.current_cycle_index = 0
        self.slow_distance: float = slow_distance
        self.slow_factor: float = slow_factor
        self.stop_distance: float = stop_distance
        self.prev_update_time: float = 0
        for i in range(len(self.roads)):
            for road in self.roads[i]:
                road.set_traffic_signal(self, i)

    @property
    def current_cycle(self) -> Tuple:
        return self.cycle[self.current_cycle_index]

    def update(self):
        self.current_cycle_index = (self.current_cycle_index + 1) % len(self.cycle)
