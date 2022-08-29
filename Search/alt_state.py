import copy
import random
from typing import Set, Dict, Optional

import numpy

from TrafficSimulator import Simulation
from TrafficSimulator.Setups.two_way_intersection import *


class Gstate:
    def __init__(self, sim: Simulation, max_c):
        """
        Constructor of a state, recives a running simulation and amount of
        action cycles (The solution length in Genetics)
        """
        self.act_cycle = 0
        self.max_c = max_c
        self.score = 0
        self.my_sim = Simulation(sim.max_gen)
        self.my_sim.n_vehicles_generated = sim.n_vehicles_generated
        self.my_sim.n_vehicles_on_map = sim.n_vehicles_on_map
        self.my_sim._inbound_roads = sim.inbound_roads
        self.my_sim._outbound_roads = sim.outbound_roads
        self.my_sim._non_empty_roads = copy.deepcopy(sim.non_empty_roads)
        self.my_sim.max_gen = sim.max_gen
        self.my_sim.collision_detected = sim.collision_detected
        self.my_sim._waiting_times_sum = sim._waiting_times_sum
        self.copy_elems(sim)
        self.v_location_before = dict()
        self.v_location_after = dict()
        self.penalty = 1
        self.green = []
        self.red = []
        self.passed_for_roads = dict()

    def copy_elems(self, sim):
        """
        Helper function for the constructor to help copy certain attributes
        from the running simulation
        """
        self.my_sim.roads = copy.deepcopy(sim.roads)
        self.my_sim.add_generator(VEHICLE_RATE, PATHS)
        self.my_sim.traffic_signals = [self.my_sim.roads[0].traffic_signal]
        self.my_sim.add_intersections(INTERSECTIONS_DICT)

    def min_optimal_score(self):
        """
        calculates a minimum score a valid solution should achieve with the
        given state
        """
        group_a = 0
        group_b = 0
        for i in self.my_sim.inbound_roads:
            if self.my_sim.roads[i].traffic_signal_state is True:
                group_a += len(self.my_sim.roads[i].vehicles) * self.max_c
            else:
                group_b += len(self.my_sim.roads[i].vehicles) * self.max_c

        res = (0.2 * (max(group_b, group_a)) / 2) + \
              (0.3 * (max(group_b, group_a)) / 3)

        if (group_a + group_b) / 5 < 10:
            return res
        res = res * 9 / 10
        return res

    def before_act(self):
        """
        checks which vehicles are at the inbound roads before committing an
        action
        """
        for ri in self.my_sim.inbound_roads:
            self.v_location_before[ri] = []
            for v in self.my_sim.roads[ri].vehicles:
                self.v_location_before[ri].append(v.index)

    def after_act(self):
        """
        checks which vehicles are at the inbound roads after committing an
        action, as well as checking which inbound roads have a green light
        or red light
        """
        for ri in self.my_sim.inbound_roads:
            self.v_location_after[ri] = []
            for v in self.my_sim.roads[ri].vehicles:
                self.v_location_after[ri].append(v.index)
            if self.my_sim.roads[ri].traffic_signal_state is True:
                self.green.append(ri)
            else:
                self.red.append(ri)

    def passed(self):
        """
        calculate for each inbound road how many vehicles have started to
        cross the junction
        """
        for ri in self.my_sim.inbound_roads:
            self.passed_for_roads[ri] = 0
            for vi in self.v_location_before[ri]:
                if vi not in self.v_location_after[ri]:
                    self.passed_for_roads[ri] += 1

    def calc_helper1(self):
        """
        calculates total sums of cars per the roads that were in green/red
        light before and after committing the action,
        in case the action was to switch lights
        """
        red_side = 0
        for i in self.my_sim.inbound_roads:
            if i in self.red:
                red_side += len(self.v_location_after[i])
        green_side = 0
        for j in self.my_sim.inbound_roads:
            if j in self.green:
                green_side += len(self.v_location_after[j])
        red_side_b = 0
        for i in self.my_sim.inbound_roads:
            if i in self.green:
                red_side_b += len(self.v_location_before[i])
        green_side_b = 0
        for j in self.my_sim.inbound_roads:
            if j in self.red:
                green_side_b += len(self.v_location_before[j])
        return red_side, green_side, red_side_b, green_side_b

    def calc_helper2(self):
        """
         calculates total sums of cars per the roads that were in green/red
        light before and after committing the action,
         in case the action was not to switch lights
        """
        red_side = 0
        for i in self.my_sim.inbound_roads:
            if i in self.red:
                red_side += len(self.v_location_after[i])
        green_side = 0
        for j in self.my_sim.inbound_roads:
            if j in self.green:
                green_side += len(self.v_location_after[j])
        red_side_b = 0
        for i in self.my_sim.inbound_roads:
            if i in self.red:
                red_side_b += len(self.v_location_before[i])
        green_side_b = 0
        for j in self.my_sim.inbound_roads:
            if j in self.green:
                green_side_b += len(self.v_location_before[j])
        return red_side, green_side, red_side_b, green_side_b

    def reward_switch(self, action):
        """
        The function measures how should we add to the total score and set
        the penalties. we add to the score the weighted amount of vehicles
        who started to cross the junction, it is weighted by the ratio of
        the max action cycle to the current action cycle, in addition for
        every right choice the score is awarded by the same ratio, and for
        every wrong action the penalty multiplier is multiplied by 0.9
        """
        if action == 1:
            # We need to calculate how much passed now
            # we need to determine that it was good to switch the lights
            # if it was bad decision we need to penalize it
            for ri in self.my_sim.inbound_roads:
                self.score += ((self.max_c / self.act_cycle) *
                               self.passed_for_roads[ri])
            red_side, green_side, red_side_b, green_side_b = self.calc_helper1()
            if (green_side < red_side or green_side_b == 0) and red_side > 0:
                self.penalty *= 9 / 10
            else:
                self.score += self.max_c / self.act_cycle

        else:
            # We need to calculate how much has passed where it is green
            # We need to determine that it was good to not switch the lights
            # if it was bad decision we need to penalize it
            for ri in self.my_sim.inbound_roads:
                if ri in self.green:
                    self.score += ((self.max_c / self.act_cycle) *
                                   self.passed_for_roads[ri])
            red_side, green_side, red_side_b, green_side_b = self.calc_helper2()
            if (green_side < red_side or green_side_b == 0) and red_side > 0:
                self.penalty *= 9 / 10
            else:
                self.score += self.max_c / self.act_cycle

    def apply_action(self, action):
        """
        applies a given action as well as measuring its affect on the
        snapshot of simulation
        """
        self.before_act()
        self.act_cycle += 1
        self.my_sim.run(action)
        if self.abrupt():
            return
        self.after_act()
        self.passed()
        self.reward_switch(action)
        self.reset()

    def reset(self):
        """
        reset dictionaries and list for the ext action cycle
        """
        self.v_location_before = dict()
        self.v_location_after = dict()
        self.passed_for_roads = dict()
        self.green = []
        self.red = []

    def is_empty(self):
        """
        checks if there are no vehicles in the inbound roads
        """
        for i in self.my_sim.inbound_roads:
            if len(self.my_sim.roads[i].vehicles) > 0:
                return False
        return True

    def done(self):
        """
        checks if the sim has completed
        """
        return self.my_sim.completed

    def abrupt(self):
        """
        checks if there was a collision
        """
        return self.my_sim.collision_detected
