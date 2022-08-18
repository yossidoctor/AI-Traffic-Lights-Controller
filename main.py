from argparse import ArgumentParser

from DefaultCycles import default_cycle
from ReinforcementLearning import q_learning

if __name__ == '__main__':
    parser = ArgumentParser(description="AI Traffic Lights Controller")
    parser.add_argument("--type",
                        help="Type of method to run",
                        choices=['fc', 'lqf', 'qlearning', 'search'],
                        required=True)
    parser.add_argument("--episodes", metavar='N',
                        help="Number of evaluation episodes to run",
                        type=int,
                        required=True)
    parser.add_argument("--render",
                        help="Displays the simulation window",
                        action='store_true')
    args = parser.parse_args()
    if args.type == 'fc':
        action_func = 'fixed_cycle_action'
        default_cycle(n_episodes=args.episodes, action_func_name=action_func, render=args.render)
    elif args.type == 'lqf':
        action_func = 'longest_queue_action'
        default_cycle(n_episodes=args.episodes, action_func_name=action_func, render=args.render)
    elif args.type == 'qlearning':
        q_learning(n_episodes=args.episodes, render=args.render)
    elif args.type == 'search':
        pass
