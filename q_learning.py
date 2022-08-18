from ReinforcementLearning import *


def q_learning(n_episodes: int, render: bool):
    env: Environment = Environment()
    actions = env.action_space
    q_agent = QLearningAgent(alpha, epsilon, discount, actions)
    n_train_episodes = 20000
    file_name = f'ReinforcementLearning\ep{n_train_episodes}_a{alpha}' \
                f'_e{epsilon}_d{discount}_m{env.max_gen}.txt'
    # Deletes existing training file
    # train_agent(q_agent, env, file_name, n_train_episodes, render=False)
    q_agent.q_values = eval(get_q_values(file_name))
    validate_agent(q_agent, env, n_episodes, render)
