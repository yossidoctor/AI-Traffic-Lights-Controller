from argparse import ArgumentParser

if __name__ == '__main__':
    # args:
    # fixed cycle, qlearning(run trained agent), search
    # window size: monitor, laptop, custom (height, width)
    # setup: two_way_intersection

    parser = ArgumentParser()
    parser.add_argument("-m", "--method", dest="filename",
                        help="write report to FILE", metavar="FILE")
    parser.add_argument("-q", "--quiet",
                        action="store_false", dest="verbose", default=True,
                        help="don't print status messages to stdout")

    args = parser.parse_args()
