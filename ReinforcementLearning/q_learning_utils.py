# import time

# Hyper-parameters
from ReinforcementLearning import Environment, QLearningAgent

alpha = 0.1
discount = 0.6
epsilon = 0.1


def save_q_values(path, q_values):
    with open(path, 'w+') as f:
        f.write(str(q_values))


def get_q_values(path):
    q_values_dict = ""
    with open(path, 'r') as f:
        for i in f.readlines():
            q_values_dict = i  # string
    return q_values_dict


def train_agent(agent, environment, path, n_episodes: int, render: bool = False):
    print(f"\n -- Training Q-agent for {n_episodes} episodes  -- ")
    # start_time = time.time()
    # current_time = time.time()

    for n_episode in range(1, n_episodes + 1):
        state = environment.reset(render)
        score = 0
        done = False

        while not done:
            action = agent.get_action(state)
            new_state, reward, done, truncated = environment.step(action)
            if truncated:
                exit()
            agent.update(state, action, new_state, reward)
            state = new_state
            score += reward

        # # For debugging purposes
        # if not n_episode % 50:
        #     current = time.time() - current_time
        #     total = time.time() - start_time
        #     expected = (total / n_episode) * n_episodes
        #     print(
        #         f"Episode {n_episode}. Current: {current:.0f}s. "
        #         f"Total: {total:.0f}s. Expected: {expected:.0f}s")
        #     current_time = time.time()

    save_q_values(path, agent.q_values)
    print(" -- Training finished -- ")


def validate_agent(agent, environment, n_episodes: int, render: bool = False):
    print(f"\n -- Evaluating Q-agent for {n_episodes} episodes -- ")
    total_wait_time, total_collisions, n_completed = 0, 0, 0

    for episode in range(1, n_episodes + 1):
        state = environment.reset(render)
        score = 0
        collision_detected = 0
        done = False

        while not done:
            action = agent.get_action(state)
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


def q_learning(n_episodes: int, render: bool):
    env: Environment = Environment()
    actions = env.action_space
    q_agent = QLearningAgent(alpha, epsilon, discount, actions)
    file_name = "ReinforcementLearning/Traffic_q_values_10000.txt"
    # train_agent(q_agent, env, file_name, n_train_episodes, render=False)
    q_agent.q_values = eval(get_q_values(file_name))
    validate_agent(q_agent, env, n_episodes, render)
