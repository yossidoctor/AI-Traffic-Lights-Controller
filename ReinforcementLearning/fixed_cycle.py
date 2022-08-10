from ReinforcementLearning import Environment


def fixed_cycle_action(sim):
    time_elapsed = sim.t - sim.traffic_signals[0].last_update_t >= 20
    if time_elapsed:
        sim.traffic_signals[0].last_update_t = sim.t
    return time_elapsed
    # t, traffic_signals = simulation.t, simulation.traffic_signals
    # actions = []
    # for traffic_signal in traffic_signals:
    #     time_elapsed = t - traffic_signal.last_update_t >= 5
    #     if time_elapsed:
    #         traffic_signal.last_update_t = t
    #     actions.append(time_elapsed)
    # return actions


def fixed_cycle_simulation(n_episodes):
    env = Environment()
    total_scores, total_wait_time, total_collisions = 0, 0, 0

    for episode in range(1, n_episodes + 1):
        state = env.reset()
        score = 0
        done = False

        while not done:
            # env.render()
            action = fixed_cycle_action(env.window.sim)
            n_state, reward, done, truncated = env.step(action)
            if env.window.sim.collision_detected:
                total_collisions += 1

            if truncated:
                exit()
            score += reward

        print(f'Episode {episode} - Score:{score}')

        total_scores += score
        total_wait_time += env.window.sim.get_average_wait_time()  # todo: why average wait time?

    print(f"Results after {n_episodes} episodes:")
    print(f"Average score per episode: {total_scores / n_episodes:.2f}")
    print(f"Average wait time per episode: {total_wait_time / n_episodes:.2f}")
    print(f"Average collisions per episode: {total_collisions / n_episodes:.2f}")


if __name__ == '__main__':
    fixed_cycle_simulation(n_episodes=100)
