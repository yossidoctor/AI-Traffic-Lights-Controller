from argparse import ArgumentParser

from default_cycle import default_cycle
from q_learning import q_learning

if __name__ == '__main__':
    # args:
    # fixed cycle, qlearning(run trained agent), search # MUST
    # window size: monitor, laptop, custom (height, width) # IF VISUALIZED
    # setup: two_way_intersection

    parser = ArgumentParser(description="AI Traffic Lights Controller")
    parser.add_argument("-t", "--type", help="Type of simulation to run",
                        choices=['fc', 'lqf', 'qlearning', 'search'], required=True)
    parser.add_argument("-r", "--render", help="Render the simulation", default=False,
                        type=bool)  # TODO: USE
    # todo: add monitor adjusted for standard 24" 1080p, laptop for 14" 1080p with scaling 150% scaling
    parser.add_argument("-d", "--display",
                        help="Display size configuration. Monitor is optimized for a standard 24' 1080p display.",
                        default='monitor',
                        choices=['monitor', 'laptop', 'custom'])

    # todo: add render option, with lower count of episodes
    args = parser.parse_args()
    if args.render:
        n_episodes = 5
        render = True
    else:
        n_episodes = 1000
        render = False
    if args.display == 'monitor':
        pass
    elif args.display == 'laptop':
        pass
    elif args.display == 'custom':
        pass
    if args.type == 'fc':
        action_func = 'fixed_cycle_action'
        default_cycle(n_episodes=n_episodes, action_func_name=action_func, render=render)
    elif args.type == 'lqf':
        action_func = 'longest_queue_action'
        default_cycle(n_episodes=n_episodes, action_func_name=action_func, render=render)
    elif args.type == 'qlearning':
        q_learning(n_episodes=500, render=False)
    elif args.type == 'search':
        pass
