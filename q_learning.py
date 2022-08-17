from ReinforcementLearning import *

if __name__ == '__main__':
    env: Environment = Environment()
    actions = env.action_space
    q_agent = QLearningAgent(alpha, epsilon, discount, actions)
    n_train_episodes = 20000
    n_eval_episodes = 1000
    file_name = f'ep{n_train_episodes}_a{alpha}_e{epsilon}_d{discount}_m{env.max_gen}.txt'
    train_agent(q_agent, env, file_name, n_train_episodes, render=False)
    q_agent.q_values = eval(get_q_values(file_name))
    validate_agent(q_agent, env, n_eval_episodes, render=False)
