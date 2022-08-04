from ReinforcementLearning import Environment, QLearningAgent

# Hyper-parameters
alpha = 0.2
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


def train_agent(q_agent, env, path, n_episodes):
    for n_episode in range(1, n_episodes + 1):
        state = env.reset()
        score = 0
        done = False

        while not done:
            action = q_agent.get_action(state)
            new_state, reward, done, truncated = env.step(action)
            if truncated:
                return
            q_agent.update(state, action, new_state, reward)
            state = new_state
            score += reward

        print(f"Episode {n_episode} - Score: {score}")

    save_q_values(path, q_agent.q_values)
    print("Training finished.\n")


def validate_agent(q_agent, env, n_episodes):
    total_scores, total_wait_time = 0, 0
    for n_episode in range(n_episodes):
        state = env.reset()
        score = 0
        done = False

        while not done:
            # env.render()
            action = q_agent.get_action(state)
            next_state, reward, done, truncated = env.step(action)
            if truncated:
                return
            state = next_state
            score += reward

        total_scores += score
        total_wait_time += env.window.sim.get_average_wait_time()

    print(f"Results after {n_episodes} episodes:")
    print(f"Average score per episode: {total_scores / n_episodes}")
    print(f"Average wait time per episode: {total_wait_time / n_episodes}")


if __name__ == '__main__':
    env = Environment()
    actions = len(env.action_space)
    q_agent = QLearningAgent(alpha=alpha, epsilon=epsilon, discount=discount, actions=actions)
    n_episodes = 5000
    # train_agent(q_agent, env, f'Traffic_q_values_{n_episodes}.txt', n_episodes=n_episodes)
    q_agent.q_values = eval(get_q_values(f'Traffic_q_values_{n_episodes}.txt'))
    validate_agent(q_agent, env, n_episodes=10)
