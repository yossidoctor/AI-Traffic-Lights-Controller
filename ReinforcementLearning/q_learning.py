from ReinforcementLearning import Environment, QLearningAgent

# Hyper-parameters
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


def train_agent(q_agent, env, path, n_episodes=10000):
    is_training = True
    for episode in range(1, n_episodes + 1):
        score = 0
        state = env.reset(training=is_training)
        if is_training:
            env.window.sim.dt = 0.9
        done = False

        while not done:
            action = q_agent.get_action(state)
            n_state, reward, done, truncated = env.step(action, training=is_training)
            if truncated:
                return
            q_agent.update(state, action, n_state, reward)
            state = n_state
            score += reward

        print(f"Episode: {episode}: Score {score}")

    save_q_values(path, q_agent.q_values)
    env.window.sim.dt = 1 / 60  # reset to default
    print("Training finished.\n")


def validate_agent(q_agent, env, n_episodes=5):
    total_scores = 0
    total_civ_wait, total_ems_wait = 0, 0
    for _ in range(n_episodes):
        state = env.reset()
        score = 0
        done = False

        while not done:
            env.render()
            action = q_agent.get_action(state)
            next_state, reward, done, truncated = env.step(action)
            if truncated:
                return
            score += reward
            state = next_state

        total_scores += score
        total_civ_wait += env.window.sim.average_wait_time
        total_ems_wait += env.window.sim.average_ems_wait_time

    print(f"Results after {n_episodes} episodes:")
    print(f"Average score per episode: {total_scores / n_episodes}")
    print(f"Average civ wait time per episode: {total_civ_wait / n_episodes}")
    print(f"Average ems wait time per episode: {total_ems_wait / n_episodes}")


if __name__ == '__main__':
    env = Environment()
    actions = env.action_space.n
    q_agent = QLearningAgent(alpha=alpha, epsilon=epsilon, discount=discount, actions=actions)
    n_episodes = 200
    train_agent(q_agent, env, f'Traffic_q_values_{n_episodes}.txt', n_episodes=n_episodes)
    q_agent.q_values = eval(get_q_values(f'Traffic_q_values_{n_episodes}.txt'))
    validate_agent(q_agent, env, n_episodes=5)
