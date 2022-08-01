from ReinforcementLearning import Environment


def fixed_cycle_action(sim):
    time_elapsed = sim.t - sim.traffic_signals[0].last_update_t >= 10
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


if __name__ == '__main__':
    # TODO: ADD DOCS
    env = Environment()
    n_episodes = 10
    n_completed_episodes = 0
    total_scores = 0
    total_civ_wait, total_ems_wait = 0, 0

    for episode in range(1, n_episodes + 1):
        state = env.reset()
        done = False
        score = 0
        truncated = False

        while not done:
            env.render()
            action = fixed_cycle_action(env.window.sim)
            n_state, reward, done, truncated = env.step(action)
            if truncated:
                break
            score += reward

        if truncated:
            break

        print(f'Episode:{episode} Score:{score} '
              f'CIV: {env.window.sim.average_wait_time:.2f} EMS: {env.window.sim.average_ems_wait_time:.2f}')

        total_scores += score
        total_civ_wait += env.window.sim.average_wait_time
        total_ems_wait += env.window.sim.average_ems_wait_time
        n_completed_episodes += 1

    print(f"Results after {n_completed_episodes} episodes:")
    print(f"Average score per episode: {total_scores / n_completed_episodes:.2f}")
    print(f"Average civ wait time per episode: {total_civ_wait / n_completed_episodes:.2f}")
    print(f"Average ems wait time per episode: {total_ems_wait / n_completed_episodes:.2f}")
