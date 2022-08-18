from TrafficSimulator import Simulation
from TrafficSimulator.curve import turn_road, TURN_RIGHT, TURN_LEFT

n = 15  # Curve resolution
a = 2  # Short offset from (0, 0)
b = 12  # Long offset from (0, 0)
length = 50  # Road length
offset = 25  # Intersection offset from the center

# Nodes
WEST_RIGHT_START = (-b - length, a)
WEST_LEFT_START = (-b - length, -a)

SOUTH_RIGHT_START = (a, b + length)
SOUTH_LEFT_START = (-a, b + length)

EAST_RIGHT_START = (b + length, -a)
EAST_LEFT_START = (b + length, a)

NORTH_RIGHT_START = (-a, -b - length)
NORTH_LEFT_START = (a, -b - length)

WEST_RIGHT = (-b, a)
WEST_LEFT = (-b, -a)

SOUTH_RIGHT = (a, b)
SOUTH_LEFT = (-a, b)

EAST_RIGHT = (b, -a)
EAST_LEFT = (b, a)

NORTH_RIGHT = (-a, -b)
NORTH_LEFT = (a, -b)

# Roads
WEST_INBOUND = (WEST_RIGHT_START, WEST_RIGHT)
SOUTH_INBOUND = (SOUTH_RIGHT_START, SOUTH_RIGHT)
EAST_INBOUND = (EAST_RIGHT_START, EAST_RIGHT)
NORTH_INBOUND = (NORTH_RIGHT_START, NORTH_RIGHT)

WEST_OUTBOUND = (WEST_LEFT, WEST_LEFT_START)
SOUTH_OUTBOUND = (SOUTH_LEFT, SOUTH_LEFT_START)
EAST_OUTBOUND = (EAST_LEFT, EAST_LEFT_START)
NORTH_OUTBOUND = (NORTH_LEFT, NORTH_LEFT_START)

WEST_STRAIGHT = (WEST_RIGHT, EAST_LEFT)
SOUTH_STRAIGHT = (SOUTH_RIGHT, NORTH_LEFT)
EAST_STRAIGHT = (EAST_RIGHT, WEST_LEFT)
NORTH_STRAIGHT = (NORTH_RIGHT, SOUTH_LEFT)

WEST_RIGHT_TURN = turn_road(WEST_RIGHT, SOUTH_LEFT, TURN_RIGHT, n)
WEST_LEFT_TURN = turn_road(WEST_RIGHT, NORTH_LEFT, TURN_LEFT, n)

SOUTH_RIGHT_TURN = turn_road(SOUTH_RIGHT, EAST_LEFT, TURN_RIGHT, n)
SOUTH_LEFT_TURN = turn_road(SOUTH_RIGHT, WEST_LEFT, TURN_LEFT, n)

EAST_RIGHT_TURN = turn_road(EAST_RIGHT, NORTH_LEFT, TURN_RIGHT, n)
EAST_LEFT_TURN = turn_road(EAST_RIGHT, SOUTH_LEFT, TURN_LEFT, n)

NORTH_RIGHT_TURN = turn_road(NORTH_RIGHT, WEST_LEFT, TURN_RIGHT, n)
NORTH_LEFT_TURN = turn_road(NORTH_RIGHT, EAST_LEFT, TURN_LEFT, n)

ROADS = [
    WEST_INBOUND,  # 0
    SOUTH_INBOUND,  # 1
    EAST_INBOUND,  # 2
    NORTH_INBOUND,  # 3

    WEST_OUTBOUND,  # 4
    SOUTH_OUTBOUND,  # 5
    EAST_OUTBOUND,  # 6
    NORTH_OUTBOUND,  # 7

    WEST_STRAIGHT,  # 8
    SOUTH_STRAIGHT,  # 9
    EAST_STRAIGHT,  # 10
    NORTH_STRAIGHT,  # 11

    *WEST_RIGHT_TURN,
    *WEST_LEFT_TURN,

    *SOUTH_RIGHT_TURN,
    *SOUTH_LEFT_TURN,

    *EAST_RIGHT_TURN,
    *EAST_LEFT_TURN,

    *NORTH_RIGHT_TURN,
    *NORTH_LEFT_TURN
]


def turn(t): return range(t, t + n)


# {FROM} {TURN DIRECTION} {TO}
t12 = turn(12)  # W_R_S
t27 = turn(27)  # W_L_N
t42 = turn(42)  # S_R_E
t57 = turn(57)  # S_L_W
t72 = turn(72)  # E_R_N
t87 = turn(87)  # E_L_S
t102 = turn(102)  # N_R_W
t117 = turn(117)  # N_L_E

# Vehicle generator
VEHICLE_RATE = 35
PATHS = [
    [3, [0, 8, 6]],  # WEST STRAIGHT EAST
    [1, [0, *t12, 5]],  # WEST RIGHT SOUTH
    # [1, [0, *t27, 7]],  # WEST LEFT NORTH

    [3, [1, 9, 7]],  # SOUTH STRAIGHT NORTH
    [1, [1, *t42, 6]],  # SOUTH RIGHT EAST
    # [1, [1, *t57, 4]],  # SOUTH LEFT WEST

    [3, [2, 10, 4]],  # EAST STRAIGHT WEST
    [1, [2, *t72, 7]],  # EAST RIGHT NORTH
    # [1, [2, *t87, 5]],  # EAST LEFT SOUTH

    [3, [3, 11, 5]],  # NORTH STRAIGHT SOUTH
    [1, [3, *t102, 4]],  # NORTH RIGHT WEST
    # [1, [3, *t117, 6]]  # NORTH LEFT EAST
]

# Intersections {main_road: intersecting_roads}
d1 = {8: {9, 11, *t42, *t57, *t87, *t117}}
d2 = {9: {10, *t12, *t27, *t72, *t87, *t117}}
d3 = {10: {11, *t27, *t57, *t102, *t117}}
d4 = {11: {*t12, *t27, *t57, *t87}}
d5 = {road: {*t87} for road in t12}
d6 = {road: {*t57, *t72, *t117} for road in t27}
d7 = {road: {*t117} for road in t42}
d8 = {road: {*t87, *t102} for road in t57}
d9 = {road: {*t117} for road in t87}

INTERSECTIONS_DICT = {
    **d1,
    **d2,
    **d3,
    **d4,
    **d5,
    **d6,
    **d7,
    **d8,
    **d9
}

# Signals
SIGNAL_ROADS = [[0, 2], [1, 3]]  # WEST, EAST, SOUTH NORTH
CYCLE = [(False, True), (False, False), (True, False), (False, False)]
SLOW_DISTANCE = 50
SLOW_FACTOR = 0.4
STOP_DISTANCE = 15


def two_way_intersection_setup(max_gen=None):
    sim = Simulation(max_gen)
    sim.add_roads(ROADS)
    sim.add_generator(VEHICLE_RATE, PATHS)
    sim.add_traffic_signal(SIGNAL_ROADS, CYCLE, SLOW_DISTANCE, SLOW_FACTOR, STOP_DISTANCE)
    sim.add_intersections(INTERSECTIONS_DICT)
    return sim
