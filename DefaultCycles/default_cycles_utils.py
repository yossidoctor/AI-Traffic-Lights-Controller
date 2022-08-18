t = 15


def fixed_cycle_action(simulation, dummy=None) -> bool:
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
        west_east_signal_state, n_west_east_vehicles, n_south_north_vehicles, non_empty_junction = state
        if west_east_signal_state and n_west_east_vehicles < n_south_north_vehicles:
            switch = True
        elif not west_east_signal_state and n_west_east_vehicles > n_south_north_vehicles:
            switch = True
    if switch:
        simulation.traffic_signals[0].prev_update_time = simulation.t
    return switch
