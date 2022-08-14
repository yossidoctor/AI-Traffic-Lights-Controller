from ReinforcementLearning import Environment


def longest_queue_action(sim, state):
    time_elapsed = sim.t - sim.traffic_signals[0].last_update_t >= 5
    switch = False
    if time_elapsed:
        sim.traffic_signals[0].last_update_t = sim.t
        west_east_signal_state, west_east_n_vehicles, south_north_n_vehicles, non_empty_junction = state
        if west_east_signal_state and west_east_n_vehicles < south_north_n_vehicles:
            switch = True
        elif not west_east_signal_state and west_east_n_vehicles > south_north_n_vehicles:
            switch = True
    return switch


def longest_queue_simulation(n_episodes):
    env = Environment()
    total_scores, total_wait_time, total_collisions = 0, 0, 0

    for episode in range(1, n_episodes + 1):
        state = env.reset()
        score = 0
        collision_detected = 0
        done = False

        while not done:
            # env.render()
            action = longest_queue_action(env.window.sim, state)
            n_state, reward, done, truncated = env.step(action)
            if truncated:
                return
            score += reward
            collision_detected = env.window.sim.collision_detected
            state = n_state

        wait_time = env.window.sim.get_average_wait_time()
        print(f"Episode {episode} - Score: {score} - Wait time: "
              f"{wait_time:.2f} -- Collisions: {int(collision_detected)}")

        total_scores += score
        total_wait_time += env.window.sim.get_average_wait_time()
        total_collisions += collision_detected

    print(f"\nResults after {n_episodes} episodes: -- ")
    print(f"Average score per episode: {total_scores / n_episodes:.2f}")
    print(f"Average wait time per episode: {total_wait_time / n_episodes:.2f}")
    print(f"Average collisions per episode: {total_collisions / n_episodes:.2f}")


if __name__ == '__main__':
    longest_queue_simulation(n_episodes=500)

# 200 eps, t = 5
# Average wait time per episode: 3.37
# Average collisions per episode: 0.05

# 200 eps, t = 10
# Average wait time per episode: 3.34
# Average collisions per episode: 0.02

# 200 eps, t = 15
# Average wait time per episode: 3.19
# Average collisions per episode: 0.07

# 200 eps, t = 15
# Average wait time per episode: 3.54
# Average collisions per episode: 0.01

