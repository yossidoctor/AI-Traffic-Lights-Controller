from argparse import ArgumentParser

from DefaultCycles import default_cycle
from ReinforcementLearning import q_learning
from Search import search

if __name__ == '__main__':
    parser = ArgumentParser(description="AI Traffic Lights Controller")
    methods = ['fc', 'lqf', 'qlearning', 'search']
    parser.add_argument("-m", "--method", choices=methods, required=True)
    parser.add_argument("-e", "--episodes", metavar='N', type=int, required=True,
                        help="Number of evaluation episodes to run")
    parser.add_argument("-r", "--render", action='store_true',
                        help="Displays the simulation window")
    args = parser.parse_args()
    if args.method in ['fc', 'lqf']:
        default_cycle(n_episodes=args.episodes, action_func_name=args.method, render=args.render)
    elif args.method == 'qlearning':
        q_learning(n_episodes=args.episodes, render=args.render)
    elif args.method == 'search':
        search(episodes=args.episodes, render=args.render)
