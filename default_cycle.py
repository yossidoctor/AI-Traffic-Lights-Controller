from DefaultCycles import longest_queue_action, fixed_cycle_action
from ReinforcementLearning import Environment


def default_cycle(n_episodes: int, action_func: str, render):
    env: Environment = Environment()
    total_scores, total_wait_time, total_collisions = 0, 0, 0
    action_func = fixed_cycle_action if action_func == 'fixed_cycle_action' \
        else longest_queue_action
    for episode in range(1, n_episodes + 1):
        state = env.reset(render)
        score = 0
        collision_detected = 0
        done = False

        while not done:
            action = action_func(env.sim)
            n_state, reward, done, truncated = env.step(action)
            if truncated:
                exit()
            score += reward
            collision_detected = env.sim.collision_detected

        wait_time = env.sim.average_wait_time
        print(f"Episode {episode} - Score: {score} - Wait time: "
              f"{wait_time:.2f} -- Collisions: {int(collision_detected)}")

        total_scores += score
        total_wait_time += env.sim.average_wait_time
        total_collisions += collision_detected

    print(f"\nResults after {n_episodes} episodes: -- ")
    print(f"Average score per episode: {total_scores / n_episodes:.2f}")
    print(f"Average wait time per episode: {total_wait_time / n_episodes:.2f}")
    print(f"Average collisions per episode: {total_collisions / n_episodes:.2f}")
