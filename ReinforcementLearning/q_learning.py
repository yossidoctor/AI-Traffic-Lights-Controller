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


def train_agent(q_agent, env, path, n_episodes, render=False):
    for n_episode in range(1, n_episodes + 1):
        state = env.reset()
        score = 0
        done = False

        while not done:
            if render:
                env.render()
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


def validate_agent(q_agent, env, n_episodes, render=False):
    print("Evaluating agent.\n")
    total_scores, total_wait_time, total_collisions = 0, 0, 0
    for n_episode in range(n_episodes):
        state = env.reset()
        score = 0
        done = False

        while not done:
            if render:
                env.render()
            action = q_agent.get_action(state)
            next_state, reward, done, truncated = env.step(action)
            if truncated:
                return
            state = next_state
            score += reward
            total_collisions += env.window.sim.collision_detected

        total_scores += score
        total_wait_time += env.window.sim.get_average_wait_time()

    print(f"Results after {n_episodes} episodes:")
    print(f"Average score per episode: {total_scores / n_episodes:.2f}")
    print(f"Average wait time per episode: {total_wait_time / n_episodes:.2f}")
    print(f"Average collisions per episode: {total_collisions / n_episodes:.2f}")


if __name__ == '__main__':
    env: Environment = Environment()
    actions = len(env.action_space)
    q_agent = QLearningAgent(alpha=alpha, epsilon=epsilon, discount=discount, actions=actions)
    # n_train_episodes = 142800  # observation space size
    n_train_episodes = 10
    n_eval_episodes = 10
    file_name = f'ep{n_train_episodes}_alpha{alpha}_epsilon{epsilon}_discount{discount}.txt'
    train_agent(q_agent, env, file_name, n_episodes=n_train_episodes, render=False)
    q_agent.q_values = eval(get_q_values(file_name))
    validate_agent(q_agent, env, n_episodes=n_eval_episodes, render=True)
