t = 15


def fixed_cycle_action(simulation) -> bool:
    """ Returns a boolean indicating to take an action
    if the enough time elapsed since previous action """
    switch = False
    time_elapsed = simulation.t - simulation.traffic_signals[0].prev_update_time >= t
    if time_elapsed:
        simulation.traffic_signals[0].prev_update_time = simulation.t
        switch = True
    return switch


def longest_queue_action(simulation, state) -> bool:
    """ Returns a boolean indicating to take an action
    if the enough time elapsed since previous action """
    switch = False
    time_elapsed = simulation.t - simulation.traffic_signals[0].prev_update_time >= t
    if time_elapsed:
        simulation.traffic_signals[0].prev_update_time = simulation.t
        signal_state, n_route_1_vehicles, n_route_2_vehicles, non_empty_junction = state
        if signal_state and n_route_1_vehicles < n_route_2_vehicles:
            switch = True
        elif not signal_state and n_route_1_vehicles > n_route_2_vehicles:
            switch = True
    return switch
