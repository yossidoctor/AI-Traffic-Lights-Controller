from DefaultCycles import longest_queue_action, fixed_cycle_action
from ReinforcementLearning import Environment

action_funcs = {'fixed_cycle_action': fixed_cycle_action,
                'longest_queue_action': longest_queue_action}


def default_cycle(n_episodes: int, action_func_name: str, render):
    print(f"\n -- Running FC for {n_episodes} episodes  -- ")
    environment: Environment = Environment()
    total_wait_time, total_collisions = 0, 0
    action_func = action_funcs[action_func_name]
    for episode in range(1, n_episodes + 1):
        state = environment.reset(render)
        score = 0
        collision_detected = 0
        done = False

        while not done:
            action = action_func(environment.sim, state)
            state, reward, done, truncated = environment.step(action)
            if truncated:
                exit()
            score += reward
            collision_detected += environment.sim.collision_detected

        if collision_detected:
            print(f"Episode {episode} - Collisions: {int(collision_detected)}")
            total_collisions += 1
        else:
            wait_time = environment.sim.average_wait_time
            total_wait_time += wait_time
            print(f"Episode {episode} - Wait time: {wait_time:.2f}")

    n_completed = n_episodes - total_collisions
    print(f"\n -- Results after {n_episodes} episodes: -- ")
    print(
        f"Average wait time per completed episode: {total_wait_time / n_completed:.2f}")
    print(f"Average collisions per episode: {total_collisions / n_episodes:.2f}")
