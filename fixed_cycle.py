from ReinforcementLearning import Environment
from TrafficSimulator import Simulation


# todo: move to utils, with LQF
def fixed_cycle_action(sim: Simulation) -> bool:
    """ Returns a boolean indicating to take an action
    if the enough time elapsed since previous action """
    time_elapsed: bool = sim.t - sim.traffic_signals[0].prev_update_time >= 20
    if time_elapsed:
        sim.traffic_signals[0].prev_update_time = sim.t
    return time_elapsed


def fixed_cycle_simulation(n_episodes: int):
    env: Environment = Environment()
    total_scores, total_wait_time, total_collisions = 0, 0, 0

    for episode in range(1, n_episodes + 1):
        state = env.reset()
        score = 0
        collision_detected = 0
        done = False

        while not done:
            action = fixed_cycle_action(env.sim)
            n_state, reward, done, truncated = env.step(action)
            if truncated:
                exit()
            score += reward
            collision_detected = env.sim.collision_detected

        wait_time = env.sim.get_average_wait_time()
        print(f"Episode {episode} - Score: {score} - Wait time: "
              f"{wait_time:.2f} -- Collisions: {int(collision_detected)}")

        total_scores += score
        total_wait_time += env.sim.get_average_wait_time()
        total_collisions += collision_detected

    print(f"\nResults after {n_episodes} episodes: -- ")
    print(f"Average score per episode: {total_scores / n_episodes:.2f}")
    print(f"Average wait time per episode: {total_wait_time / n_episodes:.2f}")
    print(f"Average collisions per episode: {total_collisions / n_episodes:.2f}")


if __name__ == '__main__':
    fixed_cycle_simulation(n_episodes=1000)

# 500 eps
# Average wait time per episode: 3.56
# Average collisions per episode: 0.02
