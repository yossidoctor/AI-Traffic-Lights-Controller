import copy
import time

import numpy as np

from Search.gentics import Genetics
from Search.alt_state import Gstate
from TrafficSimulator.Setups.two_way_intersection import two_way_intersection_setup

Chosen_Length = 5
ACTION_SPACE = [0, 1]
MAX_GEN = 50


def sim_run(render):
    """
    Runs one episode of simulation using the search method
    """
    g = Genetics(Chosen_Length, ACTION_SPACE)
    sim = two_way_intersection_setup(MAX_GEN)
    if render:
        sim.init_gui()
    while not (sim.gui_closed or sim.completed):
        # Creating a snapshot of the running simulation
        current_state = Gstate(sim, g.solution_length)
        action_list = g.pick(current_state)
        for action in action_list:
            if sim.completed:
                break
            if action == 0:
                sim.run(False)
            else:
                sim.run(True)
    if sim.collision_detected:
        return -1  # Indicates the simulation run failed
    return sim.current_average_wait_time


def search(episodes, render):
    """
    Runs episodes of simulations
    """
    sum_scores = 0
    count_collisions = 0
    score_list = []
    for i in range(episodes):
        number = sim_run(render)
        if number == -1:
            print(f"Episode {i + 1} ended due to collision")
            count_collisions += 1
        else:
            print(f"Episode {i + 1} ended with average waiting time "
                  f"of: {number}")
            sum_scores += number
            score_list.append(number)
    if episodes != 0 and count_collisions != episodes:
        print(f"Min: {min(score_list)}, Max: {max(score_list)}, "
              f"AVG: {sum_scores / (episodes - count_collisions)}, "
              f"Standard deviation: {np.std(score_list)}, collision "
              f"percentage: {100 * (count_collisions / episodes)}")
    else:
        print("Either zero episodes or all episodes ended due to collision")
